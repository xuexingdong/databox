import json

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.wechat.game.items import TopicItem
from databox.wechat.game.reply_spider import ReplySpider
from databox.wechat.game.utils import get_game_group_url, get_game_group_url_data, is_timestamp_outdated


class GameGroupSpider(RedisSpider):
    """
    游戏圈
    """
    name = 'game_group'
    redis_key = 'databox:game_group'

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.wechat.game.pipelines.TopicPipeline': 300
        }
    }

    def __init__(self, session_id=None, *args, **kwargs):
        if not session_id:
            raise ValueError
        super(GameGroupSpider, self).__init__(*args, **kwargs)
        self.session_id = session_id

    def make_request_from_data(self, data):
        data = json.loads(data)
        # 默认值填充
        if 'count' not in data:
            data['count'] = 15
        if 'offset' not in data:
            data['offset'] = 0
        body = get_game_group_url_data(data['appid'], data['count'], data['offset'])
        headers = {
            'Content-Type': 'application/json'
        }
        return Request(get_game_group_url(self.session_id), method='POST', headers=headers,
                       body=json.dumps(body), meta=data)

    def parse(self, response: Response):
        res = json.loads(response.text)
        if res['errcode'] != 0:
            self.logger.error(res['errmsg'])
            return

        meta = response.meta
        # TODO GroupItem
        for topic in res['topic_list']['topic_list']:
            # 如果没人回复，最后回复时间是0
            ts = topic['base']['last_reply_time'] if topic['base']['last_reply_time'] != 0 \
                else topic['base']['create_time']
            if is_timestamp_outdated(ts):
                self.logger.warning(f"topic {topic['base']['title']} timestamp {ts} is outdated")
                return
            topic_item = TopicItem()
            topic_item['topic_id'] = topic['base']['topic_id']
            topic_item['pic_urls'] = topic['base']['preview_pic_url_list']
            yield topic_item
            self.server.rpush(ReplySpider.redis_key, json.dumps({
                'appid':    meta['appid'],
                'topic_id': topic['base']['topic_id']
            }))
        # 判断是否还有下一页
        if res['topic_list']['has_next']:
            # 修改游标
            meta['offset'] += meta['count']
            body = get_game_group_url_data(meta['appid'], meta['count'], meta['offset'])
            yield Request(get_game_group_url(self.session_id), method='POST', headers=response.request.headers,
                          body=json.dumps(body), meta=meta)
