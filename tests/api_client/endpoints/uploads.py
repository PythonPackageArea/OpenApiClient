from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.uploads import *
from ..models.common import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.groups import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *

class Uploads:
    body_upload_file_uploads_send_file_post: BodyUploadFileUploadsSendFilePost = BodyUploadFileUploadsSendFilePost
    input_strings: InputStrings = InputStrings
    response: Response = Response
    uploads_counts: UploadsCounts = UploadsCounts
    uploads_paginated: UploadsPaginated = UploadsPaginated
    uploads_read: UploadsRead = UploadsRead
    
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
    ) -> UploadsPaginated:
    
        path = '/uploads'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def find_one(
        self,
        id_path: int
    ) -> UploadsRead:
    
        path = f'/uploads/{id_path}'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def upload_status(
        self,
        id_path: int
    ) -> Response:
    
        """
        Подробная метрика загрузки.
        
        Args:
            self (Any): Parameter description
            id_path (int): Parameter description
        
        Returns:
            Response: Response data
        """
    
        path = f'/uploads/{id_path}/status'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('get', path, params, data, files)
    
    async def upload_file(
        self,
        overwrite_existing_query: bool = models.NOTSET,
        overwrite_by_deletion_query: bool = models.NOTSET,
        return_existing_query: bool = models.NOTSET,
        group_ids_or_titles_query: List[Any] = models.NOTSET,
        search_tags_query: List[Any] = models.NOTSET,
        only_overwrite_query: bool = models.NOTSET,
        app_id_query: Optional[int] = models.NOTSET,
        app_hash_query: Optional[str] = models.NOTSET,
        app_version_query: Optional[str] = models.NOTSET,
        device_model_query: Optional[str] = models.NOTSET,
        system_version_query: Optional[str] = models.NOTSET,
        system_lang_code_query: Optional[str] = models.NOTSET,
        lang_code_query: Optional[str] = models.NOTSET,
        twofa_query: Optional[str] = models.NOTSET,
        file_file: str = models.NOTSET
    ) -> Response:
    
        path = '/uploads/send/file'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)
    
    async def upload_strings(
        self,
        overwrite_existing_query: bool = models.NOTSET,
        group_ids_query: List[Any] = models.NOTSET,
        search_tags_query: List[Any] = models.NOTSET,
        upload_id_query: Optional[str] = models.NOTSET,
        return_existing_query: bool = models.NOTSET,
        only_overwrite_query: bool = models.NOTSET,
        default_parameters_body: dict = models.NOTSET,
        sessions_body: List[dict] = models.NOTSET
    ) -> Response:
    
        path = '/uploads/send/strings'.rstrip()
        params = self._prepare_params(locals())
        data = self._prepare_body_data(locals())
        files = self._prepare_files(locals())
        return await self._handle_request('post', path, params, data, files)