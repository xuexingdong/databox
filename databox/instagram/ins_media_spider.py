from typing import Any

from scrapy_redis.spiders import RedisSpider


class InsMediaSpider(RedisSpider):
    name = 'ins_media_spider'
    redis_key = "databox:ins:" + name

    def parse(self, response, **kwargs: Any) -> Any:
        res = response.json()
        print(res)

    @staticmethod
    def get_media_info_url(media_id: str | None = None):
        return f"https://www.instagram.com/api/v1/media/{media_id}/info/"
