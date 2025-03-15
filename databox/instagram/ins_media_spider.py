from typing import Any

from scrapy import Spider


class InsMediaSpider(Spider):
    name = 'ins_media_spider'
    redis_key = "databox:" + name

    def __init__(self, name: str | None = None, media_id: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.media_id = media_id

    def parse(self, response, **kwargs: Any) -> Any:
        res = response.json()
        print(res)

    @staticmethod
    def get_media_info_url(media_id: str | None = None):
        return f"https://www.instagram.com/api/v1/media/{media_id}/info/"
