from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.common import *
from ..models.common import *
from ..models.schemas import *
from ..models.authentication import *
from ..models.bots import *
from ..models.broadcasts import *
from ..models.settings import *
from ..models.statistics import *
from ..models.uploads import *
from ..models.users import *
from ..models.withdrawals import *

class Common:
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client