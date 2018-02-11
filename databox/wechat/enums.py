from enum import unique, Enum


@unique
class QRCodeStatus(Enum):
    WAITING = '等待扫码'
    SUCCESS = '扫码成功'
    EXPIRED = '二维码过期'
    CONFIRM = '确认登录'


@unique
class MsgType(Enum):
    TEXT = 1
    SYSTEM_MESSAGE = 10000
    VOICE = 34
    VIDEO1 = 43
    EMOTION = 47
    VIDEO2 = 62
    CALL = 50
    PICTURE = 3
    POSITION = 48
    CARD = 42
    LINK = 49
    # 撤回
    BLOCKED = 10002

    UNHANDLED = -999
