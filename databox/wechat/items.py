from scrapy import Item, Field


class WechatMsgItem(Item):
    id = Field()
    title = Field()
