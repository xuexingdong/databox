from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from databox.instagram import constants


# Instagram 媒体产品类型枚举
class ProductType(Enum):
    FEED = "feed"  # 普通帖子
    IGTV = "igtv"  # IGTV 视频
    CLIPS = "clips"  # Reels 短视频
    CAROUSEL_CONTAINER = "carousel_container"  # 轮播图集
    GUIDE = "guide"  # 指南
    COLLECTION = "collection"  # 收藏集
    STORY = "story"  # 故事


class CommentSortOrder(Enum):
    POPULAR = "popular"  # 按热度排序
    RECENT = "recent"  # 按时间排序


class BaseInstagramQuery(BaseModel):
    variables: BaseModel

    def to_request_body(self) -> dict[str, Any]:
        return {
            'variables': self.variables.model_dump_json(by_alias=True),
            'doc_id': constants.DOC_ID_MAP.get(self.__class__.__name__),
        }


class ProfileQueryVariables(BaseModel):
    id: str
    render_surface: str = "PROFILE"


class PolarisProfilePageContentQuery(BaseInstagramQuery):
    variables: ProfileQueryVariables


class PostsQueryData(BaseModel):
    count: int = 12
    include_reel_media_seen_timestamp: bool = True
    include_relationship_info: bool = True
    latest_besties_reel_media: bool = True
    latest_reel_media: bool = True


class PolarisProfilePostsQueryVariables(BaseModel):
    username: str
    data: PostsQueryData = PostsQueryData()
    # pydantic can't serialize with variables start with underscore
    relay_login: bool = Field(default=True,
                              serialization_alias="__relay_internal__pv__PolarisIsLoggedInrelayprovider")
    relay_share: bool = Field(default=True,
                              serialization_alias="__relay_internal__pv__PolarisShareSheetV3relayprovider")


class PolarisProfilePostsQuery(BaseInstagramQuery):
    variables: PolarisProfilePostsQueryVariables


class PolarisProfilePostsTabContentQuery_connectionVariables(PolarisProfilePostsQueryVariables):
    first: int = 12
    last: int | None = None
    before: str | None = None
    after: str | None = None


class PolarisProfilePostsTabContentQuery_connection(BaseInstagramQuery):
    variables: PolarisProfilePostsTabContentQuery_connectionVariables


class CommentPayload(BaseModel):
    can_support_threading: bool = True
    min_id: str = ''
    sort_order: CommentSortOrder = CommentSortOrder.POPULAR
