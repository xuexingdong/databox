import time
from html import unescape

from scrapy import Spider, Request

from databox.hao6v import constants
from databox.hao6v.items import MovieItem


class Hao6vSpider(Spider):
    name = 'hao6v'

    collection = 'movies'
    start_urls = ['http://www.hao6v.com/gvod/zx.html']

    custom_settings = {
        'ITEM_PIPELINES':            {
            'databox.hao6v.pipelines.MoviePipeline': 300,
        },
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
        'CONCURRENT_REQUESTS':       5,
    }

    def parse(self, response):
        links = response.css('#main .col4 .box ul.list > li > a::attr(href)').extract()
        print(links)
        for link in links:
            yield Request(link, callback=self.parse_movie, dont_filter=True)

    def parse_movie(self, response):
        box = response.css('#main > .col6 > .box')
        movie_item = MovieItem()
        movie_item['cover'] = box.css('#endText > strong + p > img::attr(src)').extract_first()
        if not movie_item['cover']:
            self.logger.info(f"{response.url} has not cover")
            return
        selector = '#endText > strong'
        while True:
            selector += ' + p'
            texts = box.css(selector).xpath('string(.)').extract_first()
            if texts:
                texts = texts.split('◎')
                break
        for text in texts:
            for label, key in constants.LABELS.items():
                # 匹配到了
                if label in text:
                    plain_text = unescape(text[1 + len(label):].strip())
                    split_text = plain_text.split('\r\n')
                    if len(split_text) > 1:
                        movie_item[key] = list(map(lambda t: t.strip(), split_text))
                    else:
                        movie_item[key] = plain_text
                    continue
        # 简介单独抽取
        all_text = box.css('#endText').xpath('string(.)').extract_first()
        movie_item['introduction'] = self._get_introduction_from_all_text(all_text)
        movie_item['source_url'] = response.url
        download_tds = response.css('#endText table[bgcolor="#0099cc"] td')
        movie_item['download_urls'] = self._parse_download_urls_from_tds(download_tds)
        movie_item['ts'] = int(time.time())
        movie_item['pv'] = 0
        return movie_item

    @staticmethod
    def _get_introduction_from_all_text(all_text):
        begin = all_text.index('◎简　　介') + len('◎简　　介')
        end = all_text.index('【下载地址】')
        return all_text[begin:end].strip()

    @staticmethod
    def _parse_download_urls_from_tds(download_tds):
        download_urls = []
        for download_td in download_tds:
            if '在线观看' in download_td.css('::text').extract_first():
                continue
            else:
                download_urls.append(download_td.css('a::attr(href)').extract_first())
        return download_urls
