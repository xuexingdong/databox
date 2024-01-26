from enum import Enum


class PlatformCode(Enum):
    Windows = 0
    iOS = 1
    Android = 2
    MacOs = 3
    Linux = 4
    other = 5


class CodeStatus(Enum):
    WAIT_SCAN = 0
    SCANNED = 1
    SUCCESS = 2
    EXPIRED = 3


class InteractionTypeEnum(Enum):
    FOLLOWS = "follows"
    FANS = "fans"
    INTERACTION = "interaction"
# {
#     "code": 0,
#     "success": true,
#     "msg": "成功",
#     "data": {
#         "code_status": 2,
#         "login_info": {
#             "secure_session": "X4cb59session.040069b41052a758e8ea07d185374bb3100948",
#             "user_id": "656411ef000000000202b8bc",
#             "session": "040069b41052a758e8ea07d185374bb3100948"
#         }
#     }
# }
