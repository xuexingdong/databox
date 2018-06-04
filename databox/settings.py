import logging

BOT_NAME = 'databox'

SPIDER_MODULES = [
    'databox',
]

COMMANDS_MODULE = 'databox'

CONCURRENT_REQUESTS_PER_IP = 16
DOWNLOAD_DELAY = 0.3

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

# redis
REDIS_URL = 'redis://127.0.0.1:6379'
# Enables scheduling storing requests queue in redis.
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
REDIS_START_URLS_KEY = '%(name)s:start_urls'

# mongo
MONGO_URI = '127.0.0.1:27017'
MONGO_DATABASE = 'crawler'

LOG_LEVEL = logging.INFO
