import hashlib
import uuid

import requests
from scrapy.exceptions import DropItem

from databox import utils


class QRCodePipeline:
    def open_spider(self, spider):
        self.pic_set = set()
        self.qrcode_img_md5_set = set()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            if pic_url not in self.pic_set:
                self.pic_set.add(pic_url)
                # 二维码所指向的链接
                qrcode_url = common_utils.decode_qrcode_img_url(pic_url)
                if not qrcode_url:
                    continue
                # 群组二维码
                if '/g/' in qrcode_url:
                    sub_path = '/group'
                # 个人二维码
                elif 'u.' in qrcode_url:
                    sub_path = '/user'
                # 公众号
                elif '/q/' in qrcode_url:
                    raise DropItem
                # 其他
                else:
                    spider.logger.info(f"url {pic_url} is not legal qrcode img")
                    raise DropItem
                content = requests.get(pic_url).content
                qrcode_img_md5 = hashlib.md5(content).hexdigest()
                # 对图片的md5去重
                if qrcode_img_md5 not in self.qrcode_img_md5_set:
                    uuid_ = uuid.uuid4()
                    with open(f"data/imgs{sub_path}/{uuid_}.jpg", 'wb') as fout:
                        fout.write(content)
        return item
