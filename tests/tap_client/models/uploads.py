from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import exports
    from . import groups
    from . import includes
    from . import sessions
    from . import settings
    from . import accounts
    from . import authentication
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update

class SchemasPaginated(BaseModel):
    data: List["Read"]
    total: int

class SchemasRead(BaseModel):
    id: int
    counts: "Includes.IncludesCounts"
    created_at: datetime