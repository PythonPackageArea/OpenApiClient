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
    from . import uploads

class Keys(str, Enum):
    PROXIES = 'proxies'
    DEVICE_TOKENS = 'device_tokens'

class SettingsRead(BaseModel):
    key: str
    value: str
    updated_at: datetime
    created_at: datetime

class SettingsUpdate(BaseModel):
    value: str