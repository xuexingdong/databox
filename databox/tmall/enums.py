from enum import unique, Enum


@unique
class QRCodeStatus(Enum):
    WAITING = '等待扫码'
    SUCCESS = '扫码成功'
    EXPIRED = '二维码过期'
    CONFIRM = '确认登录'
