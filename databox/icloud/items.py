from scrapy import Item, Field


class LocationItem(Item):
    longitude = Field()
    latitude = Field()
    created_at = Field()
