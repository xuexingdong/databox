import json
import re
from typing import Any
from urllib.parse import urlencode

import execjs
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from databox.fenbi.fenbi_paper_spider import FenbiPaperSpider


class FenbiPaperListSpider(RedisSpider):
    name = 'fenbi_paper_list'
    redis_key = "databox:" + name

    runtime_js_regex = r'(?<=<script src=")//nodestatic.fbstatic.cn/weblts_spa_online/tiku/runtime-es2015.\w+.js(?=" type="module">)'
    js_8_regex = r'(?<=8:")\w+?(?=")'
    x_regex = r'const x=.+?(?=var M=)'

    def __init__(self, allow_label_ids=None, cookies=None, *args, **kwargs):
        super(FenbiPaperListSpider, self).__init__(*args, **kwargs)
        self.allow_label_ids = allow_label_ids
        self.cookies = cookies

    def start_requests(self):
        yield Request('https://www.fenbi.com/spa/tiku/guide/redirect', dont_filter=True)

    def parse(self, response, **kwargs: Any) -> Any:
        match = re.search(self.runtime_js_regex, response.text)
        if not match:
            return
        runtime_js_regex = 'https:' + match.group(0)
        base = response.css('base::attr(href)').get()
        yield Request(runtime_js_regex, callback=self.parse_runtime_js, meta={'base': base}, dont_filter=True)

    def parse_runtime_js(self, response):
        match = re.search(self.js_8_regex, response.text)
        if not match:
            return
        js_8_url = f'https://nodestatic.fbstatic.cn/weblts_spa_online/tiku/8-es2015.{match.group(0)}.js'
        yield Request(js_8_url, callback=self.parse_js_8, dont_filter=True)

    def parse_js_8(self, response):
        match = re.search(self.x_regex, response.text)
        if not match:
            return
        define_h = 'const h = "https://spa.fenbi.com";'
        data_str = define_h + match.group(0).replace('b.Jk', '2')
        context = execjs.compile(data_str)
        labels = context.eval('x')
        yield from self.parse_labels(labels)

    def parse_labels(self, labels):
        for label in labels:
            yield from self.process_label(label)
            if 'children' in label:
                for child in label['children']:
                    yield from self.process_label(child)

    def process_label(self, label):
        # 统一处理 Request 逻辑
        if 'prefix' in label:
            if self.allow_label_ids is None or label['id'] in self.allow_label_ids:
                yield Request(
                    self.get_paper_list_url(label['prefix'], label['id']),
                    callback=self.parse_paper_list, cookies=self.cookies,
                    meta={
                        'prefix': label['prefix'],
                        'label_id': label['id'],
                    }, dont_filter=True
                )

    def parse_paper_list(self, response):
        prefix = response.meta['prefix']
        label_id = response.meta['label_id']
        res = response.json()
        for paper in res['list']:
            exercise = paper['exercise']
            exercise_id = None
            if exercise:
                exercise_id = exercise['id']
            self.server.rpush(FenbiPaperSpider.redis_key, json.dumps({
                'prefix': prefix,
                'paper_id': paper['id'],
                'exercise_id': exercise_id
            }))
        page_info = res['pageInfo']
        if page_info['currentPage'] == page_info['totalPage']:
            return
        yield Request(
            self.get_paper_list_url(prefix, label_id, to_page=page_info['currentPage'] + 1,
                                    page_size=page_info['pageSize']),
            callback=self.parse_paper_list, cookies=response.request.cookies,
            meta=response.meta, dont_filter=True)

    @staticmethod
    def get_paper_list_url(prefix, label_id='', to_page=0, page_size=15):
        param = {
            'toPage': to_page,
            'pageSize': page_size,
            'labelId': label_id,
        }
        return f'https://tiku.fenbi.com/api/{prefix}/papers?{urlencode(param)}'
