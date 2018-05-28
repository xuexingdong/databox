from databox.pipelines import MongoPipeline


class UserPipeline(MongoPipeline):
    def process_item(self, item, spider):
        self.db['neteasemusic_user'].update_one({'id': item['id']}, {'$set': item}, True)
        return item
