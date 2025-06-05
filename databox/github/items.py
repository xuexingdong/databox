from scrapy import Item, Field


class Repo(Item):
    name = Field()
    title = Field()
    description = Field()
    avatar_url = Field()
    author_name = Field()
    author_avatar_url = Field()
    tags = Field()
    url = Field()
    content = Field()
    img_url = Field()
