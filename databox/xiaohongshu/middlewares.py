import json

import httpx

from databox.xiaohongshu.utils import XiaohongshuUtil


class XiaohongshuHeaderMiddleware:
    """
    微博访客cookie获取
    """

    COOKIE_KEY = 'weibo:visit_cookies'

    RC4_SECRET_VERSION = '1'
    LOCAL_ID_KEY = 'a1'
    # 小红书拼写错误了
    MINI_BROSWER_INFO_KEY = 'b1'

    def __init__(self):
        self.client = httpx.AsyncClient(max_redirects=0)

    def process_request(self, request, spider):
        if 'X-S-COMMON' in request.headers:
            return
        XiaohongshuUtil.get_xiaohongshu_headers(request.url, json.loads(request.body))

    def httpx_cookie_to_scrapy_cookie(self, httpx_cookie):
        # Convert httpx Cookie to Scrapy cookie format
        scrapy_cookies = []
        for name, value in httpx_cookie.items():
            scrapy_cookies.append(f'{name}={value}')

        return '; '.join(scrapy_cookies)


class WeiboCookieMiddleware:
    def process_request(self, request, spider):
        spider.logger.info('weibo cookies')

        # https: // passport.weibo.com
        # 带上cookie
        request.headers.setdefault('Cookie',
                                   'SINAGLOBAL=6587733228028.543.1703397082379; _s_tentry=-; Apache=9536511089833.73.1704369758200; ULV=1704369758235:4:2:2:9536511089833.73.1704369758200:1704352022827; XSRF-TOKEN=i86b1h6hRiSQKChs-oNMDqUF; UOR=,,www.google.com; login_sid_t=8d2e28b5c188ad96688bac5706dd3945; cross_origin_proto=SSL; SUB=_2AkMSyyWvf8NxqwFRmfoWymvla4p0zAzEieKkl9R0JRMxHRl-yT9vqm1TtRB6OUsLQYmQ5H6TKHUEQW-J6Ddaqk7dlV_p; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9Wh8c8bpeD2OjQfCz2b-hhi1; WBPSESS=V0zdZ7jH8_6F0CA8c_ussZJzTWFlOwh0ij5L3VSJbifD0eXQj950NEhUlWWbgxRXJiN32pB7BRE33m422M3MDQq8CA-xhrQnUQ5qTTa8sSdIz5OsuFcuuWWlCrQ7VCy23ySELRLPL3gqbEOihpOubNSuGsX3manaywUDguvLhMs=; PC_TOKEN=091058df8f')


class WeiboLoginMiddleware:
    def process_response(self, request, response, spider):
        spider.logger.info('weibo login')
        return response
