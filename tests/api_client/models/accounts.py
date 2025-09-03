from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import authentication
    from . import exports
    from . import groups
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import uploads

class Account(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None
    last_actions: Optional[List["AccountLastAction"]] = None
    floodwait_until: Optional[datetime] = None
    premium_until: Optional[datetime] = None
    spamblock_until: Optional[datetime] = None
    datereg_at: Optional[datetime] = None
    datereg_date: Optional[datetime] = None

class AccountLastAction(BaseModel):
    group_id: Optional[str] = None
    last_action_at: Optional[datetime] = None

class AccountSession(BaseModel):
    id: int
    string_session: Optional[str] = None
    is_alive: Optional[bool] = None
    invalid_code: Optional[str] = None
    upload_id: Optional[int] = None
    export_id: Optional[int] = None
    export_check: Optional[int] = None
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    logged_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class LastAction(BaseModel):
    group_id: Optional[str] = None
    last_action_at: Optional[datetime] = None

class AccountsCreate(BaseModel):
    id: Optional[int]
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None

class AccountsPaginated(BaseModel):
    data: List["AccountsRead"]
    total: int

class AccountsRead(BaseModel):
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

class AccountsUpdate(BaseModel):
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None
    flood_wait_until: Optional[datetime] = None
    premium_until: Optional[datetime] = None
    spamblock_until: Optional[datetime] = None