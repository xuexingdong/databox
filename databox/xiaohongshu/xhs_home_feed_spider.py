import json
from typing import Iterable, Any

from scrapy import Request, Spider
from scrapy.http import Response, JsonRequest

from databox.xiaohongshu.items import Note


class XiaohongshuHomeFeedSpider(Spider):
    name = 'xiaohongshu:home_feed'
    collection = 'xiaohongshu_home_feed'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'databox.xiaohongshu.middlewares.XiaohongshuHeaderMiddleware': 501
        },
        'ITEM_PIPELINES': {
            'databox.xiaohongshu.pipelines.NotePipeline': 800,
        }
    }
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        "Origin": "https://www.xiaohongshu.com",
        "Referer": "https://www.xiaohongshu.com/",
        "Content-Type": "application/json;charset=UTF-8"
    }

    handle_httpstatus_list = [406, 461, 588]

    def start_requests(self) -> Iterable[Request]:
        data = {
            "cursor_score": "",
            "num": 20,
            "refresh_type": 1,
            "note_index": 0,
            "unread_begin_note_id": "",
            "unread_end_note_id": "",
            "unread_note_count": 0,
            "category": "homefeed_recommend",
            "search_key": "",
            "need_num": 10,
            "image_formats": ["jpg", "webp", "avif"]}
        url = 'https://edith.xiaohongshu.com/api/sns/web/v1/homefeed'
        return [JsonRequest(url, headers=self.headers, cookies={}, data=data, dumps_kwargs={
            'ensure_ascii': False,
            'separators': (',', ':')
        }, dont_filter=True)]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        res = json.loads(response.text)
        for item in res['data']['items']:
            note = Note()
            note['id'] = item['id']
            note['_origin_data'] = item
            yield note
        request_json = json.loads(response.request.body)
        request_json['cursor_score'] = res['data']['cursor_score']
        request_json['refresh_type'] = 3
        request_json['note_index'] += request_json['num']
        yield response.request.replace(data=request_json, headers=self.headers)
