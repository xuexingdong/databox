import json
from typing import Any
from urllib.parse import parse_qs, urlparse

from scrapy.http import TextResponse
from scrapy_redis.spiders import RedisSpider
from databox.weibo.constants import PREFIX
from databox.weibo.enums import CommentFlow

from databox.weibo.items import CommentItem


class WeiboCommentSpider(RedisSpider):
    name = 'weibo:comment'
    collection = 'weibo_comment'
    redis_key = name
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'databox.weibo.middlewares.WeiboVisitorCookieMiddleware': 501
        },
        'ITEM_PIPELINES': {
            'databox.weibo.pipelines.CommentPipeline': 800,
        }
    }

    def parse(self, response: TextResponse, **kwargs: Any) -> Any:
        res = response.json()
        if res['ok'] != 1:
            self.logger.error('报错了')
            return
        if not res['data']:
            self.logger.info('没有评论')
            return
        for comment_data in res['data']:
            comment_item = CommentItem()
            comment_item['id'] = comment_data['id']
            comment_item['uid'] = comment_data['id']
            comment_item['content'] = comment_data
            yield comment_item
        params = parse_qs(urlparse(response.request.url).query)
        values = params.get('id', [])
        max_id = res['max_id']
        # 0说明已经结束了，再开始会死循环
        if max_id == 0:
            return
        next_page_url = self.get_comments_url(id=values[0] if values else None, max_id=max_id)
        self.logger.info(next_page_url)
        self.server.rpush(self.redis_key, json.dumps({
            'url': next_page_url,
            'meta': {
                'dont_filter': True
            }
        }))

    @staticmethod
    def get_comments_url(flow=CommentFlow.redu, is_reload=1, id=None, is_show_bulletin=2, is_mix=0, max_id=0, count=20,
                         type='feed', uid=None, fetch_level=0, locale='zh-CN'):
        """

        :param flow: 详见评论接口返回的filter_group字段
        :param is_reload:
        :param id: fetch_level = 0时，这个id是mblog的id；fetch_level = 1时，这个id是评论的id
        :param is_show_bulletin:
        :param is_mix:
        :param max_id:
        :param count:
        :param type: feed表示是在feed流过程中展开的，而不是【查看全部评论】点开的
        :param uid:
        :param fetch_level: 评论等级，默认是0，评论的评论是1
        :param locale:
        :return:
        """
        return f'{PREFIX}/statuses/buildComments?flow={flow.value}&is_reload={is_reload}&id={id}&is_show_bulletin={is_show_bulletin}&is_mix={is_mix}&max_id={max_id}&count={count}&type={type}&uid={uid}&fetch_level={fetch_level}&locale={locale}'
