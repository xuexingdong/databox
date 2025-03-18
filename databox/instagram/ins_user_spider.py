import re
from typing import Any

from itemadapter import ItemAdapter
from pydantic import BaseModel
from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.instagram import constants
from databox.instagram.ins_media_list_spider import InsMediaListSpider, InsMediaListData
from databox.instagram.items import InsUserItem
from databox.instagram.model import PolarisProfilePageContentQuery, ProfileQueryVariables


class InsUserData(BaseModel):
    username: str


class InsUserSpider(RedisSpider):
    USER_ID_PATTERN = r'"profile_id":\s*"(\d+)"'

    name = 'ins_user'
    redis_key = "databox:ins:" + name

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
        'ITEM_PIPELINES': {
            # 'databox.instagram.pipelines.PaperPipeline': 800,
        }
    }

    def make_request_from_data(self, data):
        ins_user_data = InsUserData.model_validate_json(data)
        self.logger.info(ins_user_data)
        profile_url = self.get_profile_info_url(ins_user_data)
        yield Request(url=profile_url, callback=self.parse, headers=constants.headers, dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        match = re.search(self.USER_ID_PATTERN, response.text)
        if not match:
            return
        user_id = match.group(1)
        formdata = PolarisProfilePageContentQuery(
            variables=ProfileQueryVariables(id=user_id)
        ).to_request_body()
        yield FormRequest(
            url=constants.GRAPHQL_URL,
            callback=self.parse_graphql,
            dont_filter=True,
            formdata=formdata
        )

    def parse_graphql(self, response: Response, **kwargs: Any) -> Any:
        json_data = response.json()
        if json_data['status'] != 'ok':
            return
        user = json_data.get('data', {}).get('user', {})
        if not user:
            return
        item = InsUserItem(
            id=user.get('id'),
            username=user.get('username'),
            full_name=user.get('full_name'),
            biography=user.get('biography'),
            media_count=user.get('media_count'),
            follower_count=user.get('follower_count'),
            following_count=user.get('following_count'),
            is_private=user.get('is_private'),
            is_verified=user.get('is_verified'),
            profile_pic_url=user.get('profile_pic_url'),
            hd_profile_pic_url=user.get('hd_profile_pic_url_info', {}).get('url'),
            category=user.get('category'),
            is_business=user.get('is_business'),
            fbid_v2=user.get('fbid_v2'),
            pk=user.get('pk')
        )
        yield item
        self.server.rpush(InsMediaListSpider.redis_key,
                          InsMediaListData(user_id=user.get('id'), username=user.get('username')).model_dump_json())

    @staticmethod
    def get_profile_info_url(username: str):
        return f"https://www.instagram.com/{username}/"
