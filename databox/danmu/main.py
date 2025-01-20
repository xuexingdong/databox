import asyncio

from databox.danmu.douyu_danmu_client import DouyuDanmuClient

if __name__ == "__main__":
    client = DouyuDanmuClient()
    asyncio.run(client.start())
