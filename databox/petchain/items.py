import scrapy
from scrapy import Field


class PetItem(scrapy.Item):
    id = Field()
    pet_id = Field()
    # 宠物昵称
    name = Field()
    # 背景颜色
    bg_color = Field()
    # 出生类型？
    birth_type = Field()
    # ？？？
    mutation = Field()
    # 第x代
    generation = Field()
    # 稀有度
    rare_degree = Field()
    # ？？？
    pet_type = Field()
    # 价格
    amount = Field()
    # 区块地址
    eth_addr = Field()
    # 父亲id
    father_id = Field()
    # 母亲id
    mother_id = Field()
    # 和onChain字段重复
    is_on_chain = Field()
    pet_url = Field()
    # 所属主人昵称
    username = Field()
    # 主人头像
    head_icon = Field()
    # 未知属性
    self_status = Field()
    # 宠物属性
    attributes = Field()
