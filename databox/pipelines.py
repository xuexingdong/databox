import abc

import httpx
import pymongo
from typing import Dict, List
from sqlalchemy import create_engine, Table, MetaData, Column, String, Integer
from sqlalchemy.dialects.mysql import insert


class RDBPipeline(abc.ABC):
    def __init__(self, db_url: str, batch_size: int = 1000):
        self.engine = create_engine(db_url)
        self.batch_size = batch_size
        self.buffer: Dict[str, List[dict]] = {}
        self.table_cache = {}
        self.metadata = MetaData()

    def get_table(self, table_name: str, item: dict) -> Table:
        if table_name not in self.table_cache:
            columns = [Column('id', Integer, primary_key=True)]
            for key in item.keys():
                # 将驼峰命名转换为下划线命名
                field_name = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
                columns.append(Column(field_name, String(255)))

            self.table_cache[table_name] = Table(table_name, self.metadata, *columns)
            self.table_cache[table_name].create(self.engine, checkfirst=True)

        return self.table_cache[table_name]

    def process_item(self, item, spider):
        table_name = spider.table_name
        if table_name not in self.buffer:
            self.buffer[table_name] = []

        self.buffer[table_name].append(dict(item))

        if len(self.buffer[table_name]) >= self.batch_size:
            self.flush(table_name)

        return item

    def flush(self, table_name: str):
        if not self.buffer.get(table_name):
            return

        items = self.buffer[table_name]
        table = self.get_table(table_name, items[0])
        with self.engine.begin() as conn:
            conn.execute(insert(table), items)
            stmt = insert(table).values(items)
            stmt = stmt.on_duplicate_key_update(**{
                c.name: c for c in stmt.inserted
                if c.name != 'id'
            })
            conn.execute(stmt)
            conn.commit()

        self.buffer[table_name] = []

    def close_spider(self, spider):
        # 爬虫结束时提交所有剩余数据
        for table_name in self.buffer.keys():
            self.flush(table_name)
        self.engine.dispose()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_url=crawler.settings.get('SQLALCHEMY_DATABASE_URI'),
            batch_size=crawler.settings.get('BATCH_SIZE', 100)
        )


class HttpPipeline(abc.ABC):
    def __init__(self, x_api):
        self.client = httpx.Client(verify=False, timeout=300)
        self.url = x_api + self.get_path()

    @abc.abstractmethod
    def get_path(self):
        pass

    def process_item(self, item, spider):
        self.client.post(self.url, json=dict(item))

    def close_spider(self, spider):
        self.client.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(x_api=crawler.settings.get('X_API'))


class MongoPipeline(abc.ABC):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = 'mongodb://' + mongo_uri
        self.mongo_db = mongo_db

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    @abc.abstractmethod
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'id': item['id']}, {'$set': item['content']}, True)
        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )
