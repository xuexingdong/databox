class TopicPipeline:
    def open_spider(self, spider):
        self.pic_set = set()
        self.file = open('data/topics.txt', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            if pic_url not in self.pic_set:
                self.pic_set.add(pic_url)
                self.file.write(pic_url + '\n')
                self.file.flush()
        return item


class ReplyPipeline:
    def open_spider(self, spider):
        self.pic_set = set()
        self.file = open('data/replys.txt', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            if pic_url not in self.pic_set:
                self.pic_set.add(pic_url)
                self.file.write(pic_url + '\n')
                self.file.flush()
        return item
