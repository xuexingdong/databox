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


class Note(Item):
    id = Field()
    model_type = Field()
    note_card = Field()
    track_id = Field()
    ignore = Field()
    _origin_data = Field()
