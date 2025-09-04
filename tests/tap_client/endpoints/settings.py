from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.settings import *
from ..models.common import *
from ..models.accounts import *
from ..models.exports import *
from ..models.groups import *
from ..models.includes import *
from ..models.sessions import *
from ..models.uploads import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.file import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.update import *

class Settings:
    schemas_read: SchemasRead = SchemasRead
    schemas_update: SchemasUpdate = SchemasUpdate
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def get_value(
        self,
        key_path: Keys
    ) -> Optional[str]:
    
        path = f'/settings/{key_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def update_setting(
        self,
        key_path: Keys,
        value_body: str = models.NOTSET
    ) -> Read:
    
        path = f'/settings/{key_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)