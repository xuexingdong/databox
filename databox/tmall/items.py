from scrapy import Item, Field


class TmallItem(Item):
    id = Field()
    title = Field()
    created_at = Field()


class TmallSkuItem(Item):
    id = Field()
    item_id = Field()
    price = Field()
    promotion_price = Field()
    created_at = Field()


class TmallRateItem(Item):
    id = Field()
    item_id = Field()
    # 金牌会员
    goldUser = Field()
    # 用户vip等级
    userVipLevel = Field()
    content = Field()
    created_at = Field()
