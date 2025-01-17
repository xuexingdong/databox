from typing import Any
from urllib.parse import quote

import arrow
from scrapy import Spider
from scrapy.http import Response

from databox.idiom.enums import IdiomEmotion
from databox.idiom.items import IdiomItem


class IdiomSpider(Spider):
    name = 'idiom'
    emotion_map = {
        '褒义成语': IdiomEmotion.POSITIVE.value,
        '贬义成语': IdiomEmotion.NEGATIVE.value,
        '中性成语': IdiomEmotion.NEUTRAL.value,
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.idiom.pipelines.IdiomPipeline': 300,
        }
    }

    def __init__(self, words, *args, **kwargs):
        super(IdiomSpider, self).__init__(*args, **kwargs)
        self.words = words
        self.start_urls = [f'https://www.hanyuguoxue.com/chengyu/search?words={quote(words)}']

    def parse(self, response: Response, **kwargs: Any) -> Any:
        ci_main = response.css('.ci-main')
        if not ci_main:
            return
        idiom_item = IdiomItem()
        idiom_item['word'] = self.words
        idiom_item['pinyin'] = ' '.join(ci_main.css('.pinyin > span::text').getall())

        ci_attrs = ci_main.css('.ci-attrs')
        idiom_item['emotion'] = self.emotion_map.get(self.find_ci_attr_value(ci_attrs, '感情'))

        explain = ci_main.css('#explain')
        idiom_item['meaning'] = '\n'.join(explain.css('.primary::text').getall())
        idiom_item['origin'] = self.find_explain_value(explain, '出处')
        idiom_item['usage'] = self.find_explain_value(explain, '用法')
        idiom_item['example'] = self.find_explain_value(explain, '例子')
        idiom_item['distinction'] = self.find_explain_value(explain, '辨析')
        idiom_item['story'] = self.find_explain_value(explain, '故事')

        detail = ci_main.css('#detail')
        idiom_item['explanation'] = detail.css('.explain').xpath('string(.)').get()
        sub_details = detail.css('details')
        for sub_detail in sub_details:
            if '例句' == sub_detail.css('summary::text').get():
                # 排除另外一个名为“例句”的信息
                if not sub_detail.css('table.compare'):
                    idiom_item['example_sentences'] = sub_detail.css('p.note').xpath('string(.)').getall()
        idiom_item['last_update_time'] = arrow.now().format('YYYY-MM-DD HH:mm:ss')
        return idiom_item

    @staticmethod
    def find_ci_attr_value(ci_attrs, field_name):
        return ci_attrs.css(f'p > span:contains({field_name}) + a::text').get()

    @staticmethod
    def find_explain_value(explain, field_name):
        names = explain.css('p.ext > span.name::text').getall()
        texts = explain.css('p.ext').xpath('string(.)').getall()
        for name, text in zip(names, texts):
            if name == field_name:
                return text[len(name) + 1:]
        return ''
