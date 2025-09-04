from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import authentication
    from . import services
    from . import settings
    from . import uploads

class InputSession(BaseModel):
    string: str
    parameters: Optional["Parameters"] = None