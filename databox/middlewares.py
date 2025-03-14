from urllib.parse import urlparse

from scrapy import Request, Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.http import Response
from typing_extensions import Self


class DomainCookieMiddleware:
    COOKIES = {
        # TODO
        'www.instagram.com': ''
    }

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        if not crawler.settings.getbool("DOMAIN_COOKIE_ENABLED"):
            raise NotConfigured
        return cls()

    def process_request(
            self, request: Request, spider: Spider
    ) -> Request | Response | None:
        domain = urlparse(request.url).netloc
        cookies = self.get_domain_cookies(domain)
        if cookies:
            pass
            request.cookies.update(cookies)

    def get_domain_cookies(self, domain: str) -> dict:
        # TODO 后期增加动态获取
        """设置指定域名的cookies"""
        cookie_str = self.COOKIES.get(domain)
        return self.cookie_str_to_dict(cookie_str)

    @staticmethod
    def cookie_str_to_dict(cookie_str: str) -> dict:
        """将 cookie 字符串转换为字典格式"""
        if not cookie_str:
            return {}

        cookies = {}
        for item in cookie_str.split(';'):
            item = item.strip()
            if not item:
                continue
            if '=' not in item:
                continue

            name, value = item.split('=', 1)
            cookies[name.strip()] = value.strip()

        return cookies
