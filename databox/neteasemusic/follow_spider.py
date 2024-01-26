import json

from scrapy import FormRequest
from databox.redis_spider import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.neteasemusic import apis, utils
from databox.neteasemusic.items import FollowItem


class NeteaseMusicFollowSpider(RedisSpider):
    """
    关注人列表爬虫
    """
    name = 'netease_music_follow'
    redis_key = "databox:" + name

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.neteasemusic.pipelines.FollowPipeline': 300,
        },
    }

    def make_request_from_data(self, data):
        res = json.loads(bytes_to_str(data, self.redis_encoding))
        meta = res['meta']
        return FormRequest(url=apis.get_follows_url(meta['userId']), formdata=res['data'], meta=meta)

    def parse(self, response):
        if not response.text:
            self.logger.warning('response is empty')
            return
        res = json.loads(response.text)
        if res['code'] != 200:
            self.logger.warning('error: ' + response.text)
            return
        if res['more']:
            data = {
                'userId': response.meta['userId'],
                'total':  'false',
                'limit':  response.meta['limit'],
                'offset': response.meta['offset'] + 100,
            }
            yield FormRequest(url=apis.get_follows_url(response.meta['userId']), formdata={
                'meta': data,
                'data': utils.encrypted_request(data)
            })
        follow_ids = [follow['userId'] for follow in res['follow']]
        for follow_id in follow_ids:
            item = FollowItem()
            item['id1'] = response.meta['userId']
            item['id2'] = follow_id
            yield item

        self.server.rpush('databox:netease_music_user',
                          *follow_ids)
