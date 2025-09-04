from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.uploads import *
from ..models.common import *
from ..models.accounts import *
from ..models.exports import *
from ..models.groups import *
from ..models.includes import *
from ..models.sessions import *
from ..models.settings import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.file import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.update import *

class Uploads:
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
        limit_query: Optional[int] = models.NOTSET
    ) -> Paginated:
    
        path = '/uploads'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Paginated)
    
    async def find_one(
        self,
        id_path: int
    ) -> Read:
    
        path = f'/uploads/{id_path}'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=Read)
    
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
        return await handle_request(self.client, 'get', path, locals(), response_model=Response)
    
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
        file_file: bytes = models.NOTSET
    ) -> Response:
    
        path = '/uploads/send/file'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Response)
    
    async def upload_strings(
        self,
        overwrite_existing_query: bool = models.NOTSET,
        group_ids_query: List[Any] = models.NOTSET,
        search_tags_query: List[Any] = models.NOTSET,
        upload_id_query: Optional[str] = models.NOTSET,
        return_existing_query: bool = models.NOTSET,
        only_overwrite_query: bool = models.NOTSET,
        default_parameters_body: "SessionParameters" = models.NOTSET,
        sessions_body: List["InputStringSession"] = models.NOTSET
    ) -> Response:
    
        path = '/uploads/send/strings'.rstrip()
        return await handle_request(self.client, 'post', path, locals(), response_model=Response)