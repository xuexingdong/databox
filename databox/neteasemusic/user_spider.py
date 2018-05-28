import json

from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.neteasemusic import utils, apis


class NeteaseMusicUserSpider(RedisSpider):
    name = 'netease_music_user'
    redis_key = "databox:" + name

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.neteasemusic.pipelines.UserPipeline': 300,
        },
    }

    def start_requests(self):
        id = 273745272
        return [Request(url='http://music.163.com/user/home?id=' + str(id), meta={
            'id': id,
        }, dont_filter=True)]

    def make_request_from_data(self, data):
        id = bytes_to_str(data, self.redis_encoding)
        return Request(url=apis.get_user_url(id), meta={'id': id})

    def parse(self, response: HtmlResponse):
        item = {}
        item['id'] = response.meta['id']
        item['nickname'] = response.css('::text').re_first('nickname:"(.*?)"')
        item['event_count'] = int(response.css('#event_count::text').extract_first(default=0))
        item['follow_count'] = int(response.css('#follow_count::text').extract_first(default=0))
        item['fan_count'] = int(response.css('#fan_count::text').extract_first(default=0))
        head_box = response.css('#head-box')[0]
        item['description'] = head_box.re_first('<div class="inf s-fc3 f-brk">个人介绍：(.*?)</div>')
        item['address'] = head_box.re_first('<span>所在地区：(.*?)</span>')
        yield item
        # 关注列表信息
        if item['follow_count'] > 0:
            data = {
                'userId':     response.meta['id'],
                'total':      True,
                'limit':      100,
                'offset':     0,
                'csrf_token': ''
            }
            self.server.rpush('databox:netease_music_follow',
                              json.dumps({
                                  'meta': data,
                                  'data': utils.encrypted_request(data)
                              }))

        # 粉丝列表信息
        if item['fan_count'] > 0:
            data = {
                'userId':     response.meta['id'],
                'total':      True,
                'limit':      100,
                'offset':     0,
                'csrf_token': ''
            }
            self.server.rpush('databox:netease_music_followed',
                              json.dumps({
                                  'meta': data,
                                  'data': utils.encrypted_request(data)
                              }))
