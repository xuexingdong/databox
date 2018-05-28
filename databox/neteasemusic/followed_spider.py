import json

from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.neteasemusic import apis, utils


class NeteaseMusicFollowedSpider(RedisSpider):
    """
    粉丝列表爬虫
    """
    name = 'netease_music_followed'
    redis_key = "databox:" + name

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
                'total':  False,
                'limit':  response.meta['limit'],
                'offset': response.meta['offset'] + 100,
            }
            yield FormRequest(url=apis.get_followeds_url(response.meta['userId']), formdata={
                'meta': data,
                'data': utils.encrypted_request(data)
            })
        self.server.rpush('databox:netease_music_user',
                          *[followed['userId'] for followed in res['followeds']])
