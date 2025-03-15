import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import StrictRedis

from databox.github.github_repo_search_spider import GithubRepoSearchSpider, GithubRepoSearchMeta
from databox.pulsemcp.pulsemcp_mcp_client_spider import PulseMcpMcpClientSpider


class McpScheduler:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.r = StrictRedis.from_url(redis_url, decode_responses=True)
        self.scheduler = AsyncIOScheduler()

    async def push_mcp_server_task(self, query):
        meta_redis = await self.r.get(f"{GithubRepoSearchSpider.redis_key}:meta:{query}")
        if meta_redis:
            meta = GithubRepoSearchMeta.model_validate_json(meta_redis)
        else:
            meta = GithubRepoSearchMeta(q=query)
        await self.r.rpush(
            GithubRepoSearchSpider.redis_key,
            meta.model_dump_json(exclude_none=True)
        )

    async def push_mcp_client_task(self):
        await self.r.rpush(PulseMcpMcpClientSpider.redis_key, '')

    async def run(self, query: str):
        """启动调度器"""
        # self.scheduler.add_job(
        #     self.push_mcp_client_task,
        #     'interval',
        #     hours=2,
        #     next_run_time=datetime.now(),
        # )
        self.scheduler.add_job(
            self.push_mcp_server_task,
            'interval',
            hours=2,
            next_run_time=datetime.now(),
            args=[query]
        )
        try:
            self.scheduler.start()
            # 保持程序运行
            await asyncio.get_event_loop().create_future()
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
        except Exception as e:
            print(f"调度器错误: {e}")
            self.scheduler.shutdown()


if __name__ == '__main__':
    scheduler = McpScheduler()
    asyncio.run(scheduler.run('mcp-server'))
