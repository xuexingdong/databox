from io import BytesIO

import requests
from PIL import Image
from pyzbar.pyzbar import decode

if __name__ == '__main__':
    with open('replys.txt') as f:
        with open('qrcode_pics.txt', 'w+') as fout:
            for line in f:
                content = Image.open(BytesIO(requests.get(line.strip()).content))
                decode_result = decode(content, None, True)
                if decode_result:
                    print(str(decode_result[0].data, encoding='utf-8'))
                    fout.write(line)
                    fout.flush()
                else:
                    print(f'url {line.strip()} 解析不出二维码')
