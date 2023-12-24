from typing import Iterable

from scrapy import Spider, Request


class WeiboAccountSpider(Spider):
    name = 'weibo_account'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_pyppeteer.handler.ScrapyPyppeteerDownloadHandler",
            "https": "scrapy_pyppeteer.handler.ScrapyPyppeteerDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PYPPETEER_LAUNCH_OPTIONS": {
            "executablePath": "",
            "headless": False
        },
    }

    def start_requests(self) -> Iterable[Request]:
        yield Request("https://www.baidu.com/", meta={"pyppeteer": True}, dont_filter=True)

    def parse(self, response):
        # 'response' contains the page as seen by the browser
        print(response)
        yield {"url": response.url}
