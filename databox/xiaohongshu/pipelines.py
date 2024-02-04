from databox.pipelines import MongoPipeline


class UserPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'user_id': item['user_id']}, {'$set': item}, True)
        return item


class NotePipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'id': item['id']}, {'$set': item}, True)
        return item
