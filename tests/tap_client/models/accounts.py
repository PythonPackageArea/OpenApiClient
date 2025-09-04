from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import exports
    from . import groups
    from . import includes
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

class SchemasCreate(BaseModel):
    id: Optional[int]
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None

class SchemasPaginated(BaseModel):
    data: List["Read"]
    total: int

class SchemasRead(BaseModel):
    id: int
    sessions: Optional[List["AccountSession"]] = None
    last_actions: Optional[List["LastAction"]] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None
    floodwait_until: Optional[datetime] = None
    premium_until: Optional[datetime] = None
    spamblock_until: Optional[datetime] = None
    datereg_at: Optional[datetime] = None
    datereg_date: Optional[datetime] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class SchemasUpdate(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None
    flood_wait_until: Optional[datetime] = None
    premium_until: Optional[datetime] = None
    spamblock_until: Optional[datetime] = None