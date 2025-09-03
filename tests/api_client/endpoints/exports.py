from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.exports import *
from ..models.common import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.groups import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *

class Exports:
    exports_statuses: ExportsStatuses = ExportsStatuses
    exports_create: ExportsCreate = ExportsCreate
    exports_paginated: ExportsPaginated = ExportsPaginated
    exports_read: ExportsRead = ExportsRead
    exports_counts: ExportsCounts = ExportsCounts
    
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
    
    async def find_many(
        self,
        start_date_query: Optional[datetime] = models.NOTSET,
        end_date_query: Optional[datetime] = models.NOTSET,
        offset_query: Optional[int] = models.NOTSET,
        limit_query: Optional[int] = models.NOTSET,
        status_query: str = models.NOTSET
    ) -> ExportsPaginated:
    
        path = '/exports'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
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
    ) -> ExportsRead:
    
        path = '/exports'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
    async def find_one(
        self,
        id_path: int
    ) -> ExportsRead:
    
        path = f'/exports/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def pack(
        self,
        id_path: str
    ) -> bool:
    
        path = f'/exports/pack/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
    async def get_file(
        self,
        id_path: str
    ) -> Any:
    
        path = f'/exports/get_file/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)