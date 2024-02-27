import json


class TiktokCookieMiddleWare:
    COOKIE_KEY = 'tiktok:cookie'

    def process_request(self, request, spider):
        cookies = json.loads(spider.server.get(self.COOKIE_KEY))
        request.cookies = cookies
