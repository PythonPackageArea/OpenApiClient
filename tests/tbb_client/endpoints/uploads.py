from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.uploads import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.users import *
from ..models.withdrawals import *

class Uploads:
    
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
        user_id_query: Optional[int] = models.NOTSET,
        upload_type_query: Literal['SELL', 'RENT', None] = models.NOTSET,
        from_bot_query: Optional[bool] = models.NOTSET,
        from_api_query: Optional[bool] = models.NOTSET
    ) -> Paginated:
    
        path = '/uploads/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def find_one(
        self,
        id_path: Optional[int]
    ) -> Optional[Read]:
    
        path = f'/uploads/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update_upload(
        self,
        id_path: Optional[int],
        done_body: Optional[bool] = models.NOTSET,
        cancelled_body: Optional[bool] = models.NOTSET,
        callback_message_id_body: Optional[int] = models.NOTSET,
        set_now_take_body: Optional[bool] = models.NOTSET,
        clear_file_unique_id_body: Optional[bool] = models.NOTSET
    ) -> Optional[Read]:
    
        path = f'/uploads/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def create_upload(
        self,
        file_id_body: Optional[str] = models.NOTSET,
        file_name_body: Optional[str] = models.NOTSET,
        file_size_mb_body: Optional[int] = models.NOTSET,
        file_unique_id_body: Optional[str] = models.NOTSET,
        file_message_id_body: Optional[int] = models.NOTSET,
        callback_message_id_body: Optional[int] = models.NOTSET,
        from_bot_body: Optional[bool] = models.NOTSET,
        from_api_body: Optional[bool] = models.NOTSET,
        upload_rent_reauth_body: Optional[bool] = models.NOTSET,
        upload_app_id_body: Optional[int] = models.NOTSET,
        upload_type_body: Type = models.NOTSET,
        user_id_body: int = models.NOTSET,
        default_parameters_body: Optional["Parameters"] = models.NOTSET,
        sessions_body: Optional[List["InputSession"]] = models.NOTSET
    ) -> Optional[Union[Read, Literal['File already exists']]]:
    
        path = '/uploads/'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def take_client_queue(self) -> Optional[ClientTakeUpload]:
    
        path = '/uploads/take_client_upload/'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=ClientTakeUpload)
    
    async def send_strings(
        self,
        id_body: Optional[int] = models.NOTSET,
        default_parameters_body: Optional["Parameters"] = models.NOTSET,
        sessions_body: List["InputSession"] = models.NOTSET
    ) -> Optional[Read]:
    
        path = '/uploads/send/strings'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)