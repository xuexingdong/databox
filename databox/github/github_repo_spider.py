import json
from typing import Any
from urllib.parse import urlparse

from scrapy import Request
from scrapy.http import Response
from scrapy_redis.spiders import RedisSpider

from databox.github.items import Repo


class GithubRepoSpider(RedisSpider):
    name = 'github_repo'
    redis_key = "databox:" + name
    custom_settings = {
        'MAX_IDLE_TIME_BEFORE_CLOSE': 60,
        'CONCURRENT_REQUESTS': 1,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_DELAY': 10,
        'RETRY_HTTP_CODES': [429],
        'ITEM_PIPELINES': {
            'databox.github.pipelines.SubmitMcpPipeline': 800,
        }
    }

    def __init__(self, url=None, match_words=None, *args, **kwargs):
        super(GithubRepoSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        self.match_words = match_words

    def parse(self, response: Response, **kwargs: Any) -> Any:
        self.logger.info(response.url)
        embedded_data = json.loads(response.css('react-partial[partial-name=repos-overview] script::text').get())
        repo_data = embedded_data['props']['initialPayload']['repo']
        sidebar = response.css('.Layout-sidebar')
        description = sidebar.css('p.f4::text').get()
        if description:
            description = description.strip()
        tags = sidebar.css('div.f6 > a::text').getall()
        markdown_body = response.css('article.markdown-body')
        title = img_url = None
        if markdown_body:
            title = markdown_body.css('.markdown-heading > h1::text').get()
            img_url = markdown_body.css('img::attr(src)').get()
        repo = Repo()
        repo['name'] = repo_data['name']
        repo['title'] = title
        repo['description'] = description
        repo['avatar_url'] = repo_data['ownerAvatar']
        repo['author_name'] = repo_data['ownerLogin']
        repo['author_avatar_url'] = repo_data['ownerAvatar']
        repo['tags'] = tags
        repo['url'] = response.url
        repo['img_url'] = img_url
        self.logger.info(repo)
        yield repo
        if self.match_words:
            all_links = markdown_body.css("a::attr(href)").getall()
            match_links = [
                response.urljoin(link)
                for link in all_links
                if any(word in link for word in self.match_words)
            ]
            for match_link in match_links:
                if self.is_github_repo(match_link):
                    yield Request(match_link)

    @staticmethod
    def is_github_repo(url):
        """
        判断一个 URL 是否是 GitHub 仓库
        """
        # 解析 URL
        parsed_url = urlparse(url)
        if 'github.com' not in url:
            return False
        path_parts = parsed_url.path.strip("/").split("/")
        return len(path_parts) == 2
