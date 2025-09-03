from ..lib import models
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.common import *
from ..models.common import *
from ..models.accounts import *
from ..models.authentication import *
from ..models.exports import *
from ..models.groups import *
from ..models.module_tasks import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *

class Common:
    h_t_t_p_validation_error: HTTPValidationError = HTTPValidationError
    validation_error: ValidationError = ValidationError
    
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