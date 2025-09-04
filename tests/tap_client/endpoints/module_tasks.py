from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.module_tasks import *
from ..models.common import *
from ..models.accounts import *
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
from ..models.sessions import *
from ..models.settings import *
from ..models.update import *

class Module_tasks:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client
    
    async def take_module_task(
        self,
        module_path: str
    ) -> Optional[ModuleTaskResponse]:
    
        """
        Отдаёт задачу для модуля, описанного в modules.yml
        
        Args:
            self (Any): Parameter description
            module_path (str): Parameter description
        
        Returns:
            Optional[ModuleTaskResponse]: Response data
        """
    
        path = f'/modules/{module_path}/take'.rstrip()
        return await handle_request(self.client, 'get', path, locals(), response_model=ModuleTaskResponse)