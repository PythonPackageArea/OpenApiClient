from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.sessions import *
from ..models.common import *
from ..models.accounts import *
from ..models.exports import *
from ..models.groups import *
from ..models.includes import *
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

class Sessions:
    schemas_create: SchemasCreate = SchemasCreate
    schemas_paginated: SchemasPaginated = SchemasPaginated
    schemas_read: SchemasRead = SchemasRead
    schemas_update: SchemasUpdate = SchemasUpdate
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def change_groups(
        self,
        where_upload_id_query: Optional[str] = models.NOTSET,
        where_sessions_ids_query: List[int] = models.NOTSET,
        where_account_ids_query: List[int] = models.NOTSET,
        add_groups_query: List[str] = models.NOTSET,
        remove_groups_query: List[str] = models.NOTSET
    ) -> bool:
    
        path = '/sessions/change_groups'.rstrip()
        return await handle_request(self.client, 'put', path, locals())
    
    async def update_many(
        self,
        ids_body: List[int] = models.NOTSET,
        data_body: "Sessions.SchemasUpdate" = models.NOTSET
    ) -> int:
    
        path = '/sessions/update_many'.rstrip()
        return await handle_request(self.client, 'put', path, locals())
    
    async def find_many(
        self,
        ids_query: List[Any] = models.NOTSET,
        phone_rules_query: List[Any] = models.NOTSET,
        include_group_ids_or_titles_query: List[Any] = models.NOTSET,
        exclude_group_ids_or_titles_query: List[Any] = models.NOTSET,
        search_tags_query: List[Any] = models.NOTSET,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        is_alive_setted_query: Optional[bool] = models.NOTSET,
        export_id_setted_query: Optional[bool] = models.NOTSET,
        account_id_setted_query: Optional[bool] = models.NOTSET,
        username_setted_query: Optional[bool] = models.NOTSET,
        max_account_id_query: Optional[int] = models.NOTSET,
        is_alive_query: Optional[bool] = models.NOTSET,
        upload_id_query: Optional[int] = models.NOTSET,
        export_id_query: Optional[int] = models.NOTSET,
        export_check_query: Optional[bool] = models.NOTSET,
        app_id_query: Optional[int] = models.NOTSET,
        logged_after_query: Optional[int] = models.NOTSET,
        logged_before_query: Optional[int] = models.NOTSET,
        floodwait_status_query: Optional[bool] = models.NOTSET,
        premium_status_query: Optional[bool] = models.NOTSET,
        premium_expire_after_query: Optional[int] = models.NOTSET,
        spamblock_status_query: Optional[bool] = models.NOTSET,
        spamblock_expire_after_query: Optional[int] = models.NOTSET,
        created_at_max_ago_query: Optional[int] = models.NOTSET,
        datereg_ago_query: Optional[int] = models.NOTSET,
        datereg_after_query: Optional[int] = models.NOTSET
    ) -> Paginated:
    
        path = '/sessions'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def create(
        self,
        string_session_body: Optional[str] = models.NOTSET,
        upload_id_body: Optional[int] = models.NOTSET,
        search_tags_body: List[str] = models.NOTSET,
        app_id_body: Optional[int] = models.NOTSET,
        app_hash_body: Optional[str] = models.NOTSET,
        app_version_body: Optional[str] = models.NOTSET,
        device_model_body: Optional[str] = models.NOTSET,
        system_version_body: Optional[str] = models.NOTSET,
        system_lang_code_body: Optional[str] = models.NOTSET,
        lang_code_body: Optional[str] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET
    ) -> Read:
    
        path = '/sessions'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def find_many_by_ids(
        self,
        phone_rules_query: List[Any] = models.NOTSET,
        include_group_ids_or_titles_query: List[Any] = models.NOTSET,
        exclude_group_ids_or_titles_query: List[Any] = models.NOTSET,
        search_tags_query: List[Any] = models.NOTSET,
        log_query: bool = models.NOTSET,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        is_alive_setted_query: Optional[bool] = models.NOTSET,
        export_id_setted_query: Optional[bool] = models.NOTSET,
        account_id_setted_query: Optional[bool] = models.NOTSET,
        username_setted_query: Optional[bool] = models.NOTSET,
        max_account_id_query: Optional[int] = models.NOTSET,
        is_alive_query: Optional[bool] = models.NOTSET,
        upload_id_query: Optional[int] = models.NOTSET,
        export_id_query: Optional[int] = models.NOTSET,
        export_check_query: Optional[bool] = models.NOTSET,
        app_id_query: Optional[int] = models.NOTSET,
        logged_after_query: Optional[int] = models.NOTSET,
        logged_before_query: Optional[int] = models.NOTSET,
        floodwait_status_query: Optional[bool] = models.NOTSET,
        premium_status_query: Optional[bool] = models.NOTSET,
        premium_expire_after_query: Optional[int] = models.NOTSET,
        spamblock_status_query: Optional[bool] = models.NOTSET,
        spamblock_expire_after_query: Optional[int] = models.NOTSET,
        created_at_max_ago_query: Optional[int] = models.NOTSET,
        datereg_ago_query: Optional[int] = models.NOTSET,
        datereg_after_query: Optional[int] = models.NOTSET
    ) -> List[int]:
    
        path = '/sessions/find_ids'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def count_avalible_in_human_readable(self) -> str:
    
        path = '/sessions/count_avalible_in_human_readable'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def count_profit(
        self,
        id_path: str,
        start_date_path: datetime = models.NOTSET,
        end_date_path: datetime = models.NOTSET
    ) -> int:
    
        path = f'/sessions/count_profit/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals())
    
    async def take(
        self,
        phone_rules_query: List[Any] = models.NOTSET,
        group_ids_query: List[Any] = models.NOTSET,
        without_group_ids_query: List[Any] = models.NOTSET,
        is_alive_setted_query: Optional[bool] = models.NOTSET,
        export_id_setted_query: Optional[bool] = models.NOTSET,
        username_setted_query: Optional[bool] = models.NOTSET,
        export_check_query: Optional[bool] = models.NOTSET,
        logged_ago_query: Optional[int] = models.NOTSET,
        action_id_query: Optional[str] = models.NOTSET,
        action_ago_query: Optional[int] = models.NOTSET,
        floodwait_status_query: Optional[bool] = models.NOTSET,
        premium_status_query: Optional[bool] = models.NOTSET,
        premium_expire_after_query: Optional[int] = models.NOTSET,
        spamblock_status_query: Optional[bool] = models.NOTSET,
        spamblock_expire_after_query: Optional[int] = models.NOTSET,
        last_heartbeat_ago_query: Optional[int] = models.NOTSET
    ) -> Optional[Read]:
    
        path = '/sessions/take'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def find_one(
        self,
        id_path: str
    ) -> Union[Read, Literal['NOT_FOUND']]:
    
        path = f'/sessions/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
    async def update(
        self,
        id_path: str,
        account_id_body: Optional[int] = models.NOTSET,
        string_session_body: Optional[str] = models.NOTSET,
        upload_id_body: Optional[int] = models.NOTSET,
        export_clear_body: Optional[bool] = models.NOTSET,
        export_id_body: Optional[int] = models.NOTSET,
        export_check_body: Optional[bool] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET,
        is_alive_body: Optional[bool] = models.NOTSET,
        invalid_code_body: Optional[str] = models.NOTSET,
        app_id_body: Optional[int] = models.NOTSET,
        app_hash_body: Optional[str] = models.NOTSET,
        app_version_body: Optional[str] = models.NOTSET,
        device_model_body: Optional[str] = models.NOTSET,
        system_version_body: Optional[str] = models.NOTSET,
        system_lang_code_body: Optional[str] = models.NOTSET,
        lang_code_body: Optional[str] = models.NOTSET,
        logged_at_body: Optional[datetime] = models.NOTSET,
        last_heartbeat_at_body: Optional[datetime] = models.NOTSET
    ) -> Read:
    
        path = f'/sessions/{id_path}'.rstrip()
        return await handle_request(self.client, 'put', path, locals(), response_model=Read)
    
    async def heartbeat_session(
        self,
        id_path: str
    ) -> Optional[Read]:
    
        path = f'/sessions/{id_path}'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Read)
    
    async def delete(
        self,
        id_path: str
    ) -> Read:
    
        path = f'/sessions/{id_path}'.rstrip()
        return await handle_request(self.client, 'delete', path, locals(), response_model=Read)