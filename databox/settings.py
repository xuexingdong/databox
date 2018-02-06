# -*- coding: utf-8 -*-

# Scrapy settings for databox project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import logging

BOT_NAME = 'databox'

# SPIDER_MODULES = ['databox.spiders']
NEWSPIDER_MODULE = 'databox.petchain'

REDIS_URL = 'redis://127.0.0.1:6379'

# Enables scheduling storing requests queue in redis.
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'

# Ensure all spiders share same duplicates filter through redis.
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'

REDIS_START_URLS_KEY = '%(name)s:start_urls'

MONGO_URI = 'mongodb://127.0.0.1:27017'
MONGO_DATABASE = 'crawler'

LOG_LEVEL = logging.DEBUG

DOWNLOAD_DELAY = 0.1
