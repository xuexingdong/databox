from enum import unique, IntEnum, StrEnum


@unique
class OptionType(IntEnum):
    TEXT = 101
    # 富文本，比如根号三这种需要使用latex和图片的选项
    RICH_TEXT = 102


class XingceModule(StrEnum):
    ZHENGZHI = '政治理论'
    CHANGSHI = '常识判断'
    YANYU = '言语理解与表达'
    SHULIANG = '数量关系'
    PANDUAN = '判断推理'
    ZILIAO = '资料分析'


class XingceSubModule(StrEnum):
    LUOJITIANKONG = '逻辑填空'
