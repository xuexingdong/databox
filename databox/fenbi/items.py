from scrapy import Item, Field


class PaperItem(Item):
    paper_id = Field()
    name = Field()
    chapters = Field()
    materials = Field()
    questions = Field()


class MaterialItem(Item):
    material_id = Field()
    content = Field()


class QuestionItem(Item):
    question_id = Field()
    content = Field()
    chapter_name = Field()
    module = Field()
    option_type = Field()
    options = Field()
    answer = Field()
    material_ids = Field()
    paper_id = Field()
