from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.accounts import *
from ..models.common import *
from ..models.authentication import *
from ..models.exports import *
from ..models.groups import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *

class Accounts:
    account: Account = Account
    account_last_action: AccountLastAction = AccountLastAction
    account_session: AccountSession = AccountSession
    last_action: LastAction = LastAction
    accounts_create: AccountsCreate = AccountsCreate
    accounts_paginated: AccountsPaginated = AccountsPaginated
    accounts_read: AccountsRead = AccountsRead
    accounts_update: AccountsUpdate = AccountsUpdate
    
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
    ) -> AccountsPaginated:
    
        path = '/accounts'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def upsert_account(
        self,
        id_body: Optional[int] = models.NOTSET,
        phone_body: Optional[str] = models.NOTSET,
        first_name_body: Optional[str] = models.NOTSET,
        last_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET
    ) -> AccountsRead:
    
        path = '/accounts'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
    async def find_one_account(
        self,
        id_path: str
    ) -> Optional[AccountsRead]:
    
        path = f'/accounts/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def update_account(
        self,
        id_path: str,
        phone_body: Optional[str] = models.NOTSET,
        first_name_body: Optional[str] = models.NOTSET,
        last_name_body: Optional[str] = models.NOTSET,
        username_body: Optional[str] = models.NOTSET,
        twofa_body: Optional[str] = models.NOTSET,
        flood_wait_until_body: Optional[str] = models.NOTSET,
        premium_until_body: Optional[str] = models.NOTSET,
        spamblock_until_body: Optional[str] = models.NOTSET
    ) -> Optional[AccountsRead]:
    
        path = f'/accounts/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
    async def perform_action(
        self,
        account_id_query: int,
        group_id_query: str
    ) -> bool:
    
        path = '/accounts/action'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)