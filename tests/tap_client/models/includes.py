from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import exports
    from . import groups
    from . import sessions
    from . import settings
    from . import uploads
    from . import accounts
    from . import authentication
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update

class IncludesCounts(BaseModel):
    total: Optional[int] = None
    not_checked: Optional[int] = None
    checked: Optional[int] = None
    dead: Optional[int] = None
    alive: Optional[int] = None
    sb: Optional[int] = None
    valid: Optional[int] = None
    exported: Optional[int] = None
    groups: Optional[Dict[str, int]] = None
    human_readable_discription: Optional[str] = None