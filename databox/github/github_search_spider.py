import json
from typing import Any
from urllib.parse import urlparse, parse_qs

import scrapy
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.github.github_repo_spider import GithubRepoSpider


class GithubSearchSpider(RedisSpider):
    name = 'github_search'
    redis_key = "databox:" + name
    custom_settings = {
        'MAX_IDLE_TIME_BEFORE_CLOSE': 120,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_DELAY': 5,
    }

    def __init__(self, q=None, p=1, match_words=None, *args, **kwargs):
        super(GithubSearchSpider, self).__init__(*args, **kwargs)
        self.q = q
        self.p = p
        self.match_words = match_words

    def start_requests(self):
        yield scrapy.Request(url=self.gen_search_url(self.q, self.p), dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        self.logger.info(response.url)
        results = response.css('div[data-testid=results-list] > div')
        if not results:
            self.logger.error("all finish")
            return
        for result in results:
            repo_url = response.urljoin(result.css('div.search-title > a::attr(href)').get())
            self.server.rpush(GithubRepoSpider.redis_key, json.dumps({
                'url': repo_url
            }))
        p = self.get_page_number(response.url)
        parsed_url = self.gen_search_url(self.q, p + 1)
        # 提取查询参数部分
        yield response.request.replace(url=parsed_url)

    @staticmethod
    def get_page_number(url):
        # 解析 URL
        parsed_url = urlparse(url)
        # 解析查询参数为字典
        query_params = parse_qs(parsed_url.query)
        # 获取当前的 `p` 参数值，如果没有则默认为 1
        return int(query_params.get('p', [1])[0])

    @staticmethod
    def gen_search_url(q, p=1):
        return f"https://github.com/search?q={q}&type=repositories&p={p}"
