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
    from . import uploads
    from . import accounts
    from . import authentication
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update

class SchemasRead(BaseModel):
    key: str
    value: str
    updated_at: datetime
    created_at: datetime

class SchemasUpdate(BaseModel):
    value: str