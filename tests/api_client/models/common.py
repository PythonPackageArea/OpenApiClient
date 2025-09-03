from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import authentication
    from . import exports
    from . import groups
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import uploads

class HTTPValidationError(BaseModel):
    detail: Optional[List["ValidationError"]] = None

class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str