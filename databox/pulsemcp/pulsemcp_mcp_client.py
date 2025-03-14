import json
from typing import Any

from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider

from databox.github.github_repo_spider import GithubRepoSpider


class PulseMcpMcpClient(RedisSpider):
    name = 'pulse_mcp_mcp_client'
    redis_key = "databox:" + name
    max_idle_time = 60

    def start_requests(self):
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


def run_spiders():
    process = CrawlerProcess(get_project_settings())
    process.crawl(PulseMcpMcpClient)
    process.start()


if __name__ == "__main__":
    run_spiders()
