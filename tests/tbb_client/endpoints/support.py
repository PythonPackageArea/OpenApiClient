from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.support import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Support:
    
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
        user_id_query: Optional[int] = models.NOTSET
    ) -> Paginated:
    
        path = '/support/'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def update(
        self,
        id_path: int,
        mark_as_solved_body: Optional[bool] = models.NOTSET
    ) -> Read:
    
        path = f'/support/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def create(
        self,
        out_body: bool = models.NOTSET,
        content_body: str = models.NOTSET,
        user_id_body: int = models.NOTSET,
        support_id_body: Optional[int] = models.NOTSET
    ) -> Read:
    
        path = '/support/send_message'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def get_support_dialogs(
        self,
        limit_query: int = models.NOTSET,
        offset_query: int = models.NOTSET
    ) -> Paginated:
    
        path = '/support/get_support_dialogs'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Paginated)