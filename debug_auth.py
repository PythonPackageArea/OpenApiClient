from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import accounts
    from . import app
    from . import exports
    from . import file
    from . import module_tasks
    from . import sessions
    from . import settings
    from . import update
    from . import uploads


class LoginInLoginin(BaseModel):
    username: str
    password: str


class LoginResponseLoginresponse(BaseModel):
    token: str
    user: "UserShort"


class SignUpInSignupin(BaseModel):
    username: str
    password: str
    secret: str


class UserShortUsershort(BaseModel):
    id: str
    username: str
    password_changed_at: datetime
    created_at: datetime
