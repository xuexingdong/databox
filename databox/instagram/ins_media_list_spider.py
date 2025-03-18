from typing import Any

from pydantic import BaseModel
from scrapy import FormRequest
from scrapy_redis.spiders import RedisSpider

from databox.instagram import constants
from databox.instagram.ins_comment_spider import InsCommentSpider, InsCommentData
from databox.instagram.items import InsMediaItem
from databox.instagram.model import PolarisProfilePostsQuery, PolarisProfilePostsQueryVariables, \
    PolarisProfilePostsTabContentQuery_connectionVariables, PolarisProfilePostsTabContentQuery_connection, ProductType


class InsMediaListData(BaseModel):
    user_id: str
    username: str
    end_cursor: str | None = None


class InsMediaListSpider(RedisSpider):
    name = 'ins_media_list'
    redis_key = "databox:ins:" + name
    redis_batch_size = 3
    custom_settings = {
        'DOWNLOAD_DELAY': 5,
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
    }

    def make_request_from_data(self, data):
        ins_media_list_data = InsMediaListData.model_validate_json(data)
        yield self.get_media_list_request(ins_media_list_data)

    def parse(self, response, **kwargs: Any) -> Any:
        json_data = response.json()
        if json_data['status'] != 'ok':
            return
        data = response.jmespath('data.xdt_api__v1__feed__user_timeline_graphql_connection').get()
        if not data:
            return
        ins_media_list_data = InsMediaListData.model_validate(response.meta)
        edges = data.get('edges', [])
        for edge in edges:
            node = edge['node']
            item = InsMediaItem(
                user_id=ins_media_list_data.user_id,
                username=ins_media_list_data.username,
                code=node['code'],
                pk=node['pk'],
                id=node['id'],
                taken_at=node['taken_at'],
                image_url=node.get('image_versions2', {}).get('candidates', [{}])[0].get('url'),
                video_url=node.get('video_versions', [{}])[0].get('url'),
                caption=node['caption'],
                comment_count=node['comment_count'],
                like_count=node['like_count'],
                product_type=ProductType(node['product_type'])
            )
            self.logger.info(item)
            yield item
            self.server.rpush(InsCommentSpider.redis_key, InsCommentData(media_id=node['pk']).model_dump_json())
        page_info = data.get('page_info')
        self.logger.info(page_info)
        if page_info.get('has_next_page', False):
            ins_media_list_data.end_cursor = page_info['end_cursor']
            self.server.rpush(self.redis_key, ins_media_list_data.model_dump_json())

    @staticmethod
    def get_media_list_request(ins_media_list_data):
        username = ins_media_list_data.username
        # first page
        if ins_media_list_data.end_cursor is None:
            formdata = PolarisProfilePostsQuery(
                variables=PolarisProfilePostsQueryVariables(username=username)
            ).to_request_body()
        else:
            formdata = PolarisProfilePostsTabContentQuery_connection(
                variables=PolarisProfilePostsTabContentQuery_connectionVariables(username=username,
                                                                                 after=ins_media_list_data.end_cursor),
            ).to_request_body()
        yield FormRequest(
            url=constants.GRAPHQL_URL,
            meta=ins_media_list_data.model_dump(),
            dont_filter=True,
            formdata=formdata
        )
