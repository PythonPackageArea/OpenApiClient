from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import exports
    from . import groups
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import uploads

class LoginIn(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: "UserShort"

class SignUpIn(BaseModel):
    username: str
    password: str
    secret: str

class UserShort(BaseModel):
    id: str
    username: str
    password_changed_at: datetime
    created_at: datetime