class TopicPipeline:
    def open_spider(self, spider):
        self.file = open('data/topics.txt', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            self.file.write(pic_url + '\n')
            self.file.flush()
        return item


class ReplyPipeline:
    def open_spider(self, spider):
        self.file = open('data/replys.txt', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            self.file.write(pic_url + '\n')
            self.file.flush()
        return item
