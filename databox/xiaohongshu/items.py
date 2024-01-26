from scrapy import Item, Field


class User(Item):
    # 0男 1女
    user_id = Field()
    gender = Field()
    ip_location = Field()
    desc = Field()
    imageb = Field()
    nickname = Field()
    red_id = Field()
    follows = Field()
    fans = Field()
    interaction = Field()
    _origin_data = Field()
