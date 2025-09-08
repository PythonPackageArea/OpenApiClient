class Templates:
    """Шаблоны для генерации файлов"""

    lib_exc = """class SendRequestError(Exception):
    def __init__(self, message, path, status_code, response_data=None) -> None:
        self.message = message
        self.path = path
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(f"[{status_code}] {path}: {message}")

class ValidationError(SendRequestError):
    pass

class AuthenticationError(SendRequestError):
    pass

class NotFoundError(SendRequestError):
    pass

class ServerError(SendRequestError):
    pass
"""

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
        # Пересоздаем сессию если она грязная или не существует
        if self._session is None or self._session.closed or self._session_dirty:
            # Закрываем старую сессию
            if self._session and not self._session.closed:
                await self._session.close()
                
            timeout = ClientTimeout(
                total=self._timeout,
                connect=10,
                sock_read=10,
                sock_connect=10
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
            data: Union[dict, str] = None,
            headers: Dict[str, str] = None
    ) -> Any:

        if not self._api_url:
            raise SendRequestError(
                'API URL is empty',
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
                        'method': method,
                        'url': full_url,
                        'params': params,
                    }

                    # Добавление кастомных headers
                    if headers:
                        request_kwargs['headers'] = headers

                    # Обработка файлов
                    if files:
                        form_data = aiohttp.FormData()
                        for field_name, file_data in files.items():
                            form_data.add_field(
                                field_name,
                                file_data,
                                filename=f'{field_name}.bin'
                            )
                        if data:
                            for key, value in data.items():
                                form_data.add_field(key, str(value))
                        request_kwargs['data'] = form_data
                    else:
                        # Обработка JSON или form data
                        if isinstance(data, dict):
                            # По умолчанию отправляем JSON для словарей
                            if content_type == "application/x-www-form-urlencoded":
                                request_kwargs['data'] = data
                            else:
                                request_kwargs['json'] = data
                        elif isinstance(data, str):
                            request_kwargs['data'] = data

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
                        raise SendRequestError(
                            str(exc), path=path, status_code=400
                        )

                    if not _retries:
                        if isinstance(exc, (ClientError, asyncio.TimeoutError)):
                            raise SendRequestError(
                                str(exc), path=path, status_code=503
                            )

                    await asyncio.sleep(0.5)  # Небольшая пауза перед повтором

                except Exception as exc:
                    logger.error(f"Unexpected error: {exc}")
                    raise SendRequestError(
                        str(exc), path=path, status_code=500
                    )

    def initialize(
            self,
            api_url: str,
            headers: Dict[str, str] = None,
            cookies: Dict[str, str] = None,
            timeout: int = 30,
            retries: int = 3,
            max_connections: int = 100,
            max_connections_per_host: int = 10
    ) -> "AiohttpClient":
        \"\"\"Инициализация клиента с настройками\"\"\"
        self._api_url = str(api_url).rstrip('/')
        
        # Используем property для автоматического обновления сессии
        if headers:
            self.headers = headers
        if cookies:
            self.cookies = cookies
            
        self._timeout = int(timeout) if timeout else 30
        self._retries = int(retries) if retries else 3

        # Обновляем настройки пула соединений
        self._connection_pool = ConnectionPool(max_connections, max_connections_per_host)

        return self

    async def close(self):
        \"\"\"Закрытие клиента и освобождение ресурсов\"\"\"
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
        return self.update_headers(Authorization=f\"Bearer {token}\")

    def remove_auth(self):
        \"\"\"Удаление авторизации\"\"\"
        if \"Authorization\" in self._base_headers:
            del self._base_headers[\"Authorization\"]
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
from .utils import handle_request

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])


def http_method(
    method: str, path: str, response_model=None
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
            
            # Подставляем path параметры  
            formatted_path = path
            for key, value in locals_dict.items():
                if key.endswith('_path') and value is not None:
                    param_name = key[:-5]  # убираем _path суффикс
                    
                    # Ищем все возможные варианты плейсхолдеров
                    target_placeholder = '{' + param_name + '}'
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
                response_model=response_model
            )
        
        # Сохраняем метаданные для отладки
        wrapper._http_method = method
        wrapper._http_path = path
        wrapper._response_model = response_model
        wrapper._original_func = func
        
        return wrapper
    return decorator


def get(
    path: str, response_model=None
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("get", path, response_model)


def post(
    path: str, response_model=None
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("post", path, response_model)


def put(
    path: str, response_model=None
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("put", path, response_model)


def delete(
    path: str, response_model=None
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("delete", path, response_model)


def patch(
    path: str, response_model=None
) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return http_method("patch", path, response_model)
"""

    utils = """\"\"\"
Вспомогательные утилиты для endpoints
\"\"\"

from typing import Optional, Dict, Any
from . import constants


def is_not_set(value: Any) -> bool:
    return value is constants.NOTSET


def prepare_params(locals_dict: dict) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка query параметров\"\"\"
    params = {
        k[:-6]: v 
        for k, v in locals_dict.items() 
        if k.endswith('_query') and not is_not_set(v)
    }
    return params if params else None


def prepare_body_data(locals_dict: dict) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка body данных с автоматической конвертацией моделей\"\"\"
    body_data = {}
    for k, v in locals_dict.items():
        if k.endswith('_body') and not is_not_set(v):
            if hasattr(v, 'model_dump'):
                body_data[k[:-5]] = v.model_dump()
            elif isinstance(v, list) and v and hasattr(v[0], 'model_dump'):
                body_data[k[:-5]] = [item.model_dump() for item in v]
            else:
                body_data[k[:-5]] = v
    return body_data if body_data else None


def prepare_files(locals_dict: dict) -> Optional[Dict[str, Any]]:
    \"\"\"Подготовка file параметров\"\"\"
    files = {
        k[:-5]: v 
        for k, v in locals_dict.items() 
        if k.endswith('_file') and not is_not_set(v)
    }
    return files if files else None


async def handle_request(client, method: str, path: str, locals_dict: dict, response_model=None) -> Any:
    \"\"\"Обработка HTTP запроса с автоматической подготовкой параметров и парсингом response модели\"\"\"
    params = prepare_params(locals_dict)
    data = prepare_body_data(locals_dict)
    files = prepare_files(locals_dict)
    
    response = await client._send_request(
        method=method,
        path=path,
        params=params,
        data=data,
        files=files
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
    
    # Если указана модель для парсинга, пытаемся парсить (только для JSON)
    if response_model is not None and isinstance(response_data, (dict, list)):
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
