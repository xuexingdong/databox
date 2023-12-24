import json
from typing import Iterable, Any

from scrapy import Spider, Request
from scrapy.http import Response


class WeiboSpider(Spider):
    name = 'weibo'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def __init__(self, *args, q=None, **kwargs):
        super().__init__(**kwargs)
        self.q = q

    def start_requests(self) -> Iterable[Request]:
        url = self.generate_url_by_q(self.q)
        return [Request(url, headers=self.HEADERS, dont_filter=True)]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        res = json.loads(response.text)
        print(res)

    @staticmethod
    def generate_url_by_q(q):
        return f'https://s.weibo.com/weibo?q={q}'
