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
    from . import settings

class BodyUploadFileUploadsSendFilePost(BaseModel):
    file: bytes

class InputStrings(BaseModel):
    default_parameters: "sessions.SessionParameters"
    sessions: List["sessions.InputStringSession"]

class Response(BaseModel):
    id: int
    received: int
    created: int
    pending: Optional[int] = None
    create_error: Optional[int] = None
    session_ids: Optional[List[int]] = None
    existing_sessions: Optional[List[int]] = None

class UploadsCounts(BaseModel):
    total: Optional[int] = None
    not_checked: Optional[int] = None
    checked: Optional[int] = None
    dead: Optional[int] = None
    alive: Optional[int] = None
    sb: Optional[int] = None
    valid: Optional[int] = None
    exported: Optional[int] = None
    groups: Optional["Groups"] = None
    human_readable_discription: Optional[str] = None

class UploadsPaginated(BaseModel):
    data: List["UploadsRead"]
    total: int

class UploadsRead(BaseModel):
    id: int
    counts: "Counts"
    created_at: datetime