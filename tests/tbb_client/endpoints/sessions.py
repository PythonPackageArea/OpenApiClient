from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.sessions import *
from ..models.common import *
from ..models.authentication import *
from ..models.services import *
from ..models.settings import *
from ..models.uploads import *

class Sessions:
    input_session: InputSession = InputSession
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client