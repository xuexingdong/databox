from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor

from databox.tiktok.tiktok_video_playwright_spider import TiktokVideoPlayWrightSpider
from databox.tiktok.tiktok_video_spider import TiktokVideoSpider

if __name__ == '__main__':
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl(TiktokVideoPlayWrightSpider, nickname='openai')
    process.crawl(TiktokVideoSpider)
    process.start()
