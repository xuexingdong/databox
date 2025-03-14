class InsUserPipeline:
    def process_item(self, item, spider):
        if 'imdb_rating' in item:
            item['imdb_rating'] = float(item['imdb_rating'][:3])
        if 'douban_rating' in item:
            item['douban_rating'] = float(item['douban_rating'][:3])
        self.db[spider.collection].update_one({'translate_name': item['translate_name']}, {'$set': item}, True)
        return item
