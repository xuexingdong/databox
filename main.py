from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.xiaohongshu.xhs_home_feed_spider import XiaohongshuHomeFeedSpider
from databox.xiaohongshu.xhs_note_spider import XiaohongshuNoteSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(XiaohongshuHomeFeedSpider)
    # process.crawl(XiaohongshuNoteSpider, user_id='1')
    process.start()
