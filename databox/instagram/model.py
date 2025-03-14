from typing import Any

from pydantic import BaseModel, Field

from databox.instagram import constants


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
    relay_login: bool = Field(True, serialization_alias="__relay_internal__pv__PolarisIsLoggedInrelayprovider")
    relay_share: bool = Field(True, serialization_alias="__relay_internal__pv__PolarisShareSheetV3relayprovider")


class PolarisProfilePostsQuery(BaseInstagramQuery):
    variables: PolarisProfilePostsQueryVariables


class PolarisProfilePostsTabContentQuery_connectionVariables(PolarisProfilePostsQueryVariables):
    first: int = 12
    last: int | None = None
    before: str | None = None
    after: str | None = None


class PolarisProfilePostsTabContentQuery_connection(BaseInstagramQuery):
    variables: PolarisProfilePostsTabContentQuery_connectionVariables
