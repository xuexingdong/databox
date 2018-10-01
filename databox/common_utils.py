from typing import Optional

import requests
from PIL import Image
from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol


def decode_qrcode_img_url(img_url: str) -> Optional[str]:
    r = requests.post('https://cli.im/Api/Browser/deqr', data={'data': img_url})
    res = r.json()
    if res['status'] != 1:
        return ''
    return res['data']['RawData']


def cut_qrcode_from_img(img: Image) -> Image:
    """
    裁剪出图片中的二维码图片
    :param img:
    :return:
    """
    decode_result = decode(img, ZBarSymbol.QRCODE, True)
    # 如果图中有二维码图片，则取第一张
    if decode_result:
        # 裁剪到二维码图片的位置
        x, y, w, h = decode_result[0][2]
        return img.crop((x, y, x + w, y + h))
