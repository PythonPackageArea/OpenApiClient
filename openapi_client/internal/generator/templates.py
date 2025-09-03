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

    lib_models = """import enum
from typing import Any


class _NotSetType:
    def __repr__(self) -> str:
        return 'NOTSET'
    
    def __bool__(self) -> bool:
        return False


NOTSET = _NotSetType()


class MethodName(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


def is_not_set(value: Any) -> bool:
    return value is NOTSET
"""

    client = """from simple_singleton import Singleton
from typing import TYPE_CHECKING

from .lib import exc as exceptions
from .lib import models  
from .common import AiohttpClient

if TYPE_CHECKING:
{zone_imports}

class ApiClient(AiohttpClient, metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
{zone_assignments}
"""


templates = Templates()
