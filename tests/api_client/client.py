from .endpoints.accounts import Accounts
from .endpoints.sessions import Sessions
from .endpoints.uploads import Uploads
from .endpoints.exports import Exports
from .endpoints.common import Common
from .endpoints.settings import Settings
from .endpoints.authentication import Authentication
from .endpoints.module_tasks import Module_tasks
from .endpoints.groups import Groups

from simple_singleton import Singleton
from typing import TYPE_CHECKING

from .lib import exc as exceptions
from .lib import models  
from .common import AiohttpClient

if TYPE_CHECKING:
    from .endpoints.accounts import Accounts
    from .endpoints.sessions import Sessions
    from .endpoints.uploads import Uploads
    from .endpoints.exports import Exports
    from .endpoints.common import Common
    from .endpoints.settings import Settings
    from .endpoints.authentication import Authentication
    from .endpoints.module_tasks import Module_tasks
    from .endpoints.groups import Groups

class ApiClient(AiohttpClient, metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.accounts: "Accounts" = Accounts(self)
        self.sessions: "Sessions" = Sessions(self)
        self.uploads: "Uploads" = Uploads(self)
        self.exports: "Exports" = Exports(self)
        self.common: "Common" = Common(self)
        self.settings: "Settings" = Settings(self)
        self.authentication: "Authentication" = Authentication(self)
        self.module_tasks: "Module_tasks" = Module_tasks(self)
        self.groups: "Groups" = Groups(self)
        self._api_url: str = 'http://127.0.0.1:8000'
        self._timeout: int = 30
        self._max_retries: int = 3
        self._retry_delay: float = 1.0
