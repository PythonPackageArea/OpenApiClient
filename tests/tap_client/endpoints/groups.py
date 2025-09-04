from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.groups import *
from ..models.common import *
from ..models.accounts import *
from ..models.exports import *
from ..models.includes import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.file import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.update import *

class Groups:
    schemas_create: SchemasCreate = SchemasCreate
    schemas_paginated: SchemasPaginated = SchemasPaginated
    schemas_read: SchemasRead = SchemasRead
    schemas_update: SchemasUpdate = SchemasUpdate
    
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
        limit_query: Optional[int] = models.NOTSET
    ) -> Paginated:
    
        path = '/groups'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def create(
        self,
        title_body: str = models.NOTSET
    ) -> Read:
    
        path = '/groups'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def find_one(
        self,
        id_or_title_path: str
    ) -> Read:
    
        path = f'/groups/{id_or_title_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update(
        self,
        id_path: str,
        title_body: str = models.NOTSET
    ) -> Read:
    
        path = f'/groups/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def delete(
        self,
        id_path: str
    ) -> Read:
    
        path = f'/groups/{id_path}'.rstrip()
        return await handle_request(self.client, 'delete', path, locals(), response_model=Read)