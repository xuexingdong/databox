from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from databox.neteasemusic.comment_spider import NeteaseMusicCommentSpider
from databox.neteasemusic.follow_spider import NeteaseMusicFollowSpider
from databox.neteasemusic.followed_spider import NeteaseMusicFollowedSpider
from databox.neteasemusic.user_spider import NeteaseMusicUserSpider

if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(NeteaseMusicUserSpider)
    process.crawl(NeteaseMusicFollowSpider)
    process.crawl(NeteaseMusicFollowedSpider)
    process.crawl(NeteaseMusicCommentSpider)
    process.start()
