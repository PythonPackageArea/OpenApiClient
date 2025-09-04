from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.broadcasts import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Broadcasts:
    get_broadcast_response: GetBroadcastResponse = GetBroadcastResponse
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def create_broadcast(
        self,
        bot_id_body: int = models.NOTSET,
        message_id_body: int = models.NOTSET,
        from_chat_id_body: int = models.NOTSET,
        reply_markup_body: Optional[str] = models.NOTSET
    ) -> Read:
    
        path = '/broadcasts'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def find_many_broadcasts(
        self,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        order_by_query: Optional[str] = models.NOTSET,
        order_direction_query: Literal['desc', 'asc'] = models.NOTSET,
        bot_id_query: Optional[int] = models.NOTSET,
        status_query: Optional[BroadcastStatus] = models.NOTSET
    ) -> Paginated:
    
        path = '/broadcasts/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def get_broadcast(
        self,
        broadcast_id_path: int
    ) -> Read:
    
        path = f'/broadcasts/{broadcast_id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update_broadcast(
        self,
        broadcast_id_path: int,
        reply_markup_body: Optional[str] = models.NOTSET,
        status_body: Optional[BroadcastStatus] = models.NOTSET,
        target_users_count_body: Optional[int] = models.NOTSET,
        sent_count_body: Optional[int] = models.NOTSET,
        failed_count_body: Optional[int] = models.NOTSET,
        retry_count_body: Optional[int] = models.NOTSET,
        worker_id_body: Optional[str] = models.NOTSET,
        last_heartbeat_at_body: Optional[datetime] = models.NOTSET,
        started_at_body: Optional[datetime] = models.NOTSET,
        completed_at_body: Optional[datetime] = models.NOTSET,
        error_message_body: Optional[str] = models.NOTSET
    ) -> Read:
    
        path = f'/broadcasts/{broadcast_id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def get_broadcast_detailed(
        self,
        broadcast_id_path: int
    ) -> GetBroadcastResponse:
    
        path = f'/broadcasts/{broadcast_id_path}/detailed'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=GetBroadcastResponse)
    
    async def get_broadcast_statistics(
        self,
        broadcast_id_path: int
    ) -> BroadcastStatsSchema:
    
        path = f'/broadcasts/{broadcast_id_path}/stats'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=BroadcastStatsSchema)