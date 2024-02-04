import json

import qrcode

from databox.xiaohongshu.xhs_client import XhsClient


class XiaohongshuHeaderMiddleware:
    COOKIE_KEY = 'xhs:visit_cookies'

    RC4_SECRET_VERSION = '1'
    LOCAL_ID_KEY = 'a1'
    # 小红书拼写错误了
    MINI_BROSWER_INFO_KEY = 'b1'

    def __init__(self):
        self.xhs_client = XhsClient()

    def process_request(self, request, spider):
        if 'X-S-Common' in request.headers:
            return
        if hasattr(spider, 'need_login') and spider.need_login:
            if not self.xhs_client.check_login():
                qr_code = self.xhs_client.create_qr_code()
                qr = qrcode.QRCode()
                qr.add_data(qr_code.url)
                qr.make(fit=True)
                qr.print_ascii(invert=True)
                if self.xhs_client.wait_until_login(qr_code):
                    cookies = self.xhs_client.get_cookie_dict()
                    request.headers.update(cookies)
        new_body = self.xhs_client.handle_post_data(json.loads(request.body))
        xhs_headers = self.xhs_client.get_xhs_headers(request.url, json.loads(new_body))
        new_headers = request.headers | xhs_headers
        return request.replace(headers=new_headers, body=new_body, cookies=self.xhs_client.get_cookie_dict())

    def process_response(self, request, response, spider):
        if response.status == 588:
            spider.logger.info(response.text)
            return
        if response.status == 461:
            params = {
                'redirectPath': response.url,
                'callFrom': 'web',
                'biz': 'sns_web',
                'verifyUuid': response.headers['verifyUuid'],
                'verifyType': response.headers['verifyType'],
                'verifyBiz': response.status
            }
            self.xhs_client.auto_rotate_captcha(params)
            spider.logger.info(params)
            # https://fe-static.xhscdn.com/formula-static/login/public/js/main.8cee1b6.js
            return
