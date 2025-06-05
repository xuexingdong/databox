import scrapy
from scrapy import Field


class Region(scrapy.Item):
    code = Field()
    name = Field()
    type = Field()
    parent_code = Field()
