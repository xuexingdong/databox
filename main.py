from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.tmall.tmall_item_spider import TmallItemSpider
from databox.tmall.tmall_rate_spider import TmallRateSpider
from databox.wechat.spiders import WechatSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    # process.crawl(PetChainSpider)
    process.crawl(TmallItemSpider)
    process.crawl(TmallRateSpider)
    process.start()
