from typing import Any, Iterable
from urllib.parse import urlencode, unquote

from scrapy import Spider, Request


class InsSpider(Spider):
    name = 'ins_spider'

    start_urls = ['https://www.instagram.com/explore/']

    custom_settings = {
        'REDIRECT_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'databox.middlewares.DomainCookieMiddleware': 400
        },
        'ITEM_PIPELINES': {
            # 'databox.instagram.pipelines.PaperPipeline': 800,
        }
    }

    def start_requests(self) -> Iterable[Request]:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-fetch-site': 'same-origin',
            'Referer': 'https://www.instagram.com/explore/'
        }
        next_url = self.get_next_url()
        yield Request(url=next_url, headers=headers, callback=self.parse, dont_filter=True)

    def parse(self, response, **kwargs: Any) -> Any:
        res = response.json()
        for sectional_item in res['sectional_items'].get('sectional_items', []):
            layout_content = sectional_item.get('layout_content', {})
            one_by_two_item = layout_content.get('one_by_two_item', {})
            if one_by_two_item:
                one_by_two_item.get('clips')
            fill_items = layout_content.get('fill_items', [])
            media_info = layout_content.get('medias', [{}])[0].get('media', {})

            # 提取用户信息
            user = media_info.get('user', {})
            user_data = {
                'id': user.get('id'),
                'username': user.get('username'),
                'full_name': user.get('full_name'),
                'is_private': user.get('is_private'),
                'profile_pic_id': user.get('profile_pic_id'),
                'profile_pic_url': unquote(user.get('profile_pic_url')),
                'follower_count': user.get('follower_count'),
                'following_count': user.get('following_count'),
                'media_count': 0,
            }

            # 提取媒体信息
            media_data = {
                'id': media_info.get('id'),
                'code': media_info.get('code'),
                'taken_at': media_info.get('taken_at'),
                'like_count': media_info.get('like_count'),
                'comment_count': media_info.get('comment_count'),
                'caption': media_info.get('caption', {}).get('text') if media_info.get('caption') else None,
                'is_video': media_info.get('is_video', False),
                'feed_type': feed_type,
                'layout_type': layout_type
            }

            # 获取媒体URL
            if media_info.get('is_video'):
                media_data['video_url'] = media_info.get('video_url')
            else:
                media_data['image_url'] = media_info.get('image_versions2', {}).get('candidates', [{}])[0].get('url')

            yield {
                'user': user_data,
                'media': media_data
            }
        if res.get('more_available', False):
            # 获取下一页
            max_id = res.get('max_id')
            if max_id:
                yield Request(
                    url=self.get_next_url(max_id),
                    headers=response.request.headers,
                    cookies=response.request.cookies,
                    callback=self.parse,
                    dont_filter=True,
                )

    @staticmethod
    def get_next_url(max_id: str | None = None):
        base_url = 'https://www.instagram.com/api/v1/discover/web/explore_grid/'
        params = {
            'include_fixed_destinations': 'true',
            'is_nonpersonalized_explore': 'false',
            'is_prefetch': 'false',
            'max_id': max_id,
            'module': 'explore_popular',
            'omit_cover_media': 'false'
        }
        return f"{base_url}?{urlencode(params)}"
