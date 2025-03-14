from typing import Any
from urllib.parse import urlencode

from scrapy import Spider


class InsCommentSpider(Spider):
    name = 'ins_comment_spider'

    start_urls = ['https://www.instagram.com/explore/']

    def __init__(self, name: str | None = None, media_id: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.media_id = media_id

    def parse(self, response, **kwargs: Any) -> Any:
        res = response.json()

    @staticmethod
    def get_comments_url(media_id: str | None = None):
        base_url = f'https://www.instagram.com/api/v1/media/{media_id}/comments/'
        params = {
            'can_support_threading': True,
            'permalink_enabled': False,
        }
        return f"{base_url}?{urlencode(params)}"
