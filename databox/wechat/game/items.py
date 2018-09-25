from scrapy import Item, Field


class TopicItem(Item):
    topic_id = Field()
    pic_urls = Field()


class ReplyItem(Item):
    reply_id = Field()
    parent_reply_id = Field()
    topic_id = Field()
    pic_urls = Field()
