import json
import re
from typing import Any

from playwright.async_api import Page
from scrapy import Spider, Request
from scrapy.http import Response


class InsDocIdSpider(Spider):
    name = 'ins_doc_id_spider'
    DOC_ID_PATTERN = r'__d\("(.*?)_instagramRelayOperation".*?e\.exports\s*=\s*"(\d+)"'
    X_IG_APP_ID_PATTERN = r'"X-IG-App-ID":\s*"(\d+)"'

    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    }

    def start_requests(self):
        yield Request(
            url='https://example.com/',
            callback=self.parse,
            meta={"playwright": True, "playwright_include_page": True},
            dont_filter=True
        )

    async def parse(self, response: Response, **kwargs: Any) -> Any:
        page: Page = response.meta["playwright_page"]
        js_responses = []

        async def handle_response(resp):
            if 'static.cdninstagram.com/rsrc.php' in resp.url and resp.url.endswith('.js'):
                js_content = await resp.text()
                js_responses.append(js_content)

        operation_name_doc_id_mapping = {}
        try:
            page.on('response', handle_response)
            await page.goto('https://www.instagram.com/')
            await page.wait_for_load_state("networkidle")
            # wait for sure
            await page.wait_for_timeout(2000)

            content = await page.content()
            x_ig_app_id_match = re.search(self.X_IG_APP_ID_PATTERN, content)
            if x_ig_app_id_match:
                x_ig_app_id = x_ig_app_id_match.group(1)
                self.logger.info("X-IG-App-ID: %s", x_ig_app_id)

            for text in js_responses:
                matches = re.finditer(self.DOC_ID_PATTERN, text, re.MULTILINE)
                for match in matches:
                    operation_name = match.group(1)
                    doc_id = match.group(2)
                    operation_name_doc_id_mapping[operation_name] = doc_id
            self.logger.info(json.dumps(operation_name_doc_id_mapping, indent=2, ensure_ascii=False))
        finally:
            page.remove_listener('response', handle_response)
