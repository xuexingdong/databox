from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.tiktok.items import TiktokVideo


class TiktokVideoSpider(RedisSpider):
    name = 'tiktok:video'
    redis_key = name
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'databox.tiktok.middlewares.TiktokCookieMiddleWare': 501
        },
        'ITEM_PIPELINES': {
            'databox.tiktok.pipelines.TiktokVideoPipeline': 800
        },
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            "Referer": "https://www.tiktok.com"
        }
    }

    def parse(self, response: Response, **kwargs: Any) -> Any:
        print(response.url)
        res = response.json()
        for item in res['itemList']:
            author_info = item['author']
            video_info = item['video']

            video = TiktokVideo()
            video['id'] = item['id']
            video['nickname'] = author_info['nickname']
            video['avatar'] = author_info['avatarThumb']
            video['create_time'] = datetime.fromtimestamp(item['createTime'])
            video['desc'] = item['desc']
            video['cover'] = video_info['cover']
            video['download_addr'] = video_info['downloadAddr']
            print(video['id'])
            yield video

    def parse_video(self, response, **kwargs: Any) -> Any:
        file_name = urlparse(response.url).path.rsplit('/')[-2] + '.mp4'
        with open(file_name, 'wb') as f:
            f.write(response.body)
