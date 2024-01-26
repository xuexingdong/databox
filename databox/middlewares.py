import json

from redis import StrictRedis
from scrapy import Request
from scrapy_redis import get_redis
from databox.redis_spider import RedisSpider


class CookieMiddleware:
    def __init__(self, r: StrictRedis):
        self.r = r

    @classmethod
    def from_crawler(cls, crawler):
        r: StrictRedis = get_redis()
        return cls(r)

    def process_request(self, request: Request, spider: RedisSpider):
        # 带上cookie
        request.cookies = json.loads(self.r.lindex('cookies_pool:' + spider.name, 0))

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
