import json
from typing import Any
from urllib.parse import urlencode

from scrapy import Spider, Request


class InsCommentSpider(Spider):
    name = 'ins_comment_spider'
    redis_key = "databox:" + name
    max_idle_time = 60 * 5

    headers = {
        'x-ig-app-id': 936619743392459,
        'x-requested-with': 'XMLHttpRequest'
    }
    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
    }

    def __init__(self, name: str | None = None, media_id: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.media_id = media_id

    def make_request_from_data(self, data):
        res = json.loads(data)
        pk = res['pk']
        yield Request(
            url=self.get_comments_url(pk),
            dont_filter=True,
        )

    def parse(self, response, **kwargs: Any) -> Any:
        res = response.json()
        pass

    @staticmethod
    def get_comments_url(media_id: str | None = None):
        base_url = f'https://www.instagram.com/api/v1/media/{media_id}/comments/'
        params = {
            'can_support_threading': True,
            'permalink_enabled': False,
        }
        return f"{base_url}?{urlencode(params)}"
