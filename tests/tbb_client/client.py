from .endpoints.common import Common
from .endpoints.schemas import Schemas
from .endpoints.statistics import Statistics
from .endpoints.withdrawals import Withdrawals
from .endpoints.broadcasts import Broadcasts
from .endpoints.authentication import Authentication
from .endpoints.users import Users
from .endpoints.bots import Bots
from .endpoints.uploads import Uploads
from .endpoints.settings import Settings
from .endpoints.support import Support

from simple_singleton import Singleton
from typing import TYPE_CHECKING

from .lib import exc as exceptions
from .lib import models  
from .common import AiohttpClient

if TYPE_CHECKING:
    from .endpoints.common import Common
    from .endpoints.schemas import Schemas
    from .endpoints.statistics import Statistics
    from .endpoints.withdrawals import Withdrawals
    from .endpoints.broadcasts import Broadcasts
    from .endpoints.authentication import Authentication
    from .endpoints.users import Users
    from .endpoints.bots import Bots
    from .endpoints.uploads import Uploads
    from .endpoints.settings import Settings
    from .endpoints.support import Support

class ApiClient(AiohttpClient, metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.common: "Common" = Common(self)
        self.schemas: "Schemas" = Schemas(self)
        self.statistics: "Statistics" = Statistics(self)
        self.withdrawals: "Withdrawals" = Withdrawals(self)
        self.broadcasts: "Broadcasts" = Broadcasts(self)
        self.authentication: "Authentication" = Authentication(self)
        self.users: "Users" = Users(self)
        self.bots: "Bots" = Bots(self)
        self.uploads: "Uploads" = Uploads(self)
        self.settings: "Settings" = Settings(self)
        self.support: "Support" = Support(self)
        self._api_url: str = 'https://api.tgdeal.net/admin_tg'
        self._timeout: int = 30
        self._max_retries: int = 3
        self._retry_delay: float = 1.0
