import json
from typing import Iterable, Any

from scrapy import Request
from scrapy.http import TextResponse
from scrapy_redis.spiders import RedisSpider

from databox.weibo import constants
from databox.weibo.comment_spider import WeiboCommentSpider
from databox.weibo.items import MBlogItem


class WeiboMBlogSpider(RedisSpider):
    name = 'weibo:mblog'
    collection = 'weibo_mblog'
    redis_key = name
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'DOWNLOADER_MIDDLEWARES': {
            'databox.weibo.middlewares.WeiboVisitorCookieMiddleware': 501
        },
        'ITEM_PIPELINES': {
            'databox.weibo.pipelines.MBlogPipeline': 800,
        }
    }

    def __init__(self, *args, uid=None, with_comment=False, **kwargs):
        super().__init__(**kwargs)
        self.uid = uid
        self.with_comment = with_comment
        self.page = 1

    def start_requests(self) -> Iterable[Request]:
        mymblog_url = self._get_mymblog_url(self.uid, self.page)
        yield Request(mymblog_url, dont_filter=True)

    def parse(self, response: TextResponse, **kwargs: Any) -> Any:
        res = response.json()
        self.logger.info(f'res: {res}')
        if res['ok'] != 1:
            self.logger.error('报错了')
            return
        if 'data' not in res:
            self.logger.warning('未登录只能看这么多微博了')
            return
        if not res['data']['list']:
            return
        for mblog in res['data']['list']:
            mblog_item = MBlogItem()
            mblog_item['id'] = mblog['id']
            mblog_item['uid'] = self.uid
            mblog_item['content'] = mblog
            yield mblog_item
        since_id = res['data']['since_id']
        self.page += 1
        next_page_url = self._get_mymblog_url(self.uid, self.page, since_id=since_id)
        self.logger.info(next_page_url)
        self.server.rpush(self.redis_key, json.dumps({
            'url': next_page_url,
            'meta': {
                'dont_filter': True
            }}))
        if self.with_comment:
            self.server.rpush(WeiboCommentSpider.redis_key,
                              *[json.dumps(self._get_comment_redis_data(x)) for x in res['data']['list']])

    @staticmethod
    def _get_mymblog_url(uid, page, feature=0, since_id=None):
        """
        :param uid:
        :param page:
        :param feature: 规则尚不清楚
        :param since_id:
        :return:
        """
        return f'{constants.PREFIX}/statuses/mymblog?uid={uid}&page={page}&feature={feature}&since_id={since_id}'

    def _get_comment_redis_data(self, mblog):
        return {
            'url': WeiboCommentSpider.get_comments_url(id=mblog['id'], uid=self.uid),
            'meta': {
                'dont_filter': True
            }
        }
