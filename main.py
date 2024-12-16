from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from databox.fenbi.fenbi_paper_list_spider import FenbiPaperListSpider
from databox.github.github_repo_search_spider import GithubRepoSearchSpider
from databox.github.github_repo_spider import GithubRepoSpider

if __name__ == '__main__':
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl(GithubRepoSearchSpider, q='mcp-server', p=1, updated_after='2024-12-14')
    process.crawl(GithubRepoSpider,
                  match_repos=[
                      'https://github.com/punkpeye/awesome-mcp-servers',
                      'https://github.com/wong2/awesome-mcp-servers',
                      'https://github.com/modelcontextprotocol/servers'
                  ], match_words=['mcp', 'modelcontextprotocol'])
    # process.crawl(FenbiPaperListSpider)
    process.start()
