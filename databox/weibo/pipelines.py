from databox.pipelines import MongoPipeline


class ProfilePipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'id': item['id']}, {'$set': item['content']}, True)
        return item


class MBlogPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'id': item['id']}, {'$set': item['content']}, True)
        return item


class CommentPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.collection].update_one({'id': item['id']}, {'$set': item['content']}, True)
        return item
