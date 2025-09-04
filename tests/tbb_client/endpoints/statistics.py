from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.statistics import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Statistics:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def get_user_profile(
        self,
        id_path: int
    ) -> UserProfile:
    
        path = f'/statistics/user_profile/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UserProfile)
    
    async def get_user_referals(
        self,
        id_path: int
    ) -> UserReferals:
    
        path = f'/statistics/user_referals/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UserReferals)
    
    async def get_bot_profile(
        self,
        id_path: int
    ) -> BotProfile:
    
        path = f'/statistics/bot_profile/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=BotProfile)
    
    async def get_users_raiting(
        self,
        bot_id_query: int,
        limit_query: int = models.NOTSET
    ) -> List[dict]:
    
        path = '/statistics/users_raiting'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def get_top_bots(
        self,
        limit_query: int = models.NOTSET
    ) -> TopBotsResponse:
    
        path = '/statistics/top_bots'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=TopBotsResponse)
    
    async def get_prices(self) -> List[dict]:
    
        path = '/statistics/get_prices'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def get_price_menu(
        self,
        user_id_query: int
    ) -> PriceMenu:
    
        path = '/statistics/get_price_menu'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=PriceMenu)
    
    async def get_user_prices_by_countries(
        self,
        user_id_path: int,
        account_type_path: str = models.NOTSET
    ) -> UserPricesByCountries:
    
        path = f'/statistics/get_user_prices_by_countries/{user_id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UserPricesByCountries)
    
    async def get_user_prices_by_all_types(
        self,
        user_id_path: int
    ) -> UserPricesByAllTypes:
    
        path = f'/statistics/get_user_prices_by_all_types/{user_id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UserPricesByAllTypes)
    
    async def get_auto_reg_discount(self) -> Dict[str, float]:
    
        path = '/statistics/get_auto_reg_discount'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=dict)
    
    async def get_upload_stats_by_categories(
        self,
        bot_id_query: Optional[int] = models.NOTSET,
        days_limit_query: int = models.NOTSET
    ) -> UploadStatsResponse:
    
        path = '/statistics/get_upload_stats_by_categories'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UploadStatsResponse)
    
    async def get_single_upload_stats(
        self,
        upload_id_path: int
    ) -> UploadStatsResponse:
    
        path = f'/statistics/get_single_upload_stats/{upload_id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=UploadStatsResponse)