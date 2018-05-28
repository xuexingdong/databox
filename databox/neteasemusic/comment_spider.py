from scrapy import Request
from scrapy.http import HtmlResponse
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.utils import bytes_to_str

from databox.neteasemusic import apis


class NeteaseMusicCommentSpider(RedisSpider):
    name = 'netease_music_comment'
    redis_key = "databox:" + name

    def make_request_from_data(self, data):
        song_id = bytes_to_str(data, self.redis_encoding)
        return Request(url=apis.get_comment_url(song_id))

    def parse(self, response: HtmlResponse):
        item = {}
        item['nickname'] = response.text.re_first('nickname:".*?"')
        item['event_count'] = response.css('#event_count::text').extract_first()
        item['follow_count'] = response.css('#follow_count::text').extract_first()
        item['fan_count'] = response.css('#fan_count::text').extract_first()
        print(item)
