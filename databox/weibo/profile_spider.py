from typing import Iterable, Any

from scrapy import Request
from scrapy.http import TextResponse
from scrapy_redis.spiders import RedisSpider

from databox.weibo import constants
from databox.weibo.items import Profile


class WeiboProfileSpider(RedisSpider):
    name = 'weibo:profile'
    collection = 'weibo_profile'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 优先级需要大于500，因为内置的ua插件优先级为500
            'databox.weibo.middlewares.WeiboVisitorCookieMiddleware': 501
        },
        'ITEM_PIPELINES': {
            'databox.weibo.pipelines.ProfilePipeline': 800,
        }
    }

    def __init__(self, uid=None, *args, **kwargs):
        super(WeiboProfileSpider, self).__init__(*args, **kwargs)
        self.uid = uid

    def start_requests(self) -> Iterable[Request]:
        profile_info_url = self._get_profile_info_url(self.uid)
        yield Request(profile_info_url, dont_filter=True)

        # profile_detail_url = self._get_profile_detail_url(self.uid)
        # yield Request(profile_detail_url, dont_filter=True)

    def parse(self, response: TextResponse, **kwargs: Any) -> Any:
        res = response.json()
        if res['ok'] != 1:
            self.logger.error('报错了')
            return
        user = res['data']['user']
        profile = Profile()
        profile['id'] = user['id']
        profile['content'] = user
        yield profile

    @staticmethod
    def _get_profile_info_url(uid):
        """
         有时候url是custom = {uid}，规则尚不清楚
        :param uid:
        :return:
        """
        return f'{constants.PREFIX}/profile/info?uid={uid}'

    @staticmethod
    def _get_profile_detail_url(uid):
        return f'{constants.PREFIX}/profile/detail?uid={uid}'
