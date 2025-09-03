from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.sessions import *
from ..models.common import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.groups import *
from ..models.module_tasks import *
from ..models.settings import *
from ..models.uploads import *

class Sessions:
    body_update_many_sessions_update_many_put: BodyUpdateManySessionsUpdateManyPut = BodyUpdateManySessionsUpdateManyPut
    input_string_session: InputStringSession = InputStringSession
    session_group: SessionGroup = SessionGroup
    session_parameters: SessionParameters = SessionParameters
    sessions_create: SessionsCreate = SessionsCreate
    sessions_paginated: SessionsPaginated = SessionsPaginated
    sessions_read: SessionsRead = SessionsRead
    sessions_update: SessionsUpdate = SessionsUpdate
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    def _prepare_params(
        self,
        locals_dict: dict
    ) -> None:
    
        return {k[:-6]: v for k, v in locals_dict.items() if k.endswith('_query') and not models.is_not_set(v)} or None
    
    def _prepare_body_data(
        self,
        locals_dict: dict
    ) -> None:
    
        body_data = {}
        for k, v in locals_dict.items():
            if k.endswith('_body') and not models.is_not_set(v):
                if hasattr(v, 'model_dump'):
                    body_data[k[:-5]] = v.model_dump()
                elif isinstance(v, list) and v and hasattr(v[0], 'model_dump'):
                    body_data[k[:-5]] = [item.model_dump() for item in v]
                else:
                    body_data[k[:-5]] = v
        return body_data if body_data else None
    
    def _prepare_files(
        self,
        locals_dict: dict
    ) -> None:
    
        return {k[:-5]: v for k, v in locals_dict.items() if k.endswith('_file') and not models.is_not_set(v)} or None
    
    async def _handle_request(
        self,
        method: str,
        path: str,
        params: Optional[dict],
        data: Optional[dict],
        files: Optional[dict]
    ) -> Any:
    
        response = await self.client._send_request(
            method=method,
            path=path, 
            params=params,
            data=data,
            files=files
        )
        
        if not hasattr(response, 'status_code'):
            return response
        
        data = await response.json()
        return data
    
    async def change_groups(
        self,
        where_upload_id_query: Optional[str] = models.NOTSET,
        where_sessions_ids_query: List[int] = models.NOTSET,
        where_account_ids_query: List[int] = models.NOTSET,
        add_groups_query: List[str] = models.NOTSET,
        remove_groups_query: List[str] = models.NOTSET
    ) -> bool:
    
        path = '/sessions/change_groups'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
    async def update_many(
        self,
        ids_body: List[int] = models.NOTSET,
        data_body: dict = models.NOTSET
    ) -> int:
    
        path = '/sessions/update_many'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
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
    ) -> SessionsPaginated:
    
        path = '/sessions'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
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
    ) -> SessionsRead:
    
        path = '/sessions'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
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
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def count_avalible_in_human_readable(self) -> str:
    
        path = '/sessions/count_avalible_in_human_readable'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def count_profit(
        self,
        id_path: str,
        start_date_query: datetime = models.NOTSET,
        end_date_query: datetime = models.NOTSET
    ) -> int:
    
        path = f'/sessions/count_profit/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
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
    ) -> Optional[SessionsRead]:
    
        path = '/sessions/take'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def find_one(
        self,
        id_path: str
    ) -> Union[SessionsRead, Literal['NOT_FOUND']]:
    
        path = f'/sessions/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
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
        logged_at_body: Optional[str] = models.NOTSET,
        last_heartbeat_at_body: Optional[str] = models.NOTSET
    ) -> SessionsRead:
    
        path = f'/sessions/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
    async def heartbeat_session(
        self,
        id_path: str
    ) -> Optional[SessionsRead]:
    
        path = f'/sessions/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
    async def delete(
        self,
        id_path: str
    ) -> SessionsRead:
    
        path = f'/sessions/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('delete', path, params, data, files)