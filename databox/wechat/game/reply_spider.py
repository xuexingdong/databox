import copy
import json

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.wechat.game.items import ReplyItem
from databox.wechat.game.utils import get_reply_url_data, get_game_reply_list_url, is_timestamp_outdated


class ReplySpider(RedisSpider):
    """
    帖子回复
    """
    name = 'reply'
    redis_key = 'databox:reply'

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.wechat.game.pipelines.ReplyPipeline': 300
        }
    }

    def __init__(self, session_id=None, *args, **kwargs):
        if not session_id:
            raise ValueError
        super(ReplySpider, self).__init__(*args, **kwargs)
        self.session_id = session_id

    def make_request_from_data(self, data):
        data = json.loads(data)
        if 'count' not in data:
            # 默认每页100
            data['count'] = 100
        if 'offset' not in data:
            data['offset'] = 0
        if 'parent_reply_id' not in data:
            data['parent_reply_id'] = None
        body = get_reply_url_data(data['appid'],
                                  data['topic_id'],
                                  data['parent_reply_id'],
                                  data['count'],
                                  data['offset'])
        headers = {
            'Content-Type': 'application/json'
        }
        return Request(get_game_reply_list_url(self.session_id), method='POST', headers=headers,
                       body=json.dumps(body), meta=data)

    def parse(self, response: Response):
        res = json.loads(response.text)
        if res['errcode'] != 0:
            self.logger.error(res['errmsg'])
            return
        meta = response.meta
        # 倒序索引回复
        for reply in reversed(res['reply_list']['reply_list']):
            ts = reply['base']['create_time']
            if is_timestamp_outdated(ts):
                self.logger.warning(
                    f"reply {reply['base']['content']} in topic {reply['base']['topic_id']} timestamp {ts} is outdated")
                break
            reply_item = ReplyItem()
            reply_item['reply_id'] = reply['base']['reply_id']
            reply_item['topic_id'] = reply['base']['topic_id']
            reply_item['pic_urls'] = reply['base']['pic_url_list']
            yield reply_item
            # 有子回复
            if 'child_reply' in reply:
                for _ in reply['child_reply']['reply_list']:
                    tmp_meta = copy.deepcopy(meta)
                    del tmp_meta['count']
                    del tmp_meta['offset']
                    body = get_reply_url_data(tmp_meta['appid'], tmp_meta['topic_id'],
                                              parent_reply_id=reply['base']['reply_id'])
                    yield Request(get_game_reply_list_url(self.session_id), method='POST',
                                  headers=response.request.headers,
                                  body=json.dumps(body), meta=meta)

        # 判断是否还有下一页
        if res['reply_list']['has_next']:
            # 修改游标
            meta['offset'] += meta['count']
            body = get_reply_url_data(meta['appid'], meta['topic_id'], None, meta['count'], meta['offset'])
            yield Request(get_game_reply_list_url(self.session_id), method='POST', headers=response.request.headers,
                          body=json.dumps(body), meta=meta)
