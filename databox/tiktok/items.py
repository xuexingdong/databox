from scrapy import Item, Field


class TiktokVideo(Item):
    id = Field()
    nickname = Field()
    avatar = Field()
    create_time = Field()
    desc = Field()
    cover = Field()
    download_addr = Field()
