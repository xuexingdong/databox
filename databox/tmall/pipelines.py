from databox.pipelines import MongoPipeline
from databox.tmall.items import TmallItem, TmallSkuItem


class TmallItemPipeline(MongoPipeline):
    def process_item(self, item, spider):
        if isinstance(item, TmallItem):
            self.db['tmall_item'].update_one({'id': item['id']}, {'$set': item}, True)
        return item


class TmallSkuItemPipeline(MongoPipeline):
    def process_item(self, item, spider):
        if isinstance(item, TmallSkuItem):
            self.db['tmall_sku_item'].update_one({'id': item['id']}, {'$set': item}, True)
        return item


class TmallRatePipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db[spider.name].update_one({'id': item['id']}, {'$set': item}, True)
        return item
