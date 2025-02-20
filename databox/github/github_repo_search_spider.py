import json
from typing import Any
from urllib.parse import urlparse, parse_qs

import arrow
import scrapy
from scrapy_redis.spiders import RedisSpider

from databox.github.github_repo_spider import GithubRepoSpider


class GithubRepoSearchSpider(RedisSpider):
    name = 'github_repo_search'
    redis_key = "databox:" + name
    custom_settings = {
        'MAX_IDLE_TIME_BEFORE_CLOSE': 60 * 5,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_DELAY': 60,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [429],
    }

    def __init__(self, q=None, p=1, updated_after=None, *args, **kwargs):
        """

        :param q:
        :param p:
        :param updated_after
        :param args:
        :param kwargs:
        """
        super(GithubRepoSearchSpider, self).__init__(*args, **kwargs)
        self.q = q
        self.p = int(p)

        if updated_after is None:
            updated_after = arrow.now().shift(days=-1).format("YYYY-MM-DD")
        self.updated_after = arrow.get(updated_after, "YYYY-MM-DD")

    def start_requests(self):
        url = self.gen_search_url(self.q, self.p)
        self.logger.info(url)
        headers = {
            'Accept': 'application/json',
            'Referer': 'https://github.com/'
        }
        yield scrapy.Request(url, headers=headers, dont_filter=True)

    def parse(self, response, **kwargs: Any) -> Any:
        repos = response.jmespath('payload.results[].repo.repository').getall()
        if not repos:
            self.logger.error("all finish")
            return
        for repo in repos:
            if arrow.get(repo['updated_at']) < self.updated_after:
                self.logger.info('find repo updated at %s, finish', repo['updated_at'])
                return
            repo_url = f'https://github.com/{repo["owner_login"]}/{repo["name"]}'
            self.server.rpush(GithubRepoSpider.redis_key, json.dumps({
                'url': repo_url
            }))
        p = int(response.jmespath('payload.page').get())
        url = self.gen_search_url(self.q, p + 1)
        self.logger.info(url)
        # 提取查询参数部分
        yield response.request.replace(url=url)

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
        return f"https://github.com/search?q={q}&type=repositories&s=updated&o=desc&p={p}"
