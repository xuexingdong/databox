# import json
# from typing import Iterable, Any
#
# from scrapy import Spider, Request
# from scrapy.http import Response
#
# from databox.weibo.items import MBlogItem
#
#
# class WeiboSpider(Spider):
#     name = 'weibo'
#     HEADERS = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
#     }
#     custom_settings = {
#         'DOWNLOADER_MIDDLEWARES': {
#             'databox.weibo.middlewares.WeiboCookiesMiddleware': 400
#         },
#         'ITEM_PIPELINES': {
#             'databox.weibo.pipelines.MBlogPipeline': 800,
#         }
#     }
#
#     def __init__(self, *args, q=None, **kwargs):
#         super().__init__(**kwargs)
#         self.q = q
#
#     def start_requests(self) -> Iterable[Request]:
#         url = self.generate_url_by_q(self.q)
#         return [Request(url, headers=self.HEADERS, dont_filter=True)]
#
#     def parse(self, response: Response, **kwargs: Any) -> Any:
#         res = json.loads(response.text)
#         mb = MBlogItem()
#         mb.title = res["title"]
#
#     @staticmethod
#     def generate_url_by_q(q):
#         containerid = 100103
#         _type = 1
#         page_type = 'searchall'
#         return f'https://weibo.com/u/'
#
#     @staticmethod
#     def get_comment_url(id, mid, max_id_type=0):
#         return f'https://m.weibo.cn/comments/hotflow?id={id}&mid={mid}&max_id_type={max_id_type}'
