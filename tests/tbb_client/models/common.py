from pydantic import BaseModel
from enum import Enum
from typing import Optional, Union, List, Dict, Literal, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from . import schemas
    from . import authentication
    from . import bots
    from . import broadcasts
    from . import settings
    from . import statistics
    from . import uploads
    from . import users
    from . import withdrawals

class BotProfile(BaseModel):
    id: int
    balance: float
    total_earned: float
    rev_share_percent: int
    total_users: int
    total_active_users: int
    boost_level: int
    boost_in_percent: int
    total_sold_in_30_days: int
    total_hold_items: int
    statistic_at: datetime

class BroadcastStatsSchema(BaseModel):
    sent_count: Optional[int] = None
    failed_count: Optional[int] = None
    pending_count: Optional[int] = None
    retry_count: Optional[int] = None
    total_count: Optional[int] = None

class BroadcastStatus(str, Enum):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    FAILED = 'FAILED'
    RECOVERING = 'RECOVERING'

class ClientTakeUpload(BaseModel):
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
    counts: Optional["Counts"] = None
    done: Optional[bool] = None
    cancelled: Optional[bool] = None
    last_take_at: Optional[datetime] = None
    updated_at: datetime
    created_at: datetime
    bot_id: int
    bot_token: str
    bot_string_session: str
    user_language: str

class Counts(BaseModel):
    total: Optional[int] = None
    checking: Optional[int] = None
    invalid: Optional[int] = None
    received: Optional[int] = None
    duplicate: Optional[int] = None
    hold: Optional[int] = None
    passed: Optional[int] = None
    free_income: Optional[float] = None
    hold_income: Optional[float] = None

class HTTPValidationError(BaseModel):
    detail: Optional[List["ValidationError"]] = None

class InputSession(BaseModel):
    string: str
    parameters: Optional["Parameters"] = None

class InputValue(BaseModel):
    value: Union[str, dict]

class LoginIn(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: "UserShort"

class Parameters(BaseModel):
    app_id: Optional[int] = None
    app_hash: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None
    system_version: Optional[str] = None
    system_lang_code: Optional[str] = None
    lang_code: Optional[str] = None
    twofa: Optional[str] = None

class PriceMenu(BaseModel):
    bot_price: float
    user_price: float
    user_boost_percent: float

class PriceSetting(BaseModel):
    startswith: Optional[str] = None
    increment: Optional[float] = None
    decrement: Optional[float] = None

class RaitingItem(BaseModel):
    user_id: int
    value: int

class ReadInput(BaseModel):
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

class SendStrings(BaseModel):
    id: Optional[int] = None
    default_parameters: Optional["Parameters"] = None
    sessions: List["InputSession"]

class SettingRead(BaseModel):
    key: str
    value: Union[str, dict, int]
    updated_at: datetime
    created_at: datetime

class SignUpIn(BaseModel):
    username: str
    password: str
    secret: str

class TopBotItem(BaseModel):
    bot_id: int
    username: Optional[str]
    total: int
    account_types: Dict[str, int]

class TopBotsPeriods(BaseModel):
    d1: List["TopBotItem"]
    d7: List["TopBotItem"]
    d30: List["TopBotItem"]

class TopBotsResponse(BaseModel):
    periods: "TopBotsPeriods"

class Type(str, Enum):
    SELL = 'SELL'
    RENT = 'RENT'

class UploadCategoryStats(BaseModel):
    account_type: str
    total_sessions: int
    alive_sessions: int
    dead_sessions: int
    duplicate_sessions: int
    auto_reg_count: int
    auto_reg_percentage: float
    money_on_hold: float
    money_earned: float

class UploadCreate(BaseModel):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size_mb: Optional[int] = None
    file_unique_id: Optional[str] = None
    file_message_id: Optional[int] = None
    callback_message_id: Optional[int] = None
    from_bot: Optional[bool] = None
    from_api: Optional[bool] = None
    upload_rent_reauth: Optional[bool] = None
    upload_app_id: Optional[int] = None
    upload_type: Type
    user_id: int
    default_parameters: Optional["Parameters"] = None
    sessions: Optional[List["InputSession"]] = None

class UploadStatsResponse(BaseModel):
    categories: List["UploadCategoryStats"]
    total_stats: "UploadCategoryStats"
    generated_at: datetime

class UploadUpdate(BaseModel):
    done: Optional[bool] = None
    cancelled: Optional[bool] = None
    callback_message_id: Optional[int] = None
    set_now_take: Optional[bool] = None
    clear_file_unique_id: Optional[bool] = None

class UserPricesByAccountType(BaseModel):
    account_type: str
    service_default: float
    user_default: float
    countries: Dict[str, float]

class UserPricesByAllTypes(BaseModel):
    account_types: Dict[str, "UserPricesByAccountType"]

class UserPricesByCountries(BaseModel):
    service_default: float
    user_default: float
    countries: Dict[str, float]

class UserProfile(BaseModel):
    id: int
    free_balance: float
    total_hold_items: int
    total_hold_balance: float
    total_sold_in_ever: int
    total_sold_in_30_days: int
    total_rent_workers: int
    total_earned: float
    boost_level: int
    boost_in_percent: int
    statistic_at: datetime

class UserReferals(BaseModel):
    quantity: int
    total_earned: float

class UserShort(BaseModel):
    id: str
    username: str
    password_changed_at: datetime
    created_at: datetime

class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class WithdrawalMethod(BaseModel):
    percent_fee: Optional[float] = None
    stable_fee: Optional[float] = None

class WithdrawalStatus(str, Enum):
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    PAID = 'PAID'
    CANCELLED = 'CANCELLED'

class Paginated(BaseModel):
    data: List["Read"]
    total: int

class Read(BaseModel):
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