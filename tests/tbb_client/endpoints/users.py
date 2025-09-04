from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.users import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.withdrawals import *

class Users:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def find_many(
        self,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        order_by_query: Optional[str] = models.NOTSET,
        order_direction_query: Literal['desc', 'asc'] = models.NOTSET,
        bot_id_query: Optional[int] = models.NOTSET,
        min_balance_query: Optional[int] = models.NOTSET,
        max_balance_query: Optional[int] = models.NOTSET,
        min_earned_query: Optional[int] = models.NOTSET,
        max_earned_query: Optional[int] = models.NOTSET,
        min_sold_query: Optional[int] = models.NOTSET,
        max_sold_query: Optional[int] = models.NOTSET,
        referrer_id_query: Optional[int] = models.NOTSET,
        language_query: Optional[Literal['en', 'ru']] = models.NOTSET,
        have_withdrawals_query: Optional[bool] = models.NOTSET,
        have_uploads_query: Optional[bool] = models.NOTSET,
        have_referals_query: Optional[bool] = models.NOTSET
    ) -> Paginated:
    
        path = '/users/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def find_unique(
        self,
        id_query: Optional[int] = models.NOTSET,
        api_token_query: Optional[str] = models.NOTSET,
        telegram_id_query: Optional[int] = models.NOTSET,
        bot_id_query: Optional[int] = models.NOTSET
    ) -> Optional[Read]:
    
        path = '/users/find_unique'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update(
        self,
        id_path: int,
        full_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET,
        upload_app_id_body: Optional[int] = models.NOTSET,
        upload_type_body: Optional[str] = models.NOTSET,
        upload_rent_reauth_body: Optional[bool] = models.NOTSET,
        banned_body: Optional[bool] = models.NOTSET,
        is_admin_body: Optional[bool] = models.NOTSET,
        language_body: Optional[Literal['en', 'ru']] = models.NOTSET,
        referrer_id_body: Optional[int] = models.NOTSET,
        individual_boost_body: Optional[int] = models.NOTSET,
        bot_initialized_body: Optional[bool] = models.NOTSET,
        increment_balance_body: Optional[float] = models.NOTSET,
        decrement_balance_body: Optional[float] = models.NOTSET,
        reset_api_token_body: Optional[bool] = models.NOTSET
    ) -> Read:
    
        path = f'/users/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def create(
        self,
        telegram_id_body: int = models.NOTSET,
        bot_id_body: int = models.NOTSET,
        referrer_id_body: Optional[int] = models.NOTSET,
        language_body: Literal['en', 'ru'] = models.NOTSET,
        full_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET
    ) -> Read:
    
        path = '/users'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)