from scrapy_redis.spiders import RedisCrawlSpider


class MeituanShopCrawler(RedisCrawlSpider):
    def process_results(self, response, results):
        return super().process_results(response, results)

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        item = scrapy.Item()
        item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        return item