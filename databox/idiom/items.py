import scrapy


class IdiomItem(scrapy.Item):
    # 成语词
    word = scrapy.Field()
    # 拼音
    pinyin = scrapy.Field()
    # 感情色彩
    emotion = scrapy.Field()
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
    # 最后更新时间
    last_update_time = scrapy.Field()