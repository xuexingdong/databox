import abc

import pymongo


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
