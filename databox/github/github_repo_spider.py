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
        'CONCURRENT_REQUESTS_PER_IP': 2,
        'ITEM_PIPELINES': {
            'databox.github.pipelines.SubmitMcpPipeline': 800,
        }
    }

    def __init__(self, url=None, match_repos=None, match_words=None, *args, **kwargs):
        super(GithubRepoSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.match_repos = match_repos
        self.match_words = match_words

    def start_requests(self):
        if self.url:
            yield Request(url=self.url, dont_filter=True)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        embedded_data_json = response.css('react-partial[partial-name=repos-overview] script::text').get()
        if not embedded_data_json:
            self.logger.error("empty repo, %s", response.url)
            return
        # TODO 空repo去除
        markdown_body = response.css('article.markdown-body')
        # 需要匹配的repo，不需要收录
        if response.url in self.match_repos:
            if self.match_words:
                all_links = markdown_body.css("a::attr(href)").getall()
                for link in all_links:
                    if self.is_github_repo(link) and any(word in link for word in self.match_words):
                        yield Request(link)
        else:
            embedded_data = json.loads(embedded_data_json)
            repo_data = embedded_data['props']['initialPayload']['repo']
            sidebar = response.css('.Layout-sidebar')
            description = sidebar.css('p.f4::text').get()
            if description:
                description = description.strip()
            tags = sidebar.css('div.f6 > a::text').getall()
            if tags:
                tags = ','.join([tag.strip() for tag in tags])
            title = img_url = None
            if markdown_body:
                title = markdown_body.css('.markdown-heading > h1::text').get()
                if title:
                    title = title.strip()
                img_url = markdown_body.css('img::attr(src)').get()
                if img_url:
                    img_url = response.urljoin(img_url)
            repo = Repo()
            repo['name'] = repo_data['name']
            repo['title'] = title
            repo['description'] = description
            repo['avatar_url'] = repo_data['ownerAvatar'].strip()
            repo['author_name'] = repo_data['ownerLogin'].strip()
            repo['author_avatar_url'] = repo_data['ownerAvatar'].strip()
            repo['tags'] = tags
            repo['url'] = response.url
            repo['img_url'] = img_url
            readme_url = f"https://raw.githubusercontent.com/{repo_data['ownerLogin']}/{repo_data['name']}/refs/heads/main/README.md"
            yield Request(
                url=readme_url,
                callback=self.parse_readme,
                meta={'repo': repo}  # 传递 repo_item
            )

    def parse_readme(self, response: Response, **kwargs: Any) -> Any:
        if response.status == 404:
            self.logger.warning('no readme, drop item, %s', response.url)
            return
        # 获取传递的 Repo item
        if '404: Not Found' in response.text:
            self.logger.warning('no readme, drop item, %s', response.url)
            return
        # 提取 README 内容
        repo = response.meta['repo']
        readme_content = response.text
        repo['content'] = readme_content.strip()
        yield repo

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
