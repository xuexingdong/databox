from scrapy import Item, Field


class Emoji(Item):
    code = Field()
    emoji = Field()
