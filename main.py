from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from databox.weibo.weibo_account import WeiboAccountSpider

if __name__ == '__main__':
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl(WeiboAccountSpider)
    # process.crawl(WeiboSpider, q='21chee')
    process.start()
