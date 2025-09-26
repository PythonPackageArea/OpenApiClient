class Templates:
    """Шаблоны для генерации файлов"""

    models = """from typing import Any

class _NotSetType:
    def __repr__(self) -> str:
        return 'NOTSET'
    
    def __bool__(self) -> bool:
        return False


NOTSET = _NotSetType()
"""

    client = """from simple_singleton import Singleton
from typing import TYPE_CHECKING

from .common import AiohttpClient
from . import constants

if TYPE_CHECKING:
{zone_imports}

class ApiClient(AiohttpClient, metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
{zone_assignments}
"""

    aiohttp_common = """import asyncio
import json
import logging
from typing import Optional, Union, Dict, Any
from contextlib import asynccontextmanager

import aiohttp
from aiohttp import ClientError, ClientTimeout, ClientSession, TCPConnector
from pydantic import BaseModel

from . import constants

logger = logging.getLogger(__name__)


class SendRequestError(Exception):
    def __init__(self, message, path, status_code, response_data=None):
        self.message = message
        self.path = path
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(f"[{status_code}] {path}: {message}")


class ConnectionPool:
    \"\"\"Пул соединений для эффективного управления ресурсами\"\"\"

    def __init__(self, max_connections: int = 100, max_connections_per_host: int = 10):
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self._connector: Optional[TCPConnector] = None

    def get_connector(self) -> TCPConnector:
        if self._connector is None or self._connector.closed:
            self._connector = TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections_per_host,
                ttl_dns_cache=30,
                use_dns_cache=True,
                keepalive_timeout=60,
                enable_cleanup_closed=True,
            )
        return self._connector

    async def close(self):
        if self._connector and not self._connector.closed:
            await self._connector.close()


class AiohttpClient:
    \"\"\"Продвинутый HTTP клиент на базе aiohttp с connection pooling\"\"\"

    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._api_url: Optional[str] = None
        self._base_headers: Dict[str, str] = {}
        self._base_cookies: Dict[str, str] = {}
        self._temp_headers: Dict[str, str] = {}
        self._temp_cookies: Dict[str, str] = {}
        self._timeout: int = 30
        self._retries: int = 3
        self._connection_pool = ConnectionPool()
        self._rate_limiter = None
        self._session_dirty = False
        self._session_lock = asyncio.Lock()

    @property
    def headers(self) -> Dict[str, str]:
        \"\"\"Получение текущих заголовков\"\"\"
        return {**self._base_headers, **self._temp_headers}

    @headers.setter  
    def headers(self, value: Dict[str, str]):
        \"\"\"Установка заголовков с обновлением сессии\"\"\"
        self._base_headers = dict(value) if value else {}
        self._session_dirty = True

    @property
    def cookies(self) -> Dict[str, str]:
        \"\"\"Получение текущих куков\"\"\"
        return {**self._base_cookies, **self._temp_cookies}

    @cookies.setter
    def cookies(self, value: Dict[str, str]):
        \"\"\"Установка куков с обновлением сессии\"\"\"
        self._base_cookies = dict(value) if value else {}
        self._session_dirty = True

    def update_headers(self, **headers):
        \"\"\"Обновление заголовков\"\"\"
        self._base_headers.update(headers)
        self._session_dirty = True
        return self

    def update_cookies(self, **cookies):
        \"\"\"Обновление куков\"\"\"
        self._base_cookies.update(cookies)
        self._session_dirty = True
        return self

    @asynccontextmanager
    async def with_headers(self, **temp_headers):
        \"\"\"Контекстный менеджер для временных заголовков\"\"\"
        old_temp = self._temp_headers.copy()
        try:
            self._temp_headers.update(temp_headers)
            self._session_dirty = True
            yield self
        finally:
            self._temp_headers = old_temp
            self._session_dirty = True

    @asynccontextmanager
    async def with_cookies(self, **temp_cookies):
        \"\"\"Контекстный менеджер для временных куков\"\"\"
        old_temp = self._temp_cookies.copy()
        try:
            self._temp_cookies.update(temp_cookies)
            self._session_dirty = True
            yield self
        finally:
            self._temp_cookies = old_temp
            self._session_dirty = True

    async def refresh_session(self):
        \"\"\"Принудительное обновление сессии\"\"\"
        async with self._session_lock:
            if self._session and not self._session.closed:
                await self._session.close()
            self._session = None
            self._session_dirty = False

    @asynccontextmanager
    async def _session_context(self):
        \"\"\"Контекстный менеджер для сессии\"\"\"        
        session = await self._ensure_session()
        try:
            yield session
        finally:
            pass  # Сессия остается открытой для повторного использования

    async def _ensure_session(self) -> ClientSession:
        # Быстрая проверка без блокировки
        if (
            self._session is not None
            and not self._session.closed
            and not self._session_dirty
        ):
            return self._session

        # Медленная проверка с блокировкой
        async with self._session_lock:
            # Двойная проверка внутри блокировки
            if (
                self._session is not None
                and not self._session.closed
                and not self._session_dirty
            ):
                return self._session

            # Закрываем старую сессию
            if self._session and not self._session.closed:
                await self._session.close()
                
            timeout = ClientTimeout(
                total=self._timeout, connect=10, sock_read=10, sock_connect=10
            )

            # Объединяем базовые и временные headers/cookies
            current_headers = self.headers
            current_cookies = self.cookies

            self._session = ClientSession(
                connector=self._connection_pool.get_connector(),
                timeout=timeout,
                headers=current_headers,
                cookies=current_cookies,
                trust_env=True,  # Использовать системные прокси
            )
            self._session_dirty = False

        return self._session

    async def _send_request(
        self,
        method: str,
        path: str,
        content_type: str = None,
        params: dict = None,
        files: dict = None,
        data: Union[dict, list, str] = None,
        headers: Dict[str, str] = None,
    ) -> Any:

        if not self._api_url:
            raise SendRequestError(
                "API URL is empty",
                path=path,
                status_code=400,
            )

        full_url = f"{self._api_url.rstrip('/')}{path}"
        _retries = self._retries

        async with self._session_context() as session:
            while _retries:
                try:
                    logger.debug(f"Making {method} request to {full_url}")

                    # Подготовка данных для отправки
                    request_kwargs = {
                        "method": method,
                        "url": full_url,
                        "params": params,
                    }

                    # Добавление кастомных headers
                    if headers:
                        request_kwargs["headers"] = headers

                    # Обработка файлов
                    if files:
                        form_data = aiohttp.FormData()
                        for field_name, file_data in files.items():
                            if isinstance(file_data, list):
                                # Список файлов - добавляем каждый отдельно
                                for i, single_file in enumerate(file_data):
                                    form_data.add_field(
                                        field_name,
                                        single_file,
                                        filename=f"{field_name}_{i}.bin",
                                    )
                            else:
                                # Один файл
                                form_data.add_field(
                                    field_name, file_data, filename=f"{field_name}.bin"
                                )
                        if data:
                            for key, value in data.items():
                                if isinstance(value, list):
                                    # Для списков добавляем каждый элемент отдельно
                                    for item in value:
                                        form_data.add_field(key, str(item))
                                else:
                                    form_data.add_field(key, str(value))
                        request_kwargs["data"] = form_data
                    else:
                        # Обработка JSON или form data
                        if isinstance(data, (dict, list)):
                            # По умолчанию отправляем JSON для словарей и списков
                            if content_type == "application/x-www-form-urlencoded":
                                request_kwargs["data"] = data
                            else:
                                request_kwargs["json"] = data
                        elif isinstance(data, str):
                            request_kwargs["data"] = data
                        elif isinstance(data, (int, float, bool)) or data is None:
                            # Примитивные типы и None отправляем как JSON
                            request_kwargs["json"] = data

                    async with session.request(**request_kwargs) as response:
                        logger.debug(f"Response status: {response.status}")

                        # Создаем response объект для совместимости
                        class AiohttpResponse:
                            def __init__(self, aiohttp_response):
                                self.status_code = aiohttp_response.status
                                self._response = aiohttp_response
                                self._content = None
                                self._text = None
                                self._json = None
                                self.headers = aiohttp_response.headers

                            async def read(self):
                                if self._content is None:
                                    self._content = await self._response.read()
                                return self._content

                            async def text(self):
                                if self._text is None:
                                    self._text = await self._response.text()
                                return self._text

                            async def json(self):
                                if self._json is None:
                                    content = await self.text()
                                    self._json = json.loads(content)
                                return self._json

                            async def content(self):
                                return await self.read()

                        wrapped_response = AiohttpResponse(response)
                        await wrapped_response.read()  # Читаем контент заранее
                        return wrapped_response

                except (ClientError, asyncio.TimeoutError) as exc:
                    _retries -= 1
                    logger.warning(f"Request failed (retries left: {_retries}): {exc}")

                    if isinstance(exc, ValueError):
                        raise SendRequestError(str(exc), path=path, status_code=400)

                    if not _retries:
                        if isinstance(exc, (ClientError, asyncio.TimeoutError)):
                            raise SendRequestError(str(exc), path=path, status_code=503)

                    await asyncio.sleep(0.5)  # Небольшая пауза перед повтором

                except Exception as exc:
                    logger.error(f"Unexpected error: {exc}")

                    # Специальная обработка для закрытой сессии
                    if "Session is closed" in str(exc) or "RuntimeError" in str(
                        type(exc).__name__
                    ):
                        _retries -= 1
                        if _retries > 0:
                            logger.warning(
                                f"Session closed, recreating (retries left: {_retries})"
                            )
                            # Принудительно обновляем сессию
                            await self.refresh_session()
                            await asyncio.sleep(
                                1.0
                            )  # Больше времени для восстановления
                            continue

                    raise SendRequestError(str(exc), path=path, status_code=500)

    def initialize(
        self,
        api_url: str,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        retries: int = 3,
        max_connections: int = 100,
        max_connections_per_host: int = 10,
    ) -> "AiohttpClient":
        \"\"\"Инициализация клиента с настройками\"\"\"
        self._api_url = str(api_url).rstrip("/")
        
        # Используем property для автоматического обновления сессии
        if headers:
            self.headers = headers
        if cookies:
            self.cookies = cookies
            
        self._timeout = int(timeout) if timeout else 30
        self._retries = int(retries) if retries else 3

        # Обновляем настройки пула соединений
        self._connection_pool = ConnectionPool(
            max_connections, max_connections_per_host
        )

        return self

    async def close(self):
        \"\"\"Закрытие клиента и освобождение ресурсов\"\"\"
        async with self._session_lock:
            if self._session and not self._session.closed:
                await self._session.close()

        await self._connection_pool.close()

    async def health_check(self) -> bool:
        \"\"\"Проверка здоровья API\"\"\"
        try:
            async with self._session_context() as session:
                async with session.get(f"{self._api_url}/health") as response:
                    return response.status == 200
        except Exception:
            return False

    def set_rate_limiter(self, rate_limiter):
        \"\"\"Установка ограничителя частоты запросов\"\"\"
        self._rate_limiter = rate_limiter

    def set_auth_token(self, token: str):
        \"\"\"Установка Bearer токена авторизации\"\"\"
        return self.update_headers(Authorization=f"Bearer {token}")

    def remove_auth(self):
        \"\"\"Удаление авторизации\"\"\"
        if "Authorization" in self._base_headers:
            del self._base_headers["Authorization"]
            self._session_dirty = True
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()"""

    decorators = """\"\"\"
HTTP декораторы для endpoints (FastAPI-style)
\"\"\"

import inspect
from functools import wraps
from typing import Optional, Any, Callable, TypeVar
from .utils import handle_request, filter_params_by_suffix

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])


def http_method(
    method: str, path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    \"\"\"Базовый декоратор для HTTP методов с полной обработкой\"\"\"

    def decorator(func: DecoratedCallable) -> DecoratedCallable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Получаем сигнатуру функции для восстановления locals()
            sig = inspect.signature(func)
            bound_args = sig.bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            
            locals_dict = dict(bound_args.arguments)
            
            # Подставляем path параметры используя утилиты
            
            formatted_path = path
            path_params = filter_params_by_suffix(locals_dict, '_path')
            
            for param_name, value, field_name in path_params:
                if value is not None:
                    # Ищем все возможные варианты плейсхолдеров
                    target_placeholder = '{' + field_name + '}'
                    if target_placeholder in formatted_path:
                        formatted_path = formatted_path.replace(target_placeholder, str(value))
                    else:
                        # Fallback - заменяем любой плейсхолдер в пути
                        import re
                        if '{' in formatted_path and '}' in formatted_path:
                            # Простая замена первого найденного {placeholder}
                            start = formatted_path.find('{')
                            end = formatted_path.find('}', start)
                            if start != -1 and end != -1:
                                before = formatted_path[:start]
                                after = formatted_path[end+1:]
                                formatted_path = before + str(value) + after
            
            return await handle_request(
                self.client, 
                method, 
                formatted_path.rstrip('/'), 
                locals_dict, 
                response_model=response_model,
                response_models=response_models,
                whole_body_fields=whole_body_fields,
                field_mapping=field_mapping,
                param_mapping=param_mapping,
                body_required=body_required
            )
        
        # Сохраняем метаданные для отладки
        wrapper._http_method = method
        wrapper._http_path = path
        wrapper._response_model = response_model
        wrapper._original_func = func
        
        return wrapper
    return decorator


def get(
    path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("get", path, response_model, response_models, whole_body_fields, field_mapping, param_mapping, body_required)


def post(
    path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("post", path, response_model, response_models, whole_body_fields, field_mapping, param_mapping, body_required)


def put(
    path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("put", path, response_model, response_models, whole_body_fields, field_mapping, param_mapping, body_required)


def delete(
    path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("delete", path, response_model, response_models, whole_body_fields, field_mapping, param_mapping, body_required)


def patch(
    path: str, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("patch", path, response_model, response_models, whole_body_fields, field_mapping, param_mapping, body_required)
"""

    utils = """\"\"\"
Вспомогательные утилиты для endpoints
\"\"\"

from typing import Optional, Dict, Any
from datetime import datetime, date
from . import constants


def is_not_set(value: Any) -> bool:
    return value is constants.NOTSET


def serialize_value(value: Any) -> Any:
    \"\"\"Рекурсивная сериализация значений для JSON\"\"\"
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, bool):
        # Boolean значения остаются boolean для body данных
        return value
    elif isinstance(value, bytes):
        # Кодируем bytes в base64 для JSON
        import base64
        return base64.b64encode(value).decode('utf-8')
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    elif hasattr(value, 'model_dump'):
        # Pydantic модель - используем model_dump с сериализацией
        return serialize_value(value.model_dump())
    else:
        return value


def serialize_query_value(value: Any) -> Any:
    \"\"\"Специальная сериализация для query параметров\"\"\"
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, bool):
        # Boolean значения для query параметров должны быть строками
        return str(value).lower()
    elif isinstance(value, bytes):
        # Кодируем bytes в base64 для JSON
        import base64
        return base64.b64encode(value).decode('utf-8')
    elif isinstance(value, dict):
        return {k: serialize_query_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [serialize_query_value(item) for item in value]
    elif hasattr(value, 'model_dump'):
        # Pydantic модель - используем model_dump с сериализацией
        return serialize_query_value(value.model_dump())
    else:
        return value


def extract_field_name_from_param(param_name: str, suffix: str) -> str:
    \"\"\"Извлекает имя поля из имени параметра, правильно обрабатывая rfind\"\"\"
    if suffix in param_name:
        suffix_pos = param_name.rfind(suffix)
        base_name = param_name[:suffix_pos]
        remainder = param_name[suffix_pos + len(suffix):]
        field_name = base_name + remainder if remainder else base_name
        return field_name
    else:
        return param_name


def filter_params_by_suffix(locals_dict: dict, suffix: str) -> list:
    \"\"\"Фильтрует параметры по суффиксу, исключая NOTSET значения\"\"\"
    result = []
    for param_name, value in locals_dict.items():
        if suffix in param_name and param_name != 'self' and not is_not_set(value):
            field_name = extract_field_name_from_param(param_name, suffix)
            result.append((param_name, value, field_name))
    return result


def prepare_params(locals_dict: dict, param_mapping: dict = None) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка query параметров\"\"\"
    
    params = {}
    query_params = filter_params_by_suffix(locals_dict, '_query')
    
    for param_name, value, field_name in query_params:
        # Используем оригинальное имя из param_mapping если доступно
        if param_mapping and param_name in param_mapping:
            original_name = param_mapping[param_name]["name"]
        else:
            original_name = field_name
        # Сериализуем query параметры (особенно важно для дат и boolean)
        params[original_name] = serialize_query_value(value)
    
    return params if params else None


def prepare_headers(locals_dict: dict, param_mapping: dict = None) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка header параметров\"\"\"
    
    headers = {}
    
    # Ищем параметры которые являются headers по param_mapping
    if param_mapping:
        for param_name, value in locals_dict.items():
            if param_name != 'self' and not is_not_set(value) and param_name in param_mapping:
                param_info = param_mapping[param_name]
                if param_info["type"] == "header":
                    headers[param_info["name"]] = str(value)
    
    return headers if headers else None


def prepare_cookies(locals_dict: dict, param_mapping: dict = None) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка cookie параметров\"\"\"
    
    cookies = {}
    
    # Ищем параметры которые являются cookies по param_mapping  
    if param_mapping:
        for param_name, value in locals_dict.items():
            if param_name != 'self' and not is_not_set(value) and param_name in param_mapping:
                param_info = param_mapping[param_name]
                if param_info["type"] == "cookie":
                    cookies[param_info["name"]] = str(value)
    
    return cookies if cookies else None


def prepare_body_data(locals_dict: dict, whole_body_fields=None, field_mapping=None, body_required=False) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка body данных с автоматической конвертацией моделей\"\"\"
    
    if whole_body_fields is None:
        whole_body_fields = []
    if field_mapping is None:
        field_mapping = {}
    
    body_data = {}
    additional_fields = {}
    whole_body_value = None
    other_body_fields = {}
    
    # Используем утилиту для фильтрации body параметров
    body_params = filter_params_by_suffix(locals_dict, '_body')
    
    for param_name, value, field_name in body_params:
            
        # Проверяем если это поле указано как whole_body_field
        if field_name in whole_body_fields:
            # Это поле передается как весь body целиком
            whole_body_value = serialize_value(value)
            break  # Если найдено whole_body поле, используем только его
        elif param_name.startswith('additional_fields_body'):
            # Специальная обработка дополнительных полей - распаковываем их
            if isinstance(value, dict):
                # Сериализуем дополнительные поля
                serialized_additional = serialize_value(value)
                additional_fields.update(serialized_additional)
        else:
            # Обычные поля - сериализуем все значения
            # Используем маппинг если есть, иначе оригинальное имя
            actual_field_name = field_mapping.get(field_name, field_name)
            other_body_fields[actual_field_name] = serialize_value(value)
    
    # Если есть whole_body поле, используем его как весь body
    if whole_body_value is not None:
        return whole_body_value
    
    # Если есть только одно body поле, проверяем нужно ли передать его как весь body
    if len(other_body_fields) == 1 and not additional_fields:
        single_field_name, single_field_value = next(iter(other_body_fields.items()))
        
        # Автоматически передаем как весь body только для очень простых случаев:
        # - Поле называется 'request_body' (создается для $ref на корневом уровне)
        # - Поле содержит простое значение (не dict с несколькими полями)
        if (single_field_name == 'request_body' or
            (single_field_name in ['new_data'] and not isinstance(single_field_value, dict))):
            return single_field_value
    
    # Иначе собираем body из отдельных полей
    body_data.update(other_body_fields)
    body_data.update(additional_fields)
    
    # Если body обязательный и нет данных, возвращаем пустой словарь
    if not body_data and body_required:
        return {}
    
    return body_data if body_data else None


def prepare_files(locals_dict: dict) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка file параметров (bytes и List[bytes])\"\"\"
    
    files = {}
    file_params = filter_params_by_suffix(locals_dict, '_file')
    
    for param_name, value, field_name in file_params:
        # bytes или список bytes считаются файлами
        if isinstance(value, bytes):
            files[field_name] = value
        elif isinstance(value, list) and value and isinstance(value[0], bytes):
            # Список bytes файлов
            files[field_name] = value
    
    return files if files else None


def prepare_form_data(locals_dict: dict) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка form данных (не файлы)\"\"\"
    
    form_data = {}
    file_params = filter_params_by_suffix(locals_dict, '_file')
    
    for param_name, value, field_name in file_params:
        # Исключаем bytes и List[bytes] - это файлы
        if not isinstance(value, bytes) and not (isinstance(value, list) and value and isinstance(value[0], bytes)):
            form_data[field_name] = serialize_value(value)
    
    return form_data if form_data else None


async def handle_request(client, method: str, path: str, locals_dict: dict, response_model=None, response_models=None, whole_body_fields=None, field_mapping=None, param_mapping=None, body_required=False) -> Any:
    \"\"\"Обработка HTTP запроса с автоматической подготовкой параметров и парсингом response модели\"\"\"
    params = prepare_params(locals_dict, param_mapping)
    data = prepare_body_data(locals_dict, whole_body_fields, field_mapping, body_required)
    files = prepare_files(locals_dict)
    form_data = prepare_form_data(locals_dict)
    headers = prepare_headers(locals_dict, param_mapping)
    cookies = prepare_cookies(locals_dict, param_mapping)
    
    # Добавляем cookies в headers как Cookie заголовок
    if cookies:
        cookie_header = "; ".join([f"{name}={value}" for name, value in cookies.items()])
        if headers:
            headers["Cookie"] = cookie_header
        else:
            headers = {"Cookie": cookie_header}
    
    # Объединяем form_data с data для multipart запросов
    if form_data:
        if data:
            # Если есть и body data и form data, объединяем
            if isinstance(data, dict):
                data.update(form_data)
            else:
                # Если data не dict, создаем новый dict
                data = form_data
        else:
            data = form_data
    
    response = await client._send_request(
        method=method,
        path=path,
        params=params,
        data=data,
        files=files,
        headers=headers
    )
    
    if not hasattr(response, 'status_code'):
        return response
    
    # Определяем content-type и читаем соответствующим способом
    content_type = response.headers.get('content-type', '').lower()
    
    try:
        if 'application/json' in content_type:
            response_data = await response.json()
        elif content_type.startswith('text/'):
            response_data = await response.text()
        elif 'application/xml' in content_type or 'text/xml' in content_type:
            response_data = await response.text()
        elif 'application/octet-stream' in content_type or 'application/zip' in content_type:
            response_data = await response.read()
        else:
            # Универсальная попытка JSON, fallback на text
            try:
                response_data = await response.json()
            except Exception:
                try:
                    response_data = await response.text()
                except Exception:
                    response_data = await response.read()
    
    except Exception:
        # Если все способы не сработали, возвращаем сырой response
        return response
    
    # Если указан список моделей (Union типы), пытаемся парсить каждую по очереди
    if response_models is not None and isinstance(response_data, (dict, list)):
        for model in response_models:
            try:
                if isinstance(response_data, list):
                    return [model(**item) for item in response_data]
                else:
                    return model(**response_data)
            except Exception:
                # Пробуем следующую модель
                continue
        # Если ни одна модель не подошла, возвращаем raw data
        pass
    
    # Если указана одна модель для парсинга, пытаемся парсить (только для JSON)
    elif response_model is not None and isinstance(response_data, (dict, list)):
        try:
            # Если response_data - это список, создаем список моделей
            if isinstance(response_data, list):
                return [response_model(**item) for item in response_data]
            # Иначе создаем одну модель
            else:
                return response_model(**response_data)
        except Exception:
            # Если парсинг не удался, возвращаем raw data
            pass
    
    return response_data
"""


templates = Templates()
