import json
from typing import Any

from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider

from databox.instagram import constants
from databox.instagram.ins_comment_spider import InsCommentSpider
from databox.instagram.items import InsMediaItem
from databox.instagram.model import PolarisProfilePostsQuery, PolarisProfilePostsQueryVariables, \
    PolarisProfilePostsTabContentQuery_connectionVariables, PolarisProfilePostsTabContentQuery_connection, ProductType


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
        user_id = res['user_id']
        username = res['username']
        formdata = PolarisProfilePostsQuery(
            variables=PolarisProfilePostsQueryVariables(username=username),
        ).to_request_body()
        self.logger.info(formdata)
        yield FormRequest(
            url=constants.GRAPHQL_URL,
            meta={
                'user_id': user_id,
                'username': username
            },
            dont_filter=True,
            formdata=formdata
        )

    def parse(self, response, **kwargs: Any) -> Any:
        data = response.jmespath('data.xdt_api__v1__feed__user_timeline_graphql_connection').get()
        if not data:
            return
        user_id = response.meta.get('user_id')
        username = response.meta.get('username')
        edges = data.get('edges', [])
        media_ids = set()
        for edge in edges:
            node = edge['node']
            item = InsMediaItem()
            item['user_id'] = user_id
            item['username'] = username
            item['code'] = node['code']
            item['pk'] = node['pk']
            item['id'] = node['id']
            item['taken_at'] = node['taken_at']
            item['caption'] = node['caption']
            item['comment_count'] = node['comment_count']
            item['like_count'] = node['like_count']
            item['product_type'] = ProductType(node['product_type'])
            self.logger.info(item)
            yield item
            media_ids.add(node['pk'])

        comment_spider_data = map(
            lambda media_id: json.dumps({
                'media_id': media_id,
            }),
            media_ids
        )
        self.server.rpush(InsCommentSpider.redis_key, *comment_spider_data)
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
