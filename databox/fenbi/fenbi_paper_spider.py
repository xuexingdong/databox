import json

from scrapy import Request

from databox.redis_spider import RedisSpider


class FenbiPaperSpider(RedisSpider):
    name = 'fenbi_paper'
    redis_key = "databox:" + name

    def __init__(self, paper_id=None, *args, **kwargs):
        super(FenbiPaperSpider, self).__init__(*args, **kwargs)
        self.paper_id = paper_id

    def start_requests(self):
        if self.paper_id:
            url = f'https://tiku.fenbi.com/api/xingce/exercises?app=web&kav=100&av=100&hav=100&version=3.0.0.0'
            cookies = {

            }
            yield Request(url=url, cookies=cookies, dont_filter=True)

    def make_request_from_data(self, data):
        data = json.loads(data)
        print(data['paper_id'])
