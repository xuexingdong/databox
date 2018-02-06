from databox.pipelines import MongoPipeline


class PetPipeline(MongoPipeline):
    collection_name = 'pet'

    def process_item(self, item, spider):
        self.db[self.collection_name].update_one({'id': item['id']}, {'$set': item}, True)
        return item
