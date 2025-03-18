from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.instagram.ins_comment_spider import InsCommentSpider
from databox.instagram.ins_doc_id_spider import InsDocIdSpider
from databox.instagram.ins_media_list_spider import InsMediaListSpider
from databox.instagram.ins_user_spider import InsUserSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    # process.crawl(InsDocIdSpider)
    process.crawl(InsUserSpider)
    process.crawl(InsMediaListSpider)
    process.crawl(InsCommentSpider)
    process.start()
