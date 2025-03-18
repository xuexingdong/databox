from pydantic import BaseModel
from scrapy import Item, Field

from databox.instagram.model import ProductType


class InsUserItem(BaseModel):
    id: str
    username: str
    full_name: str = ''
    biography: str = ''
    media_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    is_private: bool = False
    is_verified: bool = False
    profile_pic_url: str = ''
    hd_profile_pic_url: str = ''
    category: str = ''
    is_business: bool = False
    fbid_v2: str = ''
    pk: str


class InsMediaItem(BaseModel):
    user_id: str
    username: str
    code: str
    pk: str
    id: str
    taken_at: int
    image_url: str | None = None
    video_url: str | None = None
    caption: str | None = None
    caption_is_edited: bool = False
    comment_count: int = 0
    like_count: int = 0
    product_type: ProductType
