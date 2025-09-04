from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.accounts import *
from ..models.common import *
from ..models.exports import *
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

class Accounts:
    schemas_create: SchemasCreate = SchemasCreate
    schemas_paginated: SchemasPaginated = SchemasPaginated
    schemas_read: SchemasRead = SchemasRead
    schemas_update: SchemasUpdate = SchemasUpdate
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def find_many_accounts(
        self,
        phone_rules_query: List[Any] = models.NOTSET,
        group_ids_query: List[Any] = models.NOTSET,
        include_sessions_query: bool = models.NOTSET,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        some_session_id_query: Optional[str] = models.NOTSET,
        some_session_logged_ago_query: Optional[int] = models.NOTSET,
        some_session_upload_id_query: Optional[int] = models.NOTSET,
        some_session_export_id_query: Optional[int] = models.NOTSET,
        some_session_export_check_query: Optional[int] = models.NOTSET,
        some_session_is_alive_query: Optional[int] = models.NOTSET,
        action_id_query: Optional[str] = models.NOTSET,
        action_last_ago_query: Optional[int] = models.NOTSET,
        floodwait_status_query: Optional[bool] = models.NOTSET,
        premium_status_query: Optional[bool] = models.NOTSET,
        premium_expire_after_query: Optional[int] = models.NOTSET,
        spamblock_status_query: Optional[bool] = models.NOTSET,
        spamblock_expire_after_query: Optional[int] = models.NOTSET
    ) -> Paginated:
    
        path = '/accounts'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def upsert_account(
        self,
        id_body: Optional[int] = models.NOTSET,
        phone_body: Optional[str] = models.NOTSET,
        first_name_body: Optional[str] = models.NOTSET,
        last_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET
    ) -> Read:
    
        path = '/accounts'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def find_one_account(
        self,
        id_path: str
    ) -> Optional[Read]:
    
        path = f'/accounts/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update_account(
        self,
        id_path: str,
        phone_body: Optional[str] = models.NOTSET,
        first_name_body: Optional[str] = models.NOTSET,
        last_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET,
        flood_wait_until_body: Optional[datetime] = models.NOTSET,
        premium_until_body: Optional[datetime] = models.NOTSET,
        spamblock_until_body: Optional[datetime] = models.NOTSET
    ) -> Optional[Read]:
    
        path = f'/accounts/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def perform_action(
        self,
        account_id_query: int,
        group_id_query: str
    ) -> bool:
    
        path = '/accounts/action'.rstrip()
        return await handle_request(self.client, 'post', path, locals())