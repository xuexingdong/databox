# import json
# import pickle
# import re
# from http.cookies import SimpleCookie
#
# from scrapy import FormRequest, Request
# from scrapy_redis.spiders import RedisSpider
#
# from databox.alipay import constants
# from databox.puppeteer import utils
# from databox.alipay.items import AlipayQrcodeItem
# from databox.alipay.spiders.aplipay_bill import AlipayBillSpider
# from databox.puppeteer.request import PuppeteerRequest
#
#
# class AlipayLoginSpider(RedisSpider):
#     name = 'alipay_login'
#     redis_key = name
#     headers = {
#         'referer': 'https://auth.alipay.com/'
#     }
#     custom_settings = {
#         'DOWNLOAD_DELAY': 5,
#         'CONCURRENT_REQUESTS': 1,
#         'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
#         'ITEM_PIPELINES': {
#             'databox.alipay.pipelines.MailImgPipeline': 300,
#         },
#         'COMPRESSION_ENABLED': False
#     }
#
#     alipay_uid_regex = re.compile(constants.ALIPAY_UID_REGEX)
#
#     def __init__(self, smtpuser=None, smtppass=None, *args, **kwargs):
#         super(AlipayLoginSpider, self).__init__(*args, **kwargs)
#         self.smtpuser = smtpuser
#         self.smtppass = smtppass
#
#     def make_request_from_data(self, data):
#         self.logger.info('start login alipay')
#         data = json.loads(data.decode(self.redis_encoding))
#         return PuppeteerRequest(url=constants.LOGIN_URL,
#                                 callback=self.parse,
#                                 screenshot=True,
#                                 screenshot_selector='canvas',
#                                 screenshot_meta_key='sc',
#                                 dont_filter=True,
#                                 meta={
#                                     'mailto': data['mailto']
#                                 })
#
#     def parse(self, response, **kwargs):
#         puppeteer_cookies = response.meta['cookies']
#         cookies = utils.puppeteer_cookies_to_request_cookies(puppeteer_cookies)
#         security_id = response.css('input[name=qrCodeSecurityId]::attr(value)').get()
#         callback = 'light.request._callbacks.callback'
#         params = {
#             'securityId': security_id,
#             '_callback': callback
#         }
#         # jump url after qrcode scanned
#         action = response.css('#login::attr(action)').get()
#         inputs = response.css('input')
#         form_data = {}
#         for input_ in inputs:
#             name = input_.css('::attr(name)').get()
#             if name:
#                 value = input_.css('::attr(value)').get()
#                 form_data[name] = value if value else ''
#         yield FormRequest(
#             constants.BAR_CODE_STATUS_URL,
#             callback=self.parse_bar_code_status,
#             method='GET',
#             headers=self.headers,
#             cookies=cookies,
#             dont_filter=True,
#             formdata=params,
#             meta={
#                 'action': action,
#                 'dont_retry': True,
#                 'form_data': form_data,
#                 'mailto': response.meta['mailto'],
#                 'puppeteer_cookies': puppeteer_cookies
#             }
#         )
#         # return qrcode item
#         item = AlipayQrcodeItem()
#         item['img_title'] = '支付宝登录二维码'
#         item['img_bytes'] = response.meta['sc']
#         item['mailto'] = response.meta['mailto']
#         yield item
#
#     def parse_bar_code_status(self, response):
#         """
#         获取扫码状态
#         :param response:
#         :return:
#         """
#         callback = 'light.request._callbacks.callback'
#         res = eval(response.text[len(callback) + 1:-1])
#         if res['stat'] == 'fail':
#             self.logger.info('qrcode scan failed:' + res['msg'])
#             return
#         if res['barcodeStatus'] != 'confirmed':
#             self.logger.info('waiting qrcode to scan')
#             return response.request
#         self.logger.info('qrcode scan success')
#         meta = response.meta
#         return FormRequest(
#             meta['action'],
#             callback=self.parse_login_form_submit,
#             method='POST',
#             dont_filter=True,
#             formdata=meta['form_data'],
#             meta={
#                 'dont_redirect': True,
#                 'handle_httpstatus_list': [302],
#                 'mailto': meta['mailto'],
#                 'puppeteer_cookies': meta['puppeteer_cookies']
#             }
#         )
#
#     def parse_login_form_submit(self, response):
#         """
#         登录表单提交
#         :param response:
#         :return:
#         """
#         if response.status != 302:
#             self.logger.error('alipay login failed!')
#             return
#         return Request(
#             response.headers['Location'].decode(),
#             callback=self.parse_submit_redirect,
#             headers=self.headers,
#             dont_filter=True,
#             meta=response.meta
#         )
#
#     def parse_submit_redirect(self, response):
#         """
#         登录表单提交重定向
#         :param response:
#         :return:
#         """
#         if response.status == 200:
#             self.logger.info('alipay login success')
#             yield Request(
#                 constants.BILL_URL,
#                 callback=self.test_cookie,
#                 dont_filter=True,
#                 meta=response.meta
#             )
#
#     def test_cookie(self, response):
#         mailto = response.meta['mailto']
#         if response.status == 302:
#             self.logger.warning('alipay check security... return to login')
#             return
#         alipay_uid = self.alipay_uid_regex.search(response.text)[1]
#         c = SimpleCookie(response.request.headers.get('Cookie').decode())
#         cookies = []
#         for morsel in c.values():
#             cookies.append(morsel)
#         self.logger.info(f'cookies: {cookies}')
#         # redis中存入登录cookie
#         self.server.hset(AlipayBillSpider.cookies_store_key, alipay_uid, pickle.dumps(cookies))
#         # 队列中传递cookie存储的key值与邮箱
#         self.server.rpush(AlipayBillSpider.redis_key, json.dumps({
#             'cookie_key': alipay_uid,
#             'mailto': mailto
#         }))
