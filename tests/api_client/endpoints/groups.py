from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.groups import *
from ..models.common import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *

class Groups:
    groups_create: GroupsCreate = GroupsCreate
    groups_paginated: GroupsPaginated = GroupsPaginated
    groups_read: GroupsRead = GroupsRead
    groups_update: GroupsUpdate = GroupsUpdate
    
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
        limit_query: Optional[int] = models.NOTSET
    ) -> GroupsPaginated:
    
        path = '/groups'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def create(
        self,
        title_body: str = models.NOTSET
    ) -> GroupsRead:
    
        path = '/groups'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
    async def find_one(
        self,
        id_or_title_query: str
    ) -> GroupsRead:
    
        path = f'/groups/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def update(
        self,
        id_path: str,
        title_body: str = models.NOTSET
    ) -> GroupsRead:
    
        path = f'/groups/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('put', path, params, data, files)
    
    async def delete(
        self,
        id_path: str
    ) -> GroupsRead:
    
        path = f'/groups/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('delete', path, params, data, files)