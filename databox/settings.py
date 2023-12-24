BOT_NAME = 'databox'

SPIDER_MODULES = [
    'databox',
]

COMMANDS_MODULE = 'databox'

CONCURRENT_REQUESTS_PER_IP = 16
DOWNLOAD_DELAY = 0.25

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'

# redis
# REDIS_URL = 'redis://127.0.0.1:6379'
# Enables scheduling storing requests queue in redis.
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
# Ensure all spiders share same duplicates filter through redis.
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# REDIS_START_URLS_KEY = '%(name)s:start_urls'

# DOWNLOAD_FAIL_ON_DATALOSS = False

# mongo
MONGO_URI = '127.0.0.1:27017'
MONGO_DATABASE = 'crawler'

# LOG_FILE = 'data/log.txt'
# LOG_LEVEL = logging.INFO

# 驱动路径
# CHROME_DRIVER_PATH = '/Users/xuexingdong/workspace/python/databox/chromedriver'
# CHROME_DRIVER_HEADLESS = True
