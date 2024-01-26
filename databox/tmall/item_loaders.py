from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader


class TmallItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TmallSkuLoader(ItemLoader):
    default_output_processor = TakeFirst()


class TmallRateLoader(ItemLoader):
    default_output_processor = TakeFirst()
