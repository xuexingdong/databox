import scrapy


class IdiomItem(scrapy.Item):
    # 成语词
    word = scrapy.Field()
    # 拼音
    pinyin = scrapy.Field()
    # 感情色彩
    emotion = scrapy.Field()
    # 近义词
    synonyms = scrapy.Field()
    # 反义词
    antonyms = scrapy.Field()
    # 意思
    meaning = scrapy.Field()
    # 出处
    origin = scrapy.Field()
    # 用法
    usage = scrapy.Field()
    # 例子
    example = scrapy.Field()
    # 辨析
    distinction = scrapy.Field()
    # 故事
    story = scrapy.Field()
    # 释义
    explanation = scrapy.Field()
    # 例句（列表）
    example_sentences = scrapy.Field()

    question_id = scrapy.Field()
