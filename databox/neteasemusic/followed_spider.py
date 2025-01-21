import json

from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.neteasemusic import apis, utils
from databox.neteasemusic.items import FollowItem


class NeteaseMusicFollowedSpider(RedisSpider):
    """
    粉丝列表爬虫
    """
    name = 'netease_music_followed'
    redis_key = "databox:" + name

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.neteasemusic.pipelines.FollowPipeline': 300,
        },
    }

    def make_request_from_data(self, data):
        res = json.loads(bytes_to_str(data, self.redis_encoding))
        meta = res['meta']
        return FormRequest(url=apis.get_followeds_url(meta['userId']), formdata=res['data'], meta=meta)

    def parse(self, response):
        if not response.text:
            self.logger.warning('response is empty')
            return
        res = json.loads(response.text)
        if res['code'] != 200:
            return
        if res['more']:
            data = {
                'userId': response.meta['userId'],
                'total':  'false',
                'limit':  response.meta['limit'],
                'offset': response.meta['offset'] + 100,
            }
            yield FormRequest(url=apis.get_followeds_url(response.meta['userId']), formdata={
                'meta': data,
                'data': utils.encrypted_request(data)
            })
        followed_ids = [followed['userId'] for followed in res['followeds']]
        for followed_id in followed_ids:
            item = FollowItem()
            item['id1'] = followed_id
            item['id2'] = response.meta['userId']
            yield item

        self.server.rpush('databox:netease_music_user',
                          *followed_ids)
