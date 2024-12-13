from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from databox.github.github_repo_spider import GithubRepoSpider
from databox.github.github_search_spider import GithubSearchSpider

if __name__ == '__main__':
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl(GithubSearchSpider, q='mcp-server')
    # 如果readme匹配到match_words，则继续下钻
    process.crawl(GithubRepoSpider, match_words=['mcp', 'modelcontextprotocol'])
    process.start()
