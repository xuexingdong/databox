from itemloaders import Identity
from itemloaders.processors import TakeFirst


class PetLoader:
    default_output_processor = TakeFirst()

    attributes_out = Identity()
