from enum import unique, Enum


@unique
class TmallQrCodeScanStatus(Enum):
    WAITING = '10000'
    SUCCESS = '10001'
    EXPIRED = '10004'
    CONFIRM = '10006'
