from databox.pipelines import MongoPipeline


class TmallItemPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.name].update_one({'id': item['id']}, {'$set': item}, True)
        return item


class TmallSkuItemPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.name].update_one({'id': item['id']}, {'$set': item}, True)
        return item


class TmallRatePipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.name].update_one({'id': item['id']}, {'$set': item}, True)
        return item
