import httpx


class IdiomPipeline:
    url = 'http://localhost:8081/land/idioms/add'

    def __init__(self):
        self.client = httpx.Client(verify=False, timeout=300)

    def process_item(self, item, spider):
        self.client.post(self.url, json=dict(item))

    def close_spider(self, spider):
        self.client.close()
