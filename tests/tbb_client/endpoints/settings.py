from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.settings import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Settings:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def find_many(self) -> List[dict]:
    
        path = '/settings/find_many'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def find_one(
        self,
        key_path: str
    ) -> SettingRead:
    
        path = f'/settings/{key_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=SettingRead)
    
    async def update(
        self,
        key_path: str,
        value_body: Union[str, dict] = models.NOTSET
    ) -> SettingRead:
    
        path = f'/settings/{key_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=SettingRead)
    
    async def create(
        self,
        key_query: str,
        value_body: Union[str, dict] = models.NOTSET
    ) -> SettingRead:
    
        path = '/settings'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=SettingRead)