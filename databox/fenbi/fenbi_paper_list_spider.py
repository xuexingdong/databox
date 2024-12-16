import json
import re
from typing import Any
from urllib.parse import urlencode

import execjs
from scrapy import Request

from databox.fenbi.fenbi_paper_spider import FenbiPaperSpider
from databox.redis_spider import RedisSpider


class FenbiPaperListSpider(RedisSpider):
    name = 'fenbi_paper_list'
    redis_key = "databox:" + name

    runtime_js_regex = r'(?<=<script src=")//nodestatic.fbstatic.cn/weblts_spa_online/tiku/runtime-es2015.\w+.js(?=" type="module">)'
    js_8_regex = r'(?<=8:")\w+?(?=")'
    x_regex = r'const x=.+?(?=var M=)'

    def start_requests(self):
        yield Request('https://www.fenbi.com/spa/tiku/guide/redirect', dont_filter=True)

    def parse(self, response, **kwargs: Any) -> Any:
        base = response.css('base::attr(href)').get()
        match = re.search(self.runtime_js_regex, response.text)
        if match:
            runtime_js_regex = 'https:' + match.group(0)
            yield Request(runtime_js_regex, callback=self.parse_runtime_js, meta={
                'base': base
            }, dont_filter=True)

    def parse_runtime_js(self, response, **kwargs: Any) -> Any:
        match = re.search(self.js_8_regex, response.text)
        if match:
            js_8_url = f'https://nodestatic.fbstatic.cn/weblts_spa_online/tiku/8-es2015.{match.group(0)}.js'
            yield Request(js_8_url, callback=self.parse_js_8, dont_filter=True)

    def parse_js_8(self, response, **kwargs: Any) -> Any:
        match = re.search(self.x_regex, response.text)
        if match:
            define_h = 'const h = "https://spa.fenbi.com";'
            data_str = define_h + match.group(0).replace('b.Jk', '2')
            context = execjs.compile(data_str)
            labels = context.eval('x')
            for label in labels:
                if 'prefix' in label:
                    yield Request(self.get_sub_labels_url(label['prefix']),
                                  callback=self.parse_sub_labels, meta={'prefix': label['prefix']}, dont_filter=True)
                if 'children' in label:
                    for child in label['children']:
                        if 'prefix' in child:
                            yield Request(self.get_sub_labels_url(child['prefix']),
                                          callback=self.parse_sub_labels, meta={'prefix': child['prefix']},
                                          dont_filter=True)

    def parse_sub_labels(self, response, **kwargs: Any) -> Any:
        print(response.json())
        paper_ids_list = response.jmespath('[].labelMeta.paperIds').getall()
        for paper_ids in paper_ids_list:
            self.server.rpush(
                FenbiPaperSpider.redis_key, *list(map(lambda paper_id: json.dumps({'paper_id': paper_id}), paper_ids)))

    def parse_paper_list(self, response, **kwargs: Any) -> Any:
        res = response.json()
        for paper in res['list']:
            self.server.rpush(FenbiPaperSpider.redis_key, json.dumps({
                'paper_id': paper['id']
            }))
        page_info = res['pageInfo']
        if page_info['currentPage'] == page_info['totalPage']:
            return
        yield Request(
            self.get_paper_list_url(response.meta['prefix'], page_info['currentPage'] + 1, page_info['pageSize']),
            callback=self.parse_paper_list, meta={
                'prefix': response.meta['prefix']
            }, dont_filter=True)

    @staticmethod
    def get_paper_list_url(prefix, to_page=0, page_size=15, label_id=''):
        param = {
            'toPage': to_page,
            'pageSize': page_size,
            'labelId': label_id,
        }
        return f'https://tiku.fenbi.com/api/{prefix}/comptroller/papers?{urlencode(param)}'

    @staticmethod
    def get_sub_labels_url(prefix):
        return f'https://tiku.fenbi.com/api/{prefix}/comptroller/subLabels'
