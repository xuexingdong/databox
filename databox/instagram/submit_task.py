import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import StrictRedis

from databox.instagram.ins_user_spider import InsUserSpider, InsUserData


class InsScheduler:
    def __init__(self, redis_url='redis://redis:6379'):
        self.r = StrictRedis.from_url(redis_url, decode_responses=True)
        self.scheduler = AsyncIOScheduler()

    async def push_ins_user_task(self, user_name):
        await self.r.rpush(InsUserSpider.redis_key, InsUserData(username=user_name).model_dump_json())

    async def run(self, username: str):
        """启动调度器"""
        self.scheduler.add_job(
            self.push_ins_user_task,
            'cron',
            hour=1,
            minute=0,
            next_run_time=datetime.now(),
            args=[username]
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
    scheduler = InsScheduler()
    asyncio.run(scheduler.run('realdonaldtrump'))
