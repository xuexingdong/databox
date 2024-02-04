from typing import Iterable, Any

from playwright.sync_api import Page
from scrapy import Spider, Request


class WeiboAccountSpider(Spider):
    name = 'weibo_account'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'PLAYWRIGHT_CONTEXT': {
            "persistent": {
                "user_data_dir": "/Users/xuexingdong/workspace/databox/user-dir",  # will be a persistent context
            }
        }
    }

    def __init__(self, username=None, password=None, **kwargs: Any):
        super().__init__(**kwargs)
        self.username = username
        self.password = password

    def start_requests(self) -> Iterable[Request]:
        yield Request('https://login.sina.com.cn/signup/signin.php',
                      meta={
                          'playwright': True,
                          'playwright_include_page': True,
                          # 'playwright_page_methods': [
                          #     PageMethod('fill', selector='#username', value=self.username),
                          #     PageMethod('fill', selector='#password', value=self.password),
                          #     PageMethod('click', selector='input[type=submit]'),
                          # ],
                      },
                      dont_filter=True)

    def parse(self, response, **kwargs):
        page: Page = response.meta['playwright_page']
        page.fill(selector='#username', value=self.username),
        page.fill(selector='#password', value=self.password),
        page.click(selector='input[type=submit]')
        page.wait_for_load_state('networkidle')
        check_img_path = 'screenshot.png'
        page.locator('#check_img').screenshot(path=check_img_path)
        door = input()
        page.fill(selector='#door', value=door),
        page.click(selector='input[type=submit]')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000000)

    def recg_check_img(self, check_img_path):
        return check_img_path
