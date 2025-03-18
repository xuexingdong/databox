import json
from typing import Iterable, Any

from playwright.async_api import expect
from playwright_stealth import stealth_async
from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.tiktok.tiktok_video_spider import TiktokVideoSpider


class TiktokVideoPlayWrightSpider(RedisSpider):
    name = 'tiktok:playwright'
    redis_key = name
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    headers = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        "Origin": "https://www.tiktok.com",
        "Referer": "https://www.tiktok.com"
    }

    def __init__(self, *args, nickname=None, **kwargs):
        super().__init__(**kwargs)
        self.nickname = nickname

    async def handle_page_route(self, route, request):
        response = await route.fetch()
        json = await response.json()
        await route.fulfill(response=response, json=json)

    def start_requests(self) -> Iterable[Request]:
        url = f'https://www.tiktok.com/@{self.nickname}'
        return [Request(url, headers=self.headers, dont_filter=True,
                        meta={"playwright": True,
                              "playwright_include_page": True,
                              "playwright_page_init_callback": TiktokVideoPlayWrightSpider.init_page,
                              "playwright_page_event_handlers": {
                                  "response": "handle_response"
                              }
                              })]

    @staticmethod
    async def init_page(page, request):
        await stealth_async(page)

    async def handle_response(self, response) -> None:
        if '/api/post/item_list/' in response.url:
            body = await response.body()
            if body:
                page = response.frame.page
                page_cookies = await page.context.cookies()
                cookies = {}
                for page_cookie in page_cookies:
                    cookies[page_cookie['name']] = page_cookie['value']
                self.server.setex('tiktok:cookie', 24 * 60 * 60, json.dumps(cookies))
                self.server.rpush(TiktokVideoSpider.redis_key, json.dumps({
                    "url": response.url
                }))

    async def parse(self, response: Response, **kwargs: Any) -> Any:
        page = response.meta["playwright_page"]
        try_again_button = page.locator('button', has_text='Try again')
        if await try_again_button.count() > 0:
            await try_again_button.click()
            await expect(page.locator('[data-e2e=tiktok-logo]')).to_be_visible()
        await page.keyboard.press("Escape")
        while True:
            refresh_button = page.locator('button', has_text="Refresh")
            if await refresh_button.count() == 0:
                break
            async with page.expect_response(lambda response: '/api/post/item_list/' in response.url) as _:
                await refresh_button.click()
            post_item_list_locator = page.locator('[data-e2e=user-post-item-list]')
            if await post_item_list_locator.count() > 0:
                break
        await page.wait_for_load_state()
        while True:
            post_item = page.locator('[data-e2e=user-post-item]')
            post_item_count = await post_item.count()
            await post_item.last.scroll_into_view_if_needed()
            await page.wait_for_load_state()
            new_post_item_count = await page.locator('[data-e2e=user-post-item]').count()
            if post_item_count == new_post_item_count:
                break
