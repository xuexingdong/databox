import json
import pickle
from urllib.parse import urlencode

from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.tmall.item_loaders import TmallRateLoader
from databox.tmall.items import TmallRateItem


class TmallRateSpider(RedisSpider):
    name = 'tmall_rate'

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.tmall.pipelines.TmallRatePipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'databox.tmall.middlewares.CookiesMiddleware': 400
        },
        'CONCURRENT_REQUESTS': 64,
        'RETRY_TIMES': 10
    }

    def make_request_from_data(self, data):
        return pickle.loads(data)

    def parse(self, response: Response):
        res = json.loads('{' + response.text + '}')
        current_page = response.meta['page']
        self.logger.info('第%d页评论数据' % current_page)
        paginator = res['paginator']
        # 还未到最后一页
        if current_page < paginator['lastPage']:
            next_request = response.request
            next_request.meta['query']['currentPage'] = current_page + 1
            next_request.url = next_request.meta['url'] + urlencode(next_request.meta['query'])
            # 商品详情
            yield next_request
        for rate in res['rateList']:
            l = TmallRateLoader(item=TmallRateItem())
            l.add_value('create_time', rate['rateDate'])
            l.add_value('content', rate['rateContent'])
            yield l.load_item()
