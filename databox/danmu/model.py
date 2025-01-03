from enum import StrEnum
from typing import Optional

from pydantic.dataclasses import dataclass


class TypeEnum(StrEnum):
    mrkl = "mrkl"
    loginres = "loginres"
    chatmsg = "chatmsg"


@dataclass(config={'extra': 'allow'})
class LoginRes:
    type: str
    sid: str


@dataclass(config={'extra': 'allow'})
class Chatmsg:
    type: str  # 固定为 'chatmsg'
    rid: Optional[int] = None  # 房间 id
    uid: Optional[int] = None  # 发送者 uid
    nn: Optional[str] = None  # 发送者昵称
    txt: Optional[str] = None  # 弹幕文本内容
    level: Optional[int] = None  # 用户等级
    gt: Optional[int] = 0  # 礼物头衔，默认值 0
    col: Optional[int] = 0  # 颜色，默认值 0
    ct: Optional[int] = 0  # 客户端类型，默认值 0
    rg: Optional[int] = 1  # 房间权限组，默认值 1
    pg: Optional[int] = 1  # 平台权限组，默认值 1
    dlv: Optional[int] = 0  # 酬勤等级，默认值 0
    dc: Optional[int] = 0  # 酬勤数量，默认值 0
    bdlv: Optional[int] = 0  # 最高酬勤等级，默认值 0
    cmt: Optional[int] = 0  # 弹幕具体类型，默认值 0（普通弹幕）
    sahf: Optional[int] = 0  # 扩展字段，通常不使用
    ic: Optional[str] = None  # 用户头像
    nl: Optional[int] = None  # 贵族等级
    nc: Optional[int] = 0  # 贵族弹幕标识，默认值 0
    gatin: Optional[int] = None  # 进入网关服务时间戳
    chtin: Optional[int] = None  # 进入房间服务时间戳
    repin: Optional[int] = None  # 进入发送服务时间戳
    bnn: Optional[str] = None  # 徽章昵称
    bl: Optional[int] = 0  # 徽章等级
    brid: Optional[int] = None  # 徽章房间 id
    hc: Optional[str] = None  # 徽章信息校验码
    ol: Optional[int] = None  # 主播等级
    rev: Optional[int] = 0  # 反向弹幕标记，默认值 0
    hl: Optional[int] = 0  # 高亮弹幕标记，默认值 0
    ifs: Optional[int] = 0  # 粉丝弹幕标记，默认值 0
    p2p: Optional[str] = None  # 服务功能字段
