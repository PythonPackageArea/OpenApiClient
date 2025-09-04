from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.exports import *
from ..models.common import *
from ..models.accounts import *
from ..models.groups import *
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

class Exports:
    schemas_create: SchemasCreate = SchemasCreate
    schemas_paginated: SchemasPaginated = SchemasPaginated
    schemas_read: SchemasRead = SchemasRead
    
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
        status_query: str = models.NOTSET
    ) -> Paginated:
    
        path = '/exports'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def create(
        self,
        need_quality_body: int = models.NOTSET,
        ids_body: Optional[List[int]] = models.NOTSET,
        logged_after_body: Optional[int] = models.NOTSET,
        logged_before_body: Optional[int] = models.NOTSET,
        is_alive_body: Optional[bool] = models.NOTSET,
        upload_id_body: Optional[str] = models.NOTSET,
        account_id_setted_body: Optional[bool] = models.NOTSET,
        have_premium_body: Optional[bool] = models.NOTSET,
        have_spamblock_body: Optional[bool] = models.NOTSET,
        have_floodwait_body: Optional[bool] = models.NOTSET,
        check_spamblock_body: Optional[bool] = models.NOTSET,
        created_at_max_ago_body: Optional[int] = models.NOTSET,
        include_group_ids_or_titles_body: Optional[List[str]] = models.NOTSET,
        exclude_group_ids_or_titles_body: Optional[List[str]] = models.NOTSET,
        datereg_ago_body: Optional[int] = models.NOTSET,
        datereg_after_body: Optional[int] = models.NOTSET,
        include_phone_rules_body: Optional[List[str]] = models.NOTSET,
        exclude_phone_rules_body: Optional[List[str]] = models.NOTSET,
        search_tags_body: Optional[List[str]] = models.NOTSET
    ) -> Read:
    
        path = '/exports'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def find_one(
        self,
        id_path: int
    ) -> Read:
    
        path = f'/exports/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def pack(
        self,
        id_path: str
    ) -> bool:
    
        path = f'/exports/pack/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals())
    
    async def get_file(
        self,
        id_path: str
    ) -> Any:
    
        path = f'/exports/get_file/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals())