import os
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright


class WechatVideoSpider:
    def __init__(self):
        self.client = httpx.Client(verify=False, timeout=300)
        self.current_dir = Path(__file__).resolve().parent
        self.html = os.path.join(self.current_dir, 'wasm_video_decode.html')

    def crawl(self, data):
        object_id = data["object"]["id"]
        media = data["object"]["object_desc"]["media"][0]
        media_url: str = media["url"] + media["url_token"]
        origin_mp4_name = os.path.join(self.current_dir, object_id + '.mp4')
        if not os.path.exists(origin_mp4_name):
            with self.client.stream("GET", media_url) as r:
                with open(origin_mp4_name, 'wb') as f:
                    i = 1
                    for chunk in r.iter_bytes(chunk_size=10 * 1024 * 1024):
                        if chunk:
                            print(i)
                            f.write(chunk)
                            f.flush()
                            i += 1
        decode_dict = self.get_decode_dict(media['decode_key'])
        decode_array = [int(decode_dict[str(i)]) for i in range(len(decode_dict))]
        output_mp4_name = (os.path.join(self.current_dir, object_id + '_decoded.mp4'))
        if not os.path.exists(output_mp4_name):
            WechatVideoSpider.xor_with_mp4(origin_mp4_name, output_mp4_name, decode_array)
        subtitle_content = WechatVideoSpider.parse_with_whisper(output_mp4_name)
        return {
            'subtitle': subtitle_content
        }

    def get_decode_dict(self, decode_key):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        context = browser.new_context(no_viewport=True, user_agent=user_agent)
        page = context.new_page()
        page.goto(f'file:///{self.html}')
        page.wait_for_function('typeof Module !== "undefined" && typeof Module.WxIsaac64 === "function"')
        # 执行自定义 JavaScript 代码
        return page.evaluate(f"getDecryptionArray('{decode_key}')")

    def close(self):
        self.client.close()

    @staticmethod
    def parse_with_whisper(file_name):
        # model = whisper.load_model("base")
        # print('load ok')
        # result = model.transcribe(file_name, initial_prompt='以下是普通话的句子。')
        # print('result ok')
        # return result["text"]
        return ''

    @staticmethod
    def xor_with_mp4(input_mp4, output_mp4, decode_array):
        with open(input_mp4, 'rb') as input_file:
            mp4_bytes = bytearray(input_file.read())

        # 简单的异或操作，你可能需要根据实际需求调整
        for i in range(len(decode_array)):
            mp4_bytes[i] ^= decode_array[i]

        with open(output_mp4, 'wb') as output_file:
            output_file.write(mp4_bytes)
