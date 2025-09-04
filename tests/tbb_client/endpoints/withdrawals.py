from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.withdrawals import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *

class Withdrawals:
    
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
        method_query: Optional[str] = models.NOTSET,
        status_query: Optional[WithdrawalStatus] = models.NOTSET,
        user_id_query: Optional[int] = models.NOTSET,
        requisite_query: Optional[str] = models.NOTSET
    ) -> Paginated:
    
        path = '/withdrawals/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def get_avalable_methods(self) -> Dict[str, dict]:
    
        path = '/withdrawals/avalable_methods/'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=dict)
    
    async def find_one(
        self,
        id_path: int
    ) -> Read:
    
        path = f'/withdrawals/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update(
        self,
        id_path: int,
        status_body: Optional[WithdrawalStatus] = models.NOTSET,
        requisite_body: Optional[str] = models.NOTSET,
        increment_value_body: Optional[float] = models.NOTSET,
        decrement_value_body: Optional[float] = models.NOTSET
    ) -> Read:
    
        path = f'/withdrawals/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def create(
        self,
        user_id_body: int = models.NOTSET,
        bot_id_body: Optional[int] = models.NOTSET,
        input_value_body: float = models.NOTSET,
        output_value_body: float = models.NOTSET,
        method_body: str = models.NOTSET,
        requisite_body: str = models.NOTSET
    ) -> Optional[Union[Read, bool]]:
    
        path = '/withdrawals'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)