import json

from scrapy.exceptions import IgnoreRequest

from databox.icloud.icloud_system import ICloudSystem


class LocationCookiesMiddleware:
    def process_request(self, request, spider):
        # 带上cookie
        cookie = spider.server.get('databox:icloud:cookies')
        if cookie:
            request.cookies = json.loads(cookie)


class ICloudLoginMiddleware:
    def process_response(self, request, response, spider):
        if response.status == 450:
            driver_path = spider.settings.get('CHROME_DRIVER_PATH')
            # 有账号密码，则直接登录，否则挂机
            username = spider.username
            password = spider.password
            if username and password:
                icloud = ICloudSystem(driver_path)
                try:
                    icloud.login(username, password)
                except Exception as e:
                    spider.logger.warning('icloud selenium error', e)
                    icloud.close()
                    return request
                cookies = icloud.get_cookies()
                icloud.close()
                spider.server.set('databox:icloud:cookies', json.dumps(cookies))
                return request
            raise IgnoreRequest
        return response
