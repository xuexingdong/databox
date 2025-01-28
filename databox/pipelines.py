import abc

import httpx
import pymongo


class HttpPipeline(abc.ABC):
    def __init__(self, x_api):
        self.client = httpx.Client(verify=False, timeout=300)
        self.url = x_api + self.get_path()

    @abc.abstractmethod
    def get_path(self):
        pass

    def process_item(self, item, spider):
        r = self.client.post(self.url, json=dict(item))

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
