import json
import pickle
from datetime import datetime
from urllib.parse import urlencode

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.tmall.item_loaders import TmallItemLoader, TmallSkuLoader
from databox.tmall.tmall_rate_spider import TmallRateSpider
from .items import TmallItem, TmallSkuItem


class TmallItemSpider(RedisSpider):
    name = 'tmall_item'
    redis_key = "databox:" + name

    custom_settings = {
        'ITEM_PIPELINES':         {
            'databox.tmall.pipelines.TmallItemPipeline':    300,
            'databox.tmall.pipelines.TmallSkuItemPipeline': 400,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'databox.tmall.middlewares.TmallCookiesMiddleware': 543
        },
        'CONCURRENT_REQUESTS':    64,
        'RETRY_TIMES':            10
    }

    def start_requests(self):
        item_id = '529092527208'
        # 淘宝会检查referer
        headers = {
            'Referer': 'https://mdskip.taobao.com/core/initItemDetail.htm?itemId=' + item_id
        }
        item_url = 'https://detail.tmall.com/item.htm?id=' + item_id
        # item_url = 'https://member1.taobao.com/member/fresh/account_security.htm'
        return [Request(item_url, headers=headers, meta={'item_id': item_id}, dont_filter=True)]

    def parse(self, response: Response):
        title = response.css('meta[name="keywords"]::attr(content)').extract_first('')
        item_id = response.meta['item_id']
        seller_id = response.css('#dsr-userid::attr(value)').extract_first('')
        request: Request = response.request
        request.meta.update({
            'title':  title,
            'sellId': seller_id
        })
        query1 = {
            'itemId': item_id,
            # 评论按时间排序
            'order':  1
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
            'itemId':      item_id,
            'sellerId':    seller_id,
            # 按时间排序
            'order':       3,
            # 有内容的评论
            'content':     1,
            'currentPage': 1
        }
        comment_request = Request('https://rate.tmall.com/list_detail_rate.htm?' + urlencode(query2),
                                  headers=request.headers, meta={
                'url':   'https://rate.tmall.com/list_detail_rate.htm?',
                'query': query2
            })
        self.server.lpush(TmallRateSpider.name + ':start_urls', pickle.dumps(comment_request))

    def parse_details(self, response: Response):
        request: Request = response.request
        res = json.loads(response.text)
        if res.get('isSuccess', False):
            default_model = res['defaultModel']
            loader = TmallItemLoader(item=TmallItem())
            loader.add_value('id', int(request.meta['item_id']))
            loader.add_value('title', request.meta['title'])
            loader.add_value('created_at', datetime.now())
            yield loader.load_item()

            price_info_list = default_model['itemPriceResultDO']['priceInfo']
            for sku_id, price_info in price_info_list.items():
                sku_loader = TmallSkuLoader(item=TmallSkuItem())
                sku_loader.add_value('id', int(sku_id))
                sku_loader.add_value('item_id', int(response.meta['item_id']))
                sku_loader.add_value('price', float(price_info['price']))
                sku_loader.add_value('created_at', datetime.now())
                if 'promotionList' in price_info:
                    promotion_list = price_info['promotionList']
                    sku_loader.add_value('promotion_price', float(promotion_list[0]['price']))
                yield sku_loader.load_item()
