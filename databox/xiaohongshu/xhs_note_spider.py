import json
from typing import Iterable, Any

from scrapy import Spider, Request
from scrapy.http import Response, JsonRequest

from databox.xiaohongshu.utils import XiaohongshuUtil


class XiaohongshuSpider(Spider):
    name = 'xiaohongshu:note'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'databox.xiaohongshu.middlewares.XiaohongshuHeaderMiddleware': 501
        },
    }

    def __init__(self, *args, user_red_id=None, start_date=None, end_date=None, start_note_id=None, end_note_id=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.user_red_id = user_red_id
        self.start_date = start_date
        self.end_date = end_date,
        self.start_note_id = start_note_id
        self.end_note_id = end_note_id

    def start_requests(self) -> Iterable[Request]:
        url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'
        data = {
            "keyword": self.keyword,
            "page": self.page,
            "page_size": self.page_size,
            "search_id": XiaohongshuUtil.generate_search_id(),
            "sort": "general",
            "note_type": 0,
            "ext_flags": [],
            "image_formats": ["jpg", "webp", "avif"]
        }
        return [JsonRequest(url, headers=self.HEADERS, data=data)]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        res = json.loads(response.text)
        print(res)
