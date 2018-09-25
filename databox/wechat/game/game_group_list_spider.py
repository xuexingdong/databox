import json

from scrapy import Spider
from scrapy_redis import connection

from databox.wechat.game.game_group_spider import GameGroupSpider
from databox.wechat.game.utils import get_game_group_list_url


class GameGroupListSpider(Spider):
    """
    游戏圈列表
    """
    name = 'game_group_list'

    def __init__(self, session_id=None, *args, **kwargs):
        if not session_id:
            raise ValueError
        super(GameGroupListSpider, self).__init__(*args, **kwargs)
        self.session_id = session_id
        self.start_urls = [get_game_group_list_url(self.session_id)]

    def parse(self, response):
        res = json.loads(response.text)
        if res['errcode'] != 0:
            self.logger.error(res['errmsg'])
            return

        # 推荐的圈子，所有圈子用letter_group_list，按字母检索
        for recom_group in res['recom_group_list']:
            # 王者荣耀，绝地求生
            if recom_group['group_id'] in {3001395649, 3524390065}:
                appid = recom_group['game_info']['app_id']
                self.conn.rpush(GameGroupSpider.redis_key, json.dumps({
                    'appid': appid
                }))

    def init_conn(self, conn):
        self.conn = conn
        self.conn.delete(GameGroupSpider.redis_key)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        obj = super(GameGroupListSpider, cls).from_crawler(crawler, *args, **kwargs)
        conn = connection.from_settings(crawler.settings)
        obj.init_conn(conn)
        return obj
