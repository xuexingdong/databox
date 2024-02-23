import re
from typing import Any
from urllib.parse import urljoin

import execjs
from scrapy import Spider, Request
from scrapy.http import Response


class SoraSpider(Spider):
    DATA_URL_PATTERN = re.compile(r'(?<=src=")\./data.*(?=")')

    HOST = 'https://soravideos.media/'
    name = 'sora'
    start_urls = [HOST]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        match = re.search(self.DATA_URL_PATTERN, response.text)
        data_url = urljoin(self.HOST, match.group())
        yield Request(data_url, self.parse_data, dont_filter=True)

    def parse_data(self, response: Response, **kwargs: Any) -> Any:
        context = execjs.compile(response.text)
        source_objects = context.eval('SourceObject')
        videos: list = context.eval('videos')
        videos.extend(context.eval('otherTextToVideos'))
        videos.extend(context.eval('imageToVideos'))
        videos.extend(context.eval('ConnectingVideos'))
        videos.extend(context.eval('videosBadDemo'))
        for video in videos:
            if video['source'] in source_objects:
                video['sourceName'] = source_objects[video['source']]['name']
                video['sourceLogo'] = source_objects[video['source']]['logo']
        print(videos)
