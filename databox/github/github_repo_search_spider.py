import json
from typing import Any
from urllib.parse import urlparse, parse_qs

import arrow
import scrapy
from pydantic import BaseModel
from scrapy_redis.spiders import RedisSpider

from databox.github.github_repo_spider import GithubRepoSpider


class GithubRepoSearchMeta(BaseModel):
    q: str
    p: int = 1
    updated_after: str = arrow.now().shift(days=-1).floor('day').format("YYYY-MM-DD HH:mm:ss")
    latest_updated_at: str | None = None

    def reset(self):
        self.p = 1
        self.updated_after = self.latest_updated_at


class GithubRepoSearchSpider(RedisSpider):
    name = 'github_repo_search'
    redis_key = "databox:" + name
    redis_batch_size = 1
    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'DOWNLOAD_DELAY': 45,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json',
            'Referer': 'https://github.com/'
        }
    }

    def make_request_from_data(self, data):
        meta = GithubRepoSearchMeta.model_validate_json(data)
        self.logger.info(meta)
        url = self.gen_search_url(meta.q, meta.p)
        yield scrapy.Request(url,
                             meta=meta.model_dump(),
                             dont_filter=True
                             )

    def parse(self, response, **kwargs: Any) -> Any:
        repos = response.jmespath('payload.results[].repo.repository').getall()
        if not repos:
            self.logger.error("empty page result")
            return
        meta = GithubRepoSearchMeta.model_validate(response.meta)
        updated_after = arrow.get(meta.updated_after)
        should_stop = False
        if meta.latest_updated_at is None or arrow.get(repos[0]['updated_at']) > arrow.get(meta.latest_updated_at):
            meta.latest_updated_at = repos[0]['updated_at']
        for repo in repos:
            repo_updated_time = arrow.get(repo['updated_at'])
            if repo_updated_time < updated_after:
                should_stop = True
                continue
            repo_url = f'https://github.com/{repo["owner_login"]}/{repo["name"]}'
            self.server.rpush(GithubRepoSpider.redis_key, json.dumps({
                'url': repo_url,
                'meta': {
                    'dont_filter': True,
                }
            }))
        if not should_stop and meta.p < 100:
            meta.p += 1
            self.server.set(f"{self.redis_key}:meta:{meta.q}", meta.model_dump_json(exclude_none=True))
            self.server.rpush(
                self.redis_key,
                meta.model_dump_json(exclude_none=True)
            )
        else:
            self.logger.info("reached time boundary, stop crawling")
            meta.reset()
            self.server.set(f"{self.redis_key}:meta:{meta.q}", meta.model_dump_json(exclude_none=True))

    @staticmethod
    def get_page_number(url: str):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return int(query_params.get('p', [1])[0])

    @staticmethod
    def gen_search_url(q: str, p: int):
        return f"https://github.com/search?q={q}&type=repositories&s=updated&o=desc&p={p}"
