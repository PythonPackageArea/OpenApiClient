from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import authentication
    from . import bots
    from . import broadcasts
    from . import settings
    from . import statistics
    from . import uploads
    from . import users
    from . import withdrawals

class SchemasCreate(BaseModel):
    user_id: int
    bot_id: Optional[int] = None
    input_value: float
    output_value: float
    method: str
    requisite: Optional[str] = None

class SchemasPaginated(BaseModel):
    data: List["Read"]
    total: int

class SchemasRead(BaseModel):
    id: int
    input_value: float
    output_value: float
    method: str
    status: WithdrawalStatus
    paid_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    requisite: Optional[str] = None
    user_id: int
    updated_at: datetime
    created_at: datetime

class SchemasUpdate(BaseModel):
    status: Optional[WithdrawalStatus] = None
    requisite: Optional[str] = None
    increment_value: Optional[float] = None
    decrement_value: Optional[float] = None