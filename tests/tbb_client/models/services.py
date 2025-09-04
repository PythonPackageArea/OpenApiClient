from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import authentication
    from . import sessions
    from . import settings
    from . import uploads

class BotsCreate(BaseModel):
    token: Optional[str] = None
    owner_telegram_id: Optional[int] = None
    rev_share_percent: Optional[int] = None

class BotsPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class BotsRead(BaseModel):
    id: int
    api_token: Optional[str] = None
    username: Optional[str] = None
    token: Optional[str] = None
    string_session: Optional[str] = None
    menu_photo_id: Optional[str] = None
    owner_telegram_id: Optional[int] = None
    individual_boost: Optional[int] = None
    balance: float
    total_earned: float
    rev_share_percent: int
    updated_at: datetime
    created_at: datetime

class BotsUpdate(BaseModel):
    token: Optional[str] = None
    owner_telegram_id: Optional[int] = None
    rev_share_percent: Optional[int] = None
    reset_api_token: Optional[bool] = None
    menu_photo_id: Optional[str] = None
    individual_boost: Optional[int] = None
    increment_balance: Optional[float] = None
    decrement_balance: Optional[float] = None
    is_active: Optional[bool] = None

class BroadcastsCreate(BaseModel):
    bot_id: int
    message_id: int
    from_chat_id: int
    reply_markup: Optional[str] = None

class BroadcastsPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class BroadcastsRead(BaseModel):
    id: int
    bot_id: int
    message_id: int
    from_chat_id: int
    reply_markup: Optional[str] = None
    status: BroadcastStatus
    target_users_count: int
    sent_count: int
    failed_count: int
    retry_count: int
    worker_id: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    recovery_timeout: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BroadcastsUpdate(BaseModel):
    reply_markup: Optional[str] = None
    status: Optional[BroadcastStatus] = None
    target_users_count: Optional[int] = None
    sent_count: Optional[int] = None
    failed_count: Optional[int] = None
    retry_count: Optional[int] = None
    worker_id: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class Support_messagesCreate(BaseModel):
    out: bool
    content: str
    user_id: Optional[int] = None
    support_id: Optional[int] = None

class Support_messagesPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class Support_messagesRead(BaseModel):
    out: bool
    content: str
    user_id: Optional[int] = None
    support_id: Optional[int] = None
    mark_as_solved: Optional[bool] = None
    updated_at: datetime
    created_at: datetime

class Support_messagesUpdate(BaseModel):
    mark_as_solved: Optional[bool] = None

class UploadsPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class UploadsRead(BaseModel):
    id: int
    backend_id: Optional[int] = None
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size_mb: Optional[int] = None
    file_unique_id: Optional[str] = None
    file_message_id: Optional[int] = None
    callback_message_id: Optional[int] = None
    from_bot: Optional[bool] = None
    from_api: Optional[bool] = None
    user_id: int
    upload_rent_reauth: Optional[bool] = None
    upload_app_id: Optional[int] = None
    upload_type: Type
    counts: Optional["ServicesCounts"] = None
    done: Optional[bool] = None
    cancelled: Optional[bool] = None
    last_take_at: Optional[datetime] = None
    updated_at: datetime
    created_at: datetime

class UsersCreate(BaseModel):
    telegram_id: Optional[int] = None
    bot_id: Optional[int] = None
    referrer_id: Optional[int] = None
    language: Literal['en', 'ru']
    full_name: Optional[str] = None
    username: Optional[str] = None

class UsersPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class UsersRead(BaseModel):
    id: int
    api_token: str
    bot_id: Optional[int] = None
    language: Literal['en', 'ru']
    banned: bool
    is_admin: bool
    telegram_id: Optional[int] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    upload_app_id: Optional[int] = None
    upload_type: Optional[str] = None
    upload_rent_reauth: Optional[bool] = None
    referrer_id: Optional[int] = None
    total_earned_from_referrals: float
    individual_boost: Optional[int] = None
    bot_initialized: Optional[bool] = None
    balance: float
    total_earned: float
    total_sold: int
    updated_at: datetime
    created_at: datetime

class UsersUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    upload_app_id: Optional[int] = None
    upload_type: Optional[str] = None
    upload_rent_reauth: Optional[bool] = None
    banned: Optional[bool] = None
    is_admin: Optional[bool] = None
    language: Optional[Literal['en', 'ru']] = None
    referrer_id: Optional[int] = None
    individual_boost: Optional[int] = None
    bot_initialized: Optional[bool] = None
    increment_balance: Optional[float] = None
    decrement_balance: Optional[float] = None
    reset_api_token: Optional[bool] = None

class WithdrawalsCreate(BaseModel):
    user_id: int
    bot_id: Optional[int] = None
    input_value: float
    output_value: float
    method: str
    requisite: Optional[str] = None

class WithdrawalsPaginated(BaseModel):
    data: List["settings.SettingRead"]
    total: int

class WithdrawalsRead(BaseModel):
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

class WithdrawalsUpdate(BaseModel):
    status: Optional[WithdrawalStatus] = None
    requisite: Optional[str] = None
    increment_value: Optional[float] = None
    decrement_value: Optional[float] = None