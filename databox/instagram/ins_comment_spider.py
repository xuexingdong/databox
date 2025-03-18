from typing import Any
from urllib.parse import urlencode

from pydantic import BaseModel
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from databox.instagram.model import CommentSortOrder


class InsCommentData(BaseModel):
    media_id: str
    can_support_threading: bool = True
    min_id: dict | None = None
    permalink_enabled: bool = False
    sort_order: CommentSortOrder = CommentSortOrder.POPULAR


class InsCommentSpider(RedisSpider):
    name = 'ins_comment_spider'
    redis_key = "databox:ins:" + name

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
    }

    def make_request_from_data(self, data):
        ins_comment_data = InsCommentData.model_validate_json(data)
        yield self.get_comment_request(ins_comment_data)

    def parse(self, response, **kwargs: Any) -> Any:
        json_data = response.json()
        if json_data['status'] != 'ok':
            return
        ins_comment_data = InsCommentData.model_validate(response.meta)
        ins_comment_data.min_id = json_data.get('next_min_id', None)
        if ins_comment_data.min_id:
            self.server.rpush(self.redis_key, ins_comment_data.model_dump_json())

    @staticmethod
    def get_comment_request(ins_comment_data: InsCommentData):
        base_url = f'https://www.instagram.com/api/v1/media/{ins_comment_data.media_id}/comments/'
        comment_url = f"{base_url}?{urlencode(ins_comment_data.model_dump(exclude_none=True))}"
        headers = {
            'x-ig-app-id': 936619743392459,
            'x-requested-with': 'XMLHttpRequest'
        }
        yield Request(
            url=comment_url,
            headers=headers,
            meta=ins_comment_data.model_dump(),
            dont_filter=True
        )
