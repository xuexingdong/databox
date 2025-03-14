import json
from typing import Any
from urllib.parse import urlparse

import arrow
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.http.request import NO_CALLBACK
from scrapy.utils.defer import maybe_deferred_to_future
from scrapy.utils.project import get_project_settings
from scrapy_redis.spiders import RedisSpider

from databox.github.items import Repo


class GithubRepoSpider(RedisSpider):
    name = 'github_repo'
    redis_key = "databox:" + name
    redis_batch_size = 1
    max_idle_time = 60 * 5
    custom_settings = {
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'ITEM_PIPELINES': {
            'databox.github.pipelines.SubmitMcpPipeline': 800,
        },
        'DOWNLOAD_DELAY': 5,
    }

    def __init__(self, url=None, match_repos=None, match_words=None, *args, **kwargs):
        super(GithubRepoSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.match_repos = match_repos
        self.match_words = match_words

    def start_requests(self):
        if self.url:
            yield Request(url=self.url, dont_filter=True)

    async def parse(self, response: Response, **kwargs: Any) -> Any:
        embedded_data_json = response.css('react-partial[partial-name=repos-overview] script::text').get()
        if not embedded_data_json:
            self.logger.warning("empty repo, %s", response.url)
            return
        # TODO 空repo去除
        markdown_body = response.css('article.markdown-body')
        # 需要匹配的repo，不需要收录
        if self.match_repos and response.url in self.match_repos:
            if self.match_words:
                all_links = markdown_body.css("a::attr(href)").getall()
                for link in all_links:
                    if self.is_github_repo(link) and any(word in link for word in self.match_words):
                        yield Request(link, dont_filter=True)
        else:
            embedded_data = json.loads(embedded_data_json)
            repo_data = embedded_data['props']['initialPayload']['repo']
            star = response.css('#repo-stars-counter-star::attr(title)').get(default='').replace(',', '')
            sidebar = response.css('.Layout-sidebar')
            description = sidebar.css('p.f4::text').get(default='').strip()
            tags = sidebar.css('div.f6 > a.topic-tag::text').getall()
            if tags:
                tags = ','.join([tag.strip() for tag in tags])
            license_text = sidebar.css('h3:contains("License") ~ div').xpath('string(.)').get(default='').strip()
            main_language = sidebar.css('h2:contains("Languages") ~ ul li span::text').get()
            title = img_url = None
            if markdown_body:
                title = markdown_body.css('.markdown-heading > h1::text').get(default='').strip()
                img_url = markdown_body.css('img::attr(src)').get()
                if img_url:
                    img_url = response.urljoin(img_url)
            readme_content = await self.get_readme_content(repo_data)
            if not readme_content:
                self.logger.warning('no readme, drop item, %s', response.url)
                return
            repo = Repo()
            repo['name'] = repo_data['name']
            if response.meta and 'type' in response.meta:
                repo['type'] = response.meta['type']
            repo['title'] = title
            repo['description'] = description
            repo['avatar_url'] = repo_data['ownerAvatar'].strip()
            repo['author_name'] = repo_data['ownerLogin'].strip()
            repo['author_avatar_url'] = repo_data['ownerAvatar'].strip()
            repo['tags'] = tags
            repo['url'] = response.url
            repo['img_url'] = img_url
            metadata = {
                'star': star,
                'license': license_text,
                'language': main_language,
                'is_official': self.is_official_repo(response.url),
                'latest_commit_time': await self.get_latest_commit_time(repo_data)
            }
            repo['metadata'] = metadata
            repo['content'] = readme_content

            yield repo

    async def get_readme_content(self, repo_data):
        readme_url = self.get_readme_url(repo_data['ownerLogin'], repo_data['name'], repo_data['defaultBranch'])
        readme_request = Request(
            url=readme_url,
            callback=NO_CALLBACK,
            dont_filter=True
        )
        deferred = self.crawler.engine.download(readme_request)
        readme_response = await maybe_deferred_to_future(deferred)
        return self.parse_readme(readme_response)

    @staticmethod
    def get_readme_url(author_name, name, branch):
        return f"https://raw.githubusercontent.com/{author_name}/{name}/refs/heads/{branch}/README.md"

    def parse_readme(self, response: Response):
        if response.status == 404:
            return ''
        if '404: Not Found' == response.text:
            return ''
        return response.text.strip()

    async def get_latest_commit_time(self, repo_data):
        latest_commit_url = self.get_latest_commit_url(repo_data['ownerLogin'], repo_data['name'],
                                                       repo_data['defaultBranch'])
        latest_commit_request = Request(
            url=latest_commit_url,
            callback=NO_CALLBACK,
            headers={
                'x-requested-with': 'XMLHttpRequest'
            },
            dont_filter=True
        )
        deferred = self.crawler.engine.download(latest_commit_request)
        latest_commit_response = await maybe_deferred_to_future(deferred)
        return self.parse_latest_commit_time(latest_commit_response)

    @staticmethod
    def get_latest_commit_url(author_name, name, default_branch):
        return f"https://github.com/{author_name}/{name}/latest-commit/{default_branch}"

    @staticmethod
    def parse_latest_commit_time(response: Response):
        res = response.json()
        last_commit_time = arrow.get(res['date']).format("YYYY-MM-DD HH:mm:ss")
        return last_commit_time

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

    @staticmethod
    def is_official_repo(url):
        return 'github.com/modelcontextprotocol' in url


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(GithubRepoSpider,
                  'https://github.com/modelcontextprotocol/servers', match_repos=[
            'https://github.com/punkpeye/awesome-mcp-servers',
            'https://github.com/wong2/awesome-mcp-servers',
            'https://github.com/modelcontextprotocol/servers'
        ], match_words=['mcp', 'modelcontextprotocol'])
    process.start()
