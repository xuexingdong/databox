from scrapy import Spider

from databox.emoji.items import Emoji


class EmojiSpider(Spider):
    """
    Crawl emoji-code and emotion, about five minutes.
    """
    name = 'emoji'
    start_urls = ['https://unicode.org/emoji/charts/emoji-list.html']

    custom_settings = {
        'ITEM_PIPELINES':   {
            'databox.emoji.pipelines.FilePipeline': 100
        },
        'DOWNLOAD_TIMEOUT': 600
    }

    def __init__(self, file_path=None, *args, **kwargs):
        super(EmojiSpider, self).__init__(*args, **kwargs)
        self.filepath = file_path

    def parse(self, response):
        table = response.css('table')
        trs = table.css('tr')
        for tr in trs:
            ele_code = tr.css('td.code a::attr(name)')
            ele_emoji = tr.css('td.andr img::attr(alt)')
            if not ele_code or not ele_emoji:
                continue
            item = Emoji()
            item['code'] = ele_code.extract_first()
            item['emoji'] = ele_emoji.extract_first()
            yield item
