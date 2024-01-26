from scrapy import Item, Field


class ImageItem(Item):
    img_title = Field()
    img_bytes = Field()


class AlipayQrcodeItem(ImageItem):
    mailto = Field()


class AlipayCookieItem(Item):
    cookies = Field()


class AlipayBillItem(Item):
    time = Field()
    title = Field()
    trade_np = Field()
    other = Field()
    amount = Field()
