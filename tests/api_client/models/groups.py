from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import authentication
    from . import exports
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import uploads

class GroupsCreate(BaseModel):
    title: str

class GroupsPaginated(BaseModel):
    data: List["GroupsRead"]
    total: int

class GroupsRead(BaseModel):
    id: str
    title: str
    updated_at: datetime
    created_at: datetime

class GroupsUpdate(BaseModel):
    title: str