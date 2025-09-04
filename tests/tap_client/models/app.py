from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import authentication
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update

class AccountsCreate(BaseModel):
    id: Optional[int]
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    twofa: Optional[str] = None

class AccountsPaginated(BaseModel):
    data: List["Read11"]
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

class CreateApp(BaseModel):
    need_quality: int
    ids: Optional[List[int]] = None
    logged_after: Optional[int] = None
    logged_before: Optional[int] = None
    is_alive: Optional[bool] = None
    upload_id: Optional[str] = None
    account_id_setted: Optional[bool] = None
    have_premium: Optional[bool] = None
    have_spamblock: Optional[bool] = None
    have_floodwait: Optional[bool] = None
    check_spamblock: Optional[bool] = None
    created_at_max_ago: Optional[int] = None
    include_group_ids_or_titles: Optional[List[str]] = None
    exclude_group_ids_or_titles: Optional[List[str]] = None
    datereg_ago: Optional[int] = None
    datereg_after: Optional[int] = None
    include_phone_rules: Optional[List[str]] = None
    exclude_phone_rules: Optional[List[str]] = None
    search_tags: Optional[List[str]] = None

class PaginatedApp(BaseModel):
    data: List["Read11"]
    total: int

class ReadApp(BaseModel):
    id: int
    status: ExportsStatuses
    filename: Optional[str] = None
    need_quality: int
    counts: Optional["Counts"] = None
    filters: Optional[dict] = None
    created_at: datetime

class CountsApp(BaseModel):
    marked: Optional[int] = None
    status: Optional[int] = None
    wait_check: Optional[int] = None
    need_quality: Optional[int] = None

class CreateServices(BaseModel):
    title: str

class PaginatedServices(BaseModel):
    data: List["Read11"]
    total: int

class ReadServices(BaseModel):
    id: str
    title: str
    updated_at: datetime
    created_at: datetime

class UpdateApp(BaseModel):
    title: str

class CreateSessions(BaseModel):
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

class PaginatedSessions(BaseModel):
    data: List["Read11"]
    total: int

class ReadSessions(BaseModel):
    id: int
    account_id: Optional[int] = None
    account: Optional["Account"] = None
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

class UpdateServices(BaseModel):
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

class ReadSettings(BaseModel):
    key: str
    value: str
    updated_at: datetime
    created_at: datetime

class UpdateSettings(BaseModel):
    value: str

class CountsServices(BaseModel):
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

class PaginatedUploads(BaseModel):
    data: List["Read11"]
    total: int

class ReadUploads(BaseModel):
    id: int
    counts: "IncludesCounts"
    created_at: datetime