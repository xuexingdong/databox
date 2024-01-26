# import json
# import pickle
#
# from bs4 import BeautifulSoup
# from scrapy_redis.spiders import RedisSpider
#
# from databox.alipay import constants
# from databox.alipay.items import AlipayBillItem
#
# # search = splash:select('#J-set-query-form')
# # search:mouse_click()
# # assert(splash:wait(0.5))
# from databox.puppeteer import utils
# from databox.puppeteer.request import PuppeteerRequest
#
#
# class AlipayBillSpider(RedisSpider):
#     name = 'alipay_bill'
#     redis_key = name
#     cookies_store_key = f'{name}:cookies'
#     headers = {
#         'referer': constants.BILL_URL
#     }
#     script = """
#             function main(splash)
#                 splash:clear_cookies()
#                 splash:init_cookies(splash.args.cookies)
#                 assert(splash:go(splash.args.url))
#                 assert(splash:wait(0.5))
#                 return {
#                     html = splash:html(),
#                     screenshot = splash:png(),
#                     cookies = splash:get_cookies()
#                     }
#             end
#             """
#
#     next_page_script = """
#                 function main(splash)
#                     splash:init_cookies(splash.args.cookies)
#                     assert(splash:go(splash.args.url))
#                     assert(splash:wait(0.5))
#                     search = splash:select('#J-set-query-form')
#                     search:mouse_click()
#                     assert(splash:wait(0.5))
#                     return {
#                         html = splash:html(),
#                         cookies = splash:get_cookies()
#                         }
#                 end
#                 """
#
#     custom_settings = {
#         'DOWNLOADER_MIDDLEWARES': {
#             'databox.alipay.middlewares.AlipayCookieMiddleware': 400
#         },
#         'ITEM_PIPELINES': {
#             'databox.weibo.pipelines.MBlogPipeline': 800,
#         }
#     }
#
#     def make_request_from_data(self, data):
#         self.logger.info('start crawl bill')
#         data = json.loads(data.decode(self.redis_encoding))
#         cookies = pickle.loads(self.server.hget(self.cookies_store_key, data['cookie_key']))
#         puppeteer_cookies = []
#         for morsel in cookies:
#             puppeteer_cookies.append({
#                 'name': morsel.key,
#                 'value': morsel.value,
#                 'domain': morsel['domain']
#             })
#         # kv结构转为对象结构
#         mailto = data['mailto']
#         return PuppeteerRequest(
#             constants.BILL_URL,
#             callback=self.parse,
#             method='GET',
#             dont_filter=True,
#             meta={
#                 'cookies': puppeteer_cookies,
#                 'mailto': mailto
#             })
#
#     def parse(self, response, **kwargs):
#         print(response.data['cookies'])
#         bs4 = BeautifulSoup(response.data['html'], features='html.parser')
#         bill_table = bs4.select_one('#tradeRecordsIndex')
#         bill_trs = bill_table.select('tbody > tr')
#         for bill_tr in bill_trs:
#             print(bill_tr.text)
#             item = AlipayBillItem()
#             yield item
#         if bs4.select('.page-next'):
#             request = response.request
#             request.meta['cookies'] = response.data['cookies']
#             yield request
#         yield response.request
