from databox.pipelines import MongoPipeline


class PetPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db['pet'].update_one({'id': item['id']}, {'$set': item}, True)
        return item
