from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.xiaohongshu.xhs_user_spider import XiaohongshuUserSpider

if __name__ == '__main__':
    # install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl(XiaohongshuUserSpider, profile_str='59f985684eacab1ce3cc5409')
    process.start()
