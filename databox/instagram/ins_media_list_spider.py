import json
from typing import Any

from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider

from databox.instagram import constants
from databox.instagram.model import PolarisProfilePostsQuery, PolarisProfilePostsQueryVariables, \
    PolarisProfilePostsTabContentQuery_connectionVariables, PolarisProfilePostsTabContentQuery_connection


class InsMediaListSpider(RedisSpider):
    name = 'ins_media_list_spider'
    redis_key = "databox:" + name
    max_idle_time = 60 * 5

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
    }

    def __init__(self, name: str | None = None, username: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.username = username

    def make_request_from_data(self, data):
        res = json.loads(data)
        username = res['username']
        formdata = PolarisProfilePostsQuery(
            variables=PolarisProfilePostsQueryVariables(username=username),
        ).to_request_body()
        self.logger.info(formdata)
        yield FormRequest(
            url=constants.GRAPHQL_URL,
            meta={
                'username': username
            },
            dont_filter=True,
            formdata=formdata
        )

    def parse(self, response, **kwargs: Any) -> Any:
        data = response.jmespath('data.xdt_api__v1__feed__user_timeline_graphql_connection').get()
        if not data:
            return
        username = response.meta['username']
        page_info = data.get('page_info')
        self.logger.info(page_info)
        if page_info.get('has_next_page', False):
            formdata = PolarisProfilePostsTabContentQuery_connection(
                variables=PolarisProfilePostsTabContentQuery_connectionVariables(username=username,
                                                                                 after=page_info.get('end_cursor')),
            ).to_request_body()
            yield FormRequest(
                url=constants.GRAPHQL_URL,
                meta=response.meta,
                dont_filter=True,
                formdata=formdata
            )

    @staticmethod
    def get_media_info_url(media_id: str | None = None):
        return f"https://www.instagram.com/api/v1/media/{media_id}/info/"
