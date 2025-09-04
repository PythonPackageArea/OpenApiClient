from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.authentication import *
from ..models.common import *
from ..models.accounts import *
from ..models.exports import *
from ..models.groups import *
from ..models.includes import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *
from ..models.accounts import *
from ..models.exports import *
from ..models.file import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.update import *

class Authentication:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def login(
        self,
        username_body: str = models.NOTSET,
        password_body: str = models.NOTSET
    ) -> Optional[LoginResponse]:
    
        path = '/auth/login'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=LoginResponse)
    
    async def signup(
        self,
        username_body: str = models.NOTSET,
        password_body: str = models.NOTSET,
        secret_body: str = models.NOTSET
    ) -> Optional[UserShort]:
    
        path = '/auth/signup'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=UserShort)
    
    async def test(
        self,
        data_query: str
    ) -> str:
    
        path = '/auth/test_req'.rstrip()
        return await handle_request(self.client, 'get', path, locals())