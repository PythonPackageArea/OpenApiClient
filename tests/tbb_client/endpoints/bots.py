from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.bots import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Bots:
    
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
        min_balance_query: Optional[int] = models.NOTSET,
        max_balance_query: Optional[int] = models.NOTSET,
        min_earned_query: Optional[int] = models.NOTSET,
        max_earned_query: Optional[int] = models.NOTSET,
        have_active_users_query: Optional[bool] = models.NOTSET,
        owner_telegram_id_query: Optional[int] = models.NOTSET,
        is_active_query: Optional[bool] = models.NOTSET
    ) -> Paginated:
    
        path = '/bots/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def find_unique(
        self,
        id_query: Optional[int] = models.NOTSET,
        api_token_query: Optional[str] = models.NOTSET,
        token_query: Optional[str] = models.NOTSET
    ) -> Optional[Read]:
    
        path = '/bots/find_unique'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update(
        self,
        id_path: int,
        token_body: Optional[str] = models.NOTSET,
        owner_telegram_id_body: Optional[int] = models.NOTSET,
        rev_share_percent_body: Optional[int] = models.NOTSET,
        reset_api_token_body: Optional[bool] = models.NOTSET,
        menu_photo_id_body: Optional[str] = models.NOTSET,
        individual_boost_body: Optional[int] = models.NOTSET,
        increment_balance_body: Optional[float] = models.NOTSET,
        decrement_balance_body: Optional[float] = models.NOTSET,
        is_active_body: Optional[bool] = models.NOTSET
    ) -> Read:
    
        path = f'/bots/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def create(
        self,
        token_body: Optional[str] = models.NOTSET,
        owner_telegram_id_body: Optional[int] = models.NOTSET,
        rev_share_percent_body: Optional[int] = models.NOTSET
    ) -> Read:
    
        path = '/bots'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)