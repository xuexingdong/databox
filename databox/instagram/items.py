from scrapy import Item, Field


class InsUserItem(Item):
    id = Field()
    username = Field()
    full_name = Field()
    biography = Field()
    media_count = Field()
    follower_count = Field()
    following_count = Field()
    is_private = Field()
    is_verified = Field()
    profile_pic_url = Field()
    hd_profile_pic_url = Field()
    category = Field()
    is_business = Field()
    fbid = Field()
    pk = Field()


class InsMediaItem(Item):
    user_id = Field()
    username = Field()
    code = Field()
    pk = Field()
    id = Field()
    taken_at = Field()
    caption = Field()
    caption_is_edited = Field()
    media_url = Field()
    comment_count = Field()
    like_count = Field()
    product_type = Field()
    created_at = Field()
    updated_at = Field()
