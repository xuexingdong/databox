import json

from scrapy.exceptions import IgnoreRequest

from databox.icloud.icloud_system import ICloudSystem


class LocationCookiesMiddleware:
    def process_request(self, request, spider):
        # 带上cookie
        cookies = spider.server.get('databox:icloud:cookies')
        if cookies:
            request.cookies = json.loads(cookies)


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
                except Exception as _:
                    spider.logger.warning('icloud selenium error')
                    icloud.close()
                    return request
                cookies = icloud.get_cookies()
                icloud.close()
                spider.server.set('databox:icloud:cookies', json.dumps(cookies))
                return request
            raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.error('spider raise an error', exc_info=True)
        return request
