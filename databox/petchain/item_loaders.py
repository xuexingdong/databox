from scrapy.loader.processors import TakeFirst, Identity


class PetLoader:
    default_output_processor = TakeFirst()

    attributes_out = Identity()
