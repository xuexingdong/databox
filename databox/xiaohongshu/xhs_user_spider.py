import json
import re
from typing import Iterable, Any

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.xiaohongshu.items import User


class XiaohongshuUserSpider(RedisSpider):
    """
    没登录只能查看粗略的关注数、粉丝数、获赞与收藏数如100+，1k+，1w+，登录后有具体数字

    """
    name = 'xiaohongshu:user'
    collection = 'xiaohongshu_user'
    custom_settings = {
        'ITEM_PIPELINES': {
            'databox.xiaohongshu.pipelines.UserPipeline': 800,
        }
    }
    PATTERN = re.compile(r'(?<=window\.__INITIAL_STATE__=)(.*)(?=</script>)')

    def __init__(self, profile_str=None, xhs_no=None, *args, **kwargs):
        super(XiaohongshuUserSpider, self).__init__(*args, **kwargs)
        if not profile_str and not xhs_no:
            raise ValueError("profile_str or xhs_no must not be None")
        self.profile_str = profile_str
        self.xhs_no = xhs_no

    def start_requests(self) -> Iterable[Request]:
        url = ''
        if self.profile_str is not None:
            url = f'https://www.xiaohongshu.com/user/profile/{self.profile_str}'
        elif self.xhs_no is not None:
            url = ''
        return [Request(url, dont_filter=True)]

    def parse(self, response: Response, **kwargs: Any) -> Any:
        match = self.PATTERN.search(response.text)
        if match:
            data = json.loads(match.group().replace('undefined', 'null'))
            user_data = data['user']['userPageData']
            basic_info = user_data['basicInfo']
            interactions = user_data['interactions']
            tags = user_data['tags']

            user = User()
            user['user_id'] = response.url[-24:]
            user['gender'] = basic_info['gender']
            user['ip_location'] = basic_info['ipLocation']
            user['desc'] = basic_info['desc']
            user['imageb'] = basic_info['imageb']
            user['nickname'] = basic_info['nickname']
            user['red_id'] = basic_info['redId']
            user['follows'] = interactions[0]['count']
            user['fans'] = interactions[1]['count']
            user['interaction'] = interactions[2]['count']
            user['tags'] = tags
            user['_origin_data'] = user_data
            yield user
