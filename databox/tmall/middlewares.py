import json


class TmallCookiesMiddleware:
    def process_request(self, request, spider):
        # 带上cookie
        cookie = spider.server.get('databox:cookies:tmall')
        if cookie:
            request.cookies = json.loads(cookie)
