from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class TmallItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TmallSkuLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TmallRateLoader(ItemLoader):
    default_output_processor = TakeFirst()
