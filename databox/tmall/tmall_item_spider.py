import json
from urllib.parse import urlencode

import pickle

import qrcode
import requests
from scrapy import Request
from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy_redis.spiders import RedisSpider

from databox.tmall.item_loaders import TmallItemLoader
from databox.tmall.tmall_rate_spider import TmallRateSpider
from databox.wechat.enums import QRCodeStatus
from .items import TmallItem, TmallSkuItem


class TmallItemSpider(RedisSpider):
    name = 'tmall_item'

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.tmall.pipelines.TmallItemPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'databox.tmall.middlewares.CookiesMiddleware': 543
        },
        'CONCURRENT_REQUESTS': 64,
        'RETRY_TIMES': 10
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        status = None
        while status != QRCodeStatus.CONFIRM:
            res = requests.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do').json()
            self.qrcode_url, self.lg_token, self.ad_token = res['url'], res['lgToken'], res['adToken']
            status = QRCodeStatus.WAITING
            # 控制台打印二维码
            self.print_qrcode()
            # 判断用户是否扫码
            while status != QRCodeStatus.EXPIRED and status != QRCodeStatus.SUCCESS:
                status = self.get_qrcode_status()
            # 判断用户是否点击登录
            while status != QRCodeStatus.EXPIRED and status != QRCodeStatus.CONFIRM:
                status = self.get_qrcode_status()
        requests.get('https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=' + lg_token)

    def start_requests(self):
        item_id = '529092527208'
        # 淘宝会检查referer
        headers = {
            'Referer': 'https://mdskip.taobao.com/core/initItemDetail.htm?itemId=' + item_id
        }
        item_url = 'https://detail.tmall.com/item.htm?id=' + item_id
        return [Request(item_url, headers=headers, meta={'item_id': item_id}, dont_filter=True)]

    def parse(self, response: Response):
        title = response.css('meta[name="keywords"]::attr(content)').extract_first('')
        item_id = response.meta['item_id']
        seller_id = response.css('#dsr-userid::attr(value)').extract_first('')
        request: Request = response.request
        request.meta.update({
            'title': title,
            'sellId': seller_id
        })
        query1 = {
            'itemId': item_id,
            # 评论按时间排序
            'order': 1
        }
        # 商品详情
        yield Request('https://mdskip.taobao.com/core/initItemDetail.htm?' + urlencode(query1),
                      headers=request.headers,
                      cookies=request.cookies,
                      meta=request.meta,
                      dont_filter=True,
                      callback=self.parse_details
                      )

        # 商品评论
        query2 = {
            'itemId': item_id,
            'sellerId': seller_id,
            # 按时间排序
            'order': 3,
            # 有内容的评论
            'content': 1,
            'currentPage': 1
        }
        comment_request = Request('https://rate.tmall.com/list_detail_rate.htm?' + urlencode(query2),
                                  headers=request.headers, meta={
                'url': 'https://rate.tmall.com/list_detail_rate.htm?',
                'query': query2
            })
        self.server.lpush(TmallRateSpider.name + ':start_urls', pickle.dumps(comment_request))

    def parse_details(self, response: Response):
        request: Request = response.request
        res = json.loads(response.text)
        if res.get('isSuccess', False):
            default_model = res['defaultModel']
            l = TmallItemLoader(item=TmallItem())
            l.add_value('id', int(request.meta['item_id']))
            l.add_value('title', request.meta['title'])
            yield l.load_item()

            price_info_list = default_model['itemPriceResultDO']['priceInfo']
            for sku_id, price_info in price_info_list.items():
                sku_loader = ItemLoader(item=TmallSkuItem())
                sku_loader.add_value('id', int(sku_id))
                sku_loader.add_value('item_id', int(response.meta['item_id']))
                sku_loader.add_value('price', float(price_info['price']))
                if 'promotionList' in price_info:
                    promotion_list = price_info['promotionList']
                    sku_loader.add_value('promotion_price', float(promotion_list[0]['price']))
                yield sku_loader.load_item()

    def print_qrcode(self):
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(self.qrcode_url)
        qr.make()
        qr.print_ascii(invert=True)

    def get_qrcode_status(self):
        dic = {
            '10000': QRCodeStatus.WAITING,
            '10001': QRCodeStatus.SUCCESS,
            '10004': QRCodeStatus.EXPIRED,
            '10006': QRCodeStatus.CONFIRM
        }
        res = requests.get('https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=' + self.lg_token).json()
        return dic[res['code']]
