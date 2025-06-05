import httpx


class SubmitMcpPipeline:
    url = 'https://mcp.so/api/submit-projects'

    def __init__(self):
        self.batch_size = 10
        self.batch_data = []
        self.client = httpx.Client(verify=False, timeout=300)

    def process_item(self, item, spider):
        self.batch_data.append(dict(item))  # 将数据添加到缓存
        if len(self.batch_data) >= self.batch_size:  # 缓存满了，提交数据
            self.commit_batch(spider)
        return item

    def commit_batch(self, spider):
        if not self.batch_data:
            return
        try:
            self.client.post(self.url, json=self.batch_data)
            spider.logger.info(f"Committed {len(self.batch_data)} items.")
        except Exception as e:
            spider.logger.error(f"Error committing batch: {e}")
        finally:
            self.batch_data.clear()

    def close_spider(self, spider):
        self.commit_batch(spider)
