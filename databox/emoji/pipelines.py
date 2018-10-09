class FilePipeline:
    def open_spider(self, spider):
        self.f = open(spider.file_path, 'w')

    def close_spider(self, spider):
        self.f.close()

    def process_item(self, item, spider):
        self.f.write(f"{item['code']},{item['emoji']}\n")
        self.f.flush()
        return item
