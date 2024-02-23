from typing import Iterable, Any

from scrapy import Spider, Request
from scrapy.http import Response


class TiktokVideoSpider(Spider):
    name = 'tiktok:video'
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    }

    def __init__(self, *args, username=None, **kwargs):
        super().__init__(**kwargs)
        self.username = username

    def start_requests(self) -> Iterable[Request]:
        url = f'https://www.tiktok.com/@{self.username}'
        return [Request(url, dont_filter=True, meta={"playwright": True, "playwright_include_page": True})]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        # https://www.tiktok.com/api/post/item_list
        print(response.text)
