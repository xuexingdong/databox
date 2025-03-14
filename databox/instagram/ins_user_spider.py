import json
import re
from typing import Any, Iterable

from scrapy import Request, FormRequest
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.instagram import constants
from databox.instagram.ins_media_list_spider import InsMediaListSpider
from databox.instagram.items import InsUserItem
from databox.instagram.model import PolarisProfilePageContentQuery, ProfileQueryVariables


class InsProfileSpider(RedisSpider):
    USER_ID_PATTERN = r'"profile_id":\s*"(\d+)"'

    name = 'ins_user_spider'
    redis_key = "databox:" + name

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
        'ITEM_PIPELINES': {
            # 'databox.instagram.pipelines.PaperPipeline': 800,
        }
    }

    def __init__(self, name: str | None = None, username: str | None = None, **kwargs: Any):
        super().__init__(name, **kwargs)
        self.username = username

    def start_requests(self) -> Iterable[Request]:
        profile_url = self.get_profile_info_url(self.username)
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
        item = InsUserItem()
        item['id'] = user.get('id')
        item['username'] = user.get('username')
        item['full_name'] = user.get('full_name')
        item['biography'] = user.get('biography')
        item['media_count'] = user.get('media_count')
        item['follower_count'] = user.get('follower_count')
        item['following_count'] = user.get('following_count')
        item['is_private'] = user.get('is_private')
        item['is_verified'] = user.get('is_verified')
        item['profile_pic_url'] = user.get('profile_pic_url')
        item['hd_profile_pic_url'] = user.get('hd_profile_pic_url_info', {}).get('url')
        item['category'] = user.get('category')
        item['is_business'] = user.get('is_business')
        item['fbid'] = user.get('fbid_v2')
        item['pk'] = user.get('pk')
        yield item

        self.server.rpush(InsMediaListSpider.redis_key, json.dumps({
            'username': item['username']
        }))

    @staticmethod
    def get_profile_info_url(username: str):
        return f"https://www.instagram.com/{username}/"
