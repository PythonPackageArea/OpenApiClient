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
    from . import uploads
    from . import accounts
    from . import authentication
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update

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

class ExportsStatuses(str, Enum):
    ANY = 'ANY'
    ACTIVE = 'ACTIVE'
    NOT_ENOUGH_ACCOUNTS = 'NOT_ENOUGH_ACCOUNTS'
    READY_FOR_PACKING = 'READY_FOR_PACKING'
    READY_FOR_EXPORT = 'READY_FOR_EXPORT'
    ERROR = 'ERROR'

class HTTPValidationError(BaseModel):
    detail: Optional[List["ValidationError"]] = None

class InputStringSession(BaseModel):
    string_session: Optional[str] = None
    parameters: Optional["SessionParameters"] = None

class InputStrings(BaseModel):
    default_parameters: "SessionParameters"
    sessions: List["InputStringSession"]

class Keys(str, Enum):
    PROXIES = 'proxies'
    DEVICE_TOKENS = 'device_tokens'

class LastAction(BaseModel):
    group_id: Optional[str] = None
    last_action_at: Optional[datetime] = None

class LoginIn(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: "UserShort"

class ModuleTaskResponse(BaseModel):
    module: str
    session_data: "Sessions.SchemasRead"

class Response(BaseModel):
    id: int
    received: int
    created: int
    pending: Optional[int] = None
    create_error: Optional[int] = None
    session_ids: Optional[List[int]] = None
    existing_sessions: Optional[List[int]] = None

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

class SignUpIn(BaseModel):
    username: str
    password: str
    secret: str

class UserShort(BaseModel):
    id: str
    username: str
    password_changed_at: datetime
    created_at: datetime

class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class Paginated(BaseModel):
    data: List["Read"]
    total: int

class Read(BaseModel):
    key: str
    value: str
    updated_at: datetime
    created_at: datetime