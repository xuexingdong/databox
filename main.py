import pickle

from redis import Redis
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from databox.model import Spider, SpiderStartRequest
from databox.petchain.spider import PetChainSpider
from databox.spiders.spider import XSpider

engine = create_engine(
    'mysql+pymysql://root:123456@localhost/databox?charset=utf8', echo=False)  # 创建DBSession类型
DBSession = sessionmaker(bind=engine)


def get_mysql_session():
    session = DBSession()
    return session


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(PetChainSpider)
    process.start()
