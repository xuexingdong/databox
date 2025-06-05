import logging

ROBOTSTXT_OBEY = False

COOKIES_ENABLED = True

BOT_NAME = 'databox'

SPIDER_MODULES = [
    'databox',
]

COMMANDS_MODULE = 'databox'

CONCURRENT_REQUESTS_PER_IP = 16
DOWNLOAD_DELAY = 0.25

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

SCHEDULER_PERSIST = True
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
REDIS_URL = 'redis://localhost:6379/0'

# DOWNLOAD_FAIL_ON_DATALOSS = False

# mongo
MONGO_URI = '127.0.0.1:27017'
MONGO_DATABASE = 'databox'

# LOG_FILE = 'data/log.txt'
LOG_LEVEL = logging.INFO

# 驱动路径
# CHROME_DRIVER_PATH = '/Users/xuexingdong/workspace/python/databox/chromedriver'
# CHROME_DRIVER_HEADLESS = True

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": False,
    "timeout": 30 * 1000
}