from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import authentication
    from . import exports
    from . import groups
    from . import sessions
    from . import settings
    from . import uploads

class ModuleTaskResponse(BaseModel):
    module: str
    session_data: "Read"