import json
import re
import time
from urllib.parse import quote, urlparse

import httpx
from scrapy import Request

from databox.weibo.middlewares import WeiboVisitorCookieMiddleware


class AlipayCookieMiddleware:
    """
    微博访客cookie获取
    """

    COOKIE_KEY = 'alipay:cookies'

    def __init__(self):
        self.client = httpx.Client(max_redirects=0)

    def process_request(self, request, spider):
        if request.cookies:
            return
            # visitor的路径直接访问
        if 'visitor' in request.url:
            return
        parsed_url = urlparse(request.url)
        if 'ajax' not in parsed_url.path:
            return
        if spider.server.get(WeiboVisitorCookieMiddleware.COOKIE_KEY):
            cookies = json.loads(spider.server.get(WeiboVisitorCookieMiddleware.COOKIE_KEY))
            spider.logger.info('exist cookies')
        else:
            spider.logger.info('get weibo visitor cookies')
            quoted_url = quote(request.url, safe="")
            passport_url = f'https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url={quoted_url}&domain=weibo.com&ua={quote(request.headers["User-Agent"], safe="")}&_rand={int(time.time() * 1000)}&sudaref='
            headers = {
                'Origin': 'https://passport.weibo.com',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': passport_url
            }
            spider.logger.info(f'passport_url: {passport_url}')
            response = self.client.post('https://passport.weibo.com/visitor/genvisitor', data={
                'cb': 'gen_callback'
            })
            match = re.search(r'\((.*)\)', response.text)
            data = json.loads(match.group(1))['data']
            tid = data['tid']
            response = self.client.post('https://passport.weibo.com/visitor/genvisitor2', headers=headers,
                                        data={
                                            'cb': 'visitor_gray_callback',
                                            'tid': tid,
                                            'from': 'weibo'
                                        })
            match = re.search(r'\((.*)\)', response.text)
            data = json.loads(match.group(1))['data']
            sub = data['sub']
            subp = data['subp']
            cookies = {
                'SUB': sub,
                'SUBP': subp
            }
            spider.server.set(WeiboVisitorCookieMiddleware.COOKIE_KEY, json.dumps(cookies))
            spider.logger.info(f'save cookies : {cookies}')
            # f'https://login.sina.com.cn/visitor/visitor?a=crossdomain&s={s}&sp={sp}&url={quoted_url}'
        # 替换请求链接，这个链接最后会重定向到所要访问的链接
        return Request(url=request.url, cookies=cookies, dont_filter=True)

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
