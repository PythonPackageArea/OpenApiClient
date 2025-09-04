from ..lib import models
from ..lib.utils import prepare_params, prepare_body_data, prepare_files, handle_request
from ..common import AiohttpClient
from typing import Union, Optional, List, Literal, Any
from datetime import datetime
from ..models.services import *
from ..models.common import *
from ..models.authentication import *
from ..models.sessions import *
from ..models.settings import *
from ..models.uploads import *

class Services:
    bots_create: BotsCreate = BotsCreate
    bots_paginated: BotsPaginated = BotsPaginated
    bots_read: BotsRead = BotsRead
    bots_update: BotsUpdate = BotsUpdate
    broadcasts_create: BroadcastsCreate = BroadcastsCreate
    broadcasts_paginated: BroadcastsPaginated = BroadcastsPaginated
    broadcasts_read: BroadcastsRead = BroadcastsRead
    broadcasts_update: BroadcastsUpdate = BroadcastsUpdate
    support_messages_create: Support_messagesCreate = Support_messagesCreate
    support_messages_paginated: Support_messagesPaginated = Support_messagesPaginated
    support_messages_read: Support_messagesRead = Support_messagesRead
    support_messages_update: Support_messagesUpdate = Support_messagesUpdate
    uploads_paginated: UploadsPaginated = UploadsPaginated
    uploads_read: UploadsRead = UploadsRead
    users_create: UsersCreate = UsersCreate
    users_paginated: UsersPaginated = UsersPaginated
    users_read: UsersRead = UsersRead
    users_update: UsersUpdate = UsersUpdate
    withdrawals_create: WithdrawalsCreate = WithdrawalsCreate
    withdrawals_paginated: WithdrawalsPaginated = WithdrawalsPaginated
    withdrawals_read: WithdrawalsRead = WithdrawalsRead
    withdrawals_update: WithdrawalsUpdate = WithdrawalsUpdate
    
    def __init__(
        self,
        client: AiohttpClient
    ) -> None:
    
        self.client = client