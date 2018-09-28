import hashlib
import uuid
from io import BytesIO

import requests
from PIL import Image
from pyzbar.pyzbar import decode
from scrapy.exceptions import DropItem


class QRCodePipeline:
    def open_spider(self, spider):
        self.pic_set = set()
        self.pic_md5_set = set()

    def process_item(self, item, spider):
        for pic_url in item['pic_urls']:
            if pic_url not in self.pic_set:
                content = requests.get(pic_url).content
                img_md5 = hashlib.md5(content).hexdigest()
                if img_md5 not in self.pic_md5_set:
                    # 识别是否是二维码
                    img = Image.open(BytesIO(content))
                    qrcode_img = self._get_qrcode_in_img(img)
                    if qrcode_img:
                        continue
                    # 裁剪后判断颜色是否超过两种
                    if len(qrcode_img.getcolors()) > 2:
                        raise DropItem
                    self.pic_md5_set.add(img_md5)
                    self.pic_set.add(pic_url)
                    uuid_ = uuid.uuid4()
                    with open(f'imgs/{uuid_}.jpg', 'wb') as fout:
                        fout.write(content)
        return item

    def _get_qrcode_in_img(self, img):
        decode_result = decode(img, None, True)
        # 如果图中有二维码图片，则取第一张
        if decode_result:
            # 裁剪到二维码图片的位置
            x, y, w, h = decode_result[0][2]
            return img.crop((x, y, x + w, y + h))
