import json
import re

import time
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from databox.wechat.weixin import Wechat


class WechatSpider(RedisSpider):
    name = 'wechat'

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.petchain.pipelines.PetPipeline': 300,
        },
        'COOKIES_ENABLED': False,
        'CONCURRENT_REQUESTS': 64,
        'RETRY_TIMES': 10
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wechat = Wechat()
        self.logger.info('共有 %d 个直接联系人 | %d 个群 | %d 个公众号或服务号 ｜ %d 个特殊账号',
                         len(self.wechat.contacts),
                         len(self.wechat.group_contacts),
                         len(self.wechat.media_platforms),
                         len(self.wechat.special_users)
                         )

    def start_requests(self):
        return [self.sync_request()]

    def parse(self, response):
        msg = self.wechat.handle(json.loads(response.text))
        time.sleep(1)
        yield self.sync_request()

    def sync_request(self):
        data = {
            'BaseRequest': self.wechat.base_request,
            'SyncKey': self.wechat.sync_key_list,
            'rr': ~int(time.time())
        }
        return Request(self.wechat.get_sync_url(), method='POST', body=json.dumps(data),
                       cookies=self.wechat.session.cookies)
