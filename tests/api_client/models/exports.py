from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import authentication
    from . import groups
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import uploads

class ExportsStatuses(str, Enum):
    ANY = 'ANY'
    ACTIVE = 'ACTIVE'
    NOT_ENOUGH_ACCOUNTS = 'NOT_ENOUGH_ACCOUNTS'
    READY_FOR_PACKING = 'READY_FOR_PACKING'
    READY_FOR_EXPORT = 'READY_FOR_EXPORT'
    ERROR = 'ERROR'

class ExportsCreate(BaseModel):
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

class ExportsPaginated(BaseModel):
    data: List["ExportsRead"]
    total: int

class ExportsRead(BaseModel):
    id: int
    status: Literal['ANY', 'ACTIVE', 'NOT_ENOUGH_ACCOUNTS', 'READY_FOR_PACKING', 'READY_FOR_EXPORT', 'ERROR']
    filename: Optional[str] = None
    need_quality: int
    counts: Optional["Counts"] = None
    filters: Optional[dict] = None
    created_at: datetime

class ExportsCounts(BaseModel):
    marked: Optional[int] = None
    status: Optional[int] = None
    wait_check: Optional[int] = None
    need_quality: Optional[int] = None