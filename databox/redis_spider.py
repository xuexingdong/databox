from scrapy import version_info as scrapy_version
from scrapy_redis.spiders import RedisSpider as OldRedisSpider


class RedisSpider(OldRedisSpider):
    ## vvv _add this to spider code
    def schedule_next_requests(self):
        """Schedules a request if available"""
        # TODO: While there is capacity, schedule a batch of redis requests.
        for req in self.next_requests():
            # see https://github.com/scrapy/scrapy/issues/5994
            if scrapy_version >= (2, 6):
                self.crawler.engine.crawl(req)
            else:
                self.crawler.engine.crawl(req, spider=self)
