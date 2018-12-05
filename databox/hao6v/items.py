from scrapy import Item, Field


class MovieItem(Item):
    # 映射信息
    translate_name = Field()  # 译名
    name = Field()  # 片名
    year = Field()  # 年代
    region = Field()  # 产地
    category = Field()  # 类别
    language = Field()  # 语言
    subtitles = Field()  # 字幕
    release_date = Field()  # 上映日期
    imdb_rating = Field()  # imdb评分
    douban_rating = Field()  # 豆瓣评分
    length = Field()  # 片长
    director = Field()  # 导演
    starring = Field()  # 主演

    # 单独解析
    introduction = Field()  # 简介
    cover = Field()  # 封面
    source_url = Field()  # 爬取链接
    download_urls = Field()  # 下载链接
    ts = Field()  # 爬取时间
    pv = Field()
