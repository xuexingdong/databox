from databox.icloud.items import LocationItem
from databox.pipelines import MongoPipeline


class LocationPipeline(MongoPipeline):
    def process_item(self, item, spider):
        if isinstance(item, LocationItem):
            self.db['location'].insert(dict(item))
        return item
