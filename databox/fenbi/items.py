from scrapy import Item, Field


class PaperItem(Item):
    out_paper_id = Field()
    name = Field()
    question_count = Field()
    chapters = Field()
    materials = Field()
    questions = Field()


class MaterialItem(Item):
    out_material_id = Field()
    content = Field()


class QuestionItem(Item):
    out_question_id = Field()
    content = Field()
    option_type = Field()
    options = Field()
    answer = Field()
    material_indexes = Field()


class ChapterItem(Item):
    name = Field()
    desc = Field()
    question_count = Field()
