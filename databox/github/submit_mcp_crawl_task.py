import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import StrictRedis

from databox.github.github_repo_search_spider import GithubRepoSearchSpider, GithubRepoSearchMeta
from databox.pulsemcp.pulsemcp_mcp_client_spider import PulseMcpMcpClientSpider


class McpScheduler:
    def __init__(self, redis_url=None):
        self.r = StrictRedis.from_url(
            redis_url or os.getenv('REDIS_URL', 'redis://redis:6379/0'),
            decode_responses=True
        )
        print(f"Redis URL: {self.r.connection_pool.connection_kwargs}")
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
        self.scheduler.add_job(
            self.push_mcp_client_task,
            'cron',
            hour=1,
            minute=0,
            next_run_time=datetime.now(),
        )
        self.scheduler.add_job(
            self.push_mcp_server_task,
            'interval',
            hours=2,
            next_run_time=datetime.now(),
            args=[query]
        )
        self.scheduler.start()
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    scheduler = McpScheduler()
    try:
        asyncio.run(scheduler.run('mcp-server'))
    except (KeyboardInterrupt, SystemExit):
        pass
