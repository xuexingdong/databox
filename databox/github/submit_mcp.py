from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.github.github_repo_search_spider import GithubRepoSearchSpider
from databox.github.github_repo_spider import GithubRepoSpider
from databox.pulsemcp.pulsemcp_mcp_client import PulseMcpMcpClient


def run_spiders():
    process = CrawlerProcess(get_project_settings())
    process.crawl(PulseMcpMcpClient)
    process.crawl(GithubRepoSearchSpider, q='mcp-server', updated_after='2025-02-22')
    process.crawl(GithubRepoSpider,
                  match_repos=[
                      'https://github.com/punkpeye/awesome-mcp-servers',
                      'https://github.com/wong2/awesome-mcp-servers',
                      'https://github.com/modelcontextprotocol/servers'
                  ], match_words=['mcp', 'modelcontextprotocol'])
    process.start()


if __name__ == "__main__":
    run_spiders()
