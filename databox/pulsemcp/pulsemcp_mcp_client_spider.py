import json
from typing import Any

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.github.github_repo_spider import GithubRepoSpider


class PulseMcpMcpClientSpider(RedisSpider):
    name = 'pulse_mcp_mcp_client'
    redis_key = "databox:" + name

    def make_request_from_data(self, data):
        yield Request(url='https://www.pulsemcp.com/clients', dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        clients = response.css('div.grid > a::attr(href)').getall()
        for client in clients:
            yield Request(url=response.url + client[8:], callback=self.parse_client, dont_filter=True)

    def parse_client(self, response: Response, **kwargs: Any) -> Any:
        repo_url = response.css('[data-test-id="mcp-client-github-repo"]::attr(href)').get()
        if repo_url is None:
            return
        self.server.rpush(GithubRepoSpider.redis_key, json.dumps({
            'url': repo_url,
            'meta': {
                'type': 'client'
            }
        }))
