from scrapy import Item, Field


class Profile(Item):
    id = Field()
    content = Field()


class MBlogItem(Item):
    id = Field()
    uid = Field()
    content = Field()


class CommentItem(Item):
    id = Field()
    uid = Field()
    content = Field()
