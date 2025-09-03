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
    from . import settings
    from . import uploads

class BodyUpdateManySessionsUpdateManyPut(BaseModel):
    ids: List[int]
    data: "SessionsUpdate"

class InputStringSession(BaseModel):
    string_session: Optional[str] = None
    parameters: Optional["SessionParameters"] = None

class SessionGroup(BaseModel):
    group_id: str
    title: Optional[str] = None

class SessionParameters(BaseModel):
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    twofa: Optional[str] = None

class SessionsCreate(BaseModel):
    string_session: Optional[str] = None
    upload_id: Optional[int] = None
    search_tags: Optional[List[str]] = None
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    twofa: Optional[str] = None

class SessionsPaginated(BaseModel):
    data: List["SessionsRead"]
    total: int

class SessionsRead(BaseModel):
    id: int
    account_id: Optional[int] = None
    account: Optional["accounts.Account"] = None
    string_session: Optional[str] = None
    groups: Optional[List["SessionGroup"]] = None
    search_tags: Optional[List[str]] = None
    upload_id: Optional[int] = None
    twofa: Optional[str] = None
    is_alive: Optional[bool] = None
    invalid_code: Optional[str] = None
    export_id: Optional[int] = None
    export_check: Optional[bool] = None
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    logged_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None
    updated_at: datetime
    created_at: datetime

class SessionsUpdate(BaseModel):
    account_id: Optional[int] = None
    string_session: Optional[str] = None
    upload_id: Optional[int] = None
    export_clear: Optional[bool] = None
    export_id: Optional[int] = None
    export_check: Optional[bool] = None
    twofa: Optional[str] = None
    is_alive: Optional[bool] = None
    invalid_code: Optional[str] = None
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    logged_at: Optional[datetime] = None
    last_heartbeat_at: Optional[datetime] = None