import json

import arrow
from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.icloud.items import LocationItem


class LocationSpider(RedisSpider):
    """
    icloud定位爬虫
    """
    name = 'location'

    custom_settings = {
        'ITEM_PIPELINES':            {
            'databox.icloud.pipelines.LocationPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES':    {
            'databox.icloud.middlewares.LocationCookiesMiddleware': 400,
            'databox.icloud.middlewares.ICloudLoginMiddleware':     500
        },
        'CONCURRENT_REQUESTS':       1,
        # icloud出现450，需要重跑 login_icloud
        'HTTPERROR_ALLOWED_CODES':   [450],
        # 2分钟1次
        'DOWNLOAD_DELAY':            120,
        'DOWNLOAD_FAIL_ON_DATALOSS': False
    }

    def __init__(self, username=None, password=None, *args, **kwargs):
        super(LocationSpider, self).__init__(*args, **kwargs)
        self.logger.info(f"username {username}, password {password}")
        self.username = username
        self.password = password

    def start_requests(self):
        headers = {
            'Origin': 'https://www.icloud.com'
        }
        url = 'https://p15-fmipweb.icloud.com/fmipservice/client/web/refreshClient'
        return [Request(url, method='POST', headers=headers, dont_filter=True)]

    def parse(self, response: Response):
        res = json.loads(response.text)
        if res['statusCode'] != '200':
            self.logger.error('error response')
            return response.request
        for device in res['content']:
            # 找到iphone
            if device['id'] == 'BotfTeR9f12Ls7V7V0tWLIZntjPwzmFQhtRbHHi2VBGmcXBPQQpaXOHYVNSUzmWV':
                item = LocationItem()
                item['longitude'] = device['location']['longitude']
                item['latitude'] = device['location']['latitude']
                item['created_at'] = arrow.now().datetime
                yield item
        yield response.request