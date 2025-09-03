aiohttp_common = """import asyncio
import json
import logging
from typing import Optional, Union, Dict, Any
from contextlib import asynccontextmanager

import aiohttp
from aiohttp import ClientError, ClientTimeout, ClientSession, TCPConnector
from pydantic import BaseModel

from .lib import exc as exceptions
from .lib import models

logger = logging.getLogger(__name__)


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
        self._headers: Dict[str, str] = {}
        self._cookies: Dict[str, str] = {}
        self._timeout: int = 30
        self._retries: int = 3
        self._connection_pool = ConnectionPool()
        self._rate_limiter = None

    @asynccontextmanager
    async def _session_context(self):
        \"\"\"Контекстный менеджер для сессии\"\"\"        
        session = await self._ensure_session()
        try:
            yield session
        finally:
            pass  # Сессия остается открытой для повторного использования

    async def _ensure_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(
                total=self._timeout,
                connect=10,
                sock_read=10,
                sock_connect=10
            )

            self._session = ClientSession(
                connector=self._connection_pool.get_connector(),
                timeout=timeout,
                headers=self._headers.copy(),
                cookies=self._cookies.copy(),
                trust_env=True,  # Использовать системные прокси
            )

        return self._session

    async def _send_request(
            self,
            method: models.MethodName,
            path: str,
            content_type: str = None,
            params: dict = None,
            files: dict = None,
            data: Union[dict, str] = None,
            headers: Dict[str, str] = None
    ) -> Any:

        if not self._api_url:
            raise exceptions.SendRequestError(
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
                        raise exceptions.SendRequestError(
                            str(exc), path=path, status_code=400
                        )

                    if not _retries:
                        if isinstance(exc, (ClientError, asyncio.TimeoutError)):
                            raise exceptions.SendRequestError(
                                str(exc), path=path, status_code=503
                            )

                    await asyncio.sleep(0.5)  # Небольшая пауза перед повтором

                except Exception as exc:
                    logger.error(f"Unexpected error: {exc}")
                    raise exceptions.SendRequestError(
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
        self._headers = dict(headers) if headers else {}
        self._cookies = dict(cookies) if cookies else {}
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()"""
