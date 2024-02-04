import json
from typing import Iterable, Any
from urllib.parse import urlencode

from scrapy import Spider, Request
from scrapy.http import Response


class XiaohongshuNoteSpider(Spider):
    name = 'xiaohongshu:note'
    collection = 'xiaohongshu_note'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'databox.xiaohongshu.middlewares.XiaohongshuHeaderMiddleware': 501
        },
    }
    need_login = True

    def __init__(self, *args, user_id=None, start_date=None, end_date=None, start_note_id=None, end_note_id=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date,
        self.start_note_id = start_note_id
        self.end_note_id = end_note_id

    def start_requests(self) -> Iterable[Request]:
        params = {
            'num': 30,
            'cursor': None,
            'user_id': self.user_id,
            'image_formats': 'jpg,webp,avif'
        }
        url = f'https://edith.xiaohongshu.com/api/sns/web/v1/user_posted?{urlencode(params)}'
        return [Request(url, dont_filter=True)]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        res = json.loads(response.text)
        print(res)
