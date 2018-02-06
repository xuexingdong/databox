import pickle

from redis import Redis
from scrapy import cmdline
from scrapy.crawler import CrawlerProcess
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    'mysql+pymysql://root:123456@localhost/databox?charset=utf8', echo=False)  # 创建DBSession类型
DBSession = sessionmaker(bind=engine)


def get_mysql_session():
    session = DBSession()
    return session


if __name__ == '__main__':
    cmdline.execute('scrapy crawl petchain'.split())
