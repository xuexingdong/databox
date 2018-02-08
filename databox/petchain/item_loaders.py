from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity


class PetLoader(ItemLoader):
    default_output_processor = TakeFirst()

    attributes_out = Identity()
