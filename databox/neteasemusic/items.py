import scrapy
from scrapy import Field


class UserItem(scrapy.Item):
    id = Field()
    nickname = Field()
    event_count = Field()
    follow_count = Field()
    fan_count = Field()
    description = Field()
    address = Field()


class FollowItem(scrapy.Item):
    id1 = Field()
    id2 = Field()
