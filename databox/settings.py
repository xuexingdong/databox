import logging

BOT_NAME = 'databox'

SPIDER_MODULES = [
    'databox.petchain',
    'databox.tmall',
    'databox.wechat'
]

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'

DOWNLOAD_DELAY = 0.1
REDIS_URL = 'redis://127.0.0.1:6379'

# Enables scheduling storing requests queue in redis.
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

REDIS_START_URLS_KEY = '%(name)s:start_urls'

# mongo
MONGO_URI = '127.0.0.1:27017'
MONGO_DATABASE = 'crawler'

LOG_LEVEL = logging.DEBUG
