import json
import random
import re
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, urlencode

import httpx
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from databox.xiaohongshu.constants import PlatformCode, CodeStatus


@dataclass
class XhsResponse:
    code: int
    success: bool
    msg: Optional[int] = None
    data: Optional[dict] = None


@dataclass
class LoginInfo:
    user_id: str
    session: str
    secure_session: str


@dataclass
class QrCodeStatusResponse:
    code_status: CodeStatus
    login_info: LoginInfo = None


@dataclass
class XhsQrCode:
    code: str
    qr_id: str
    multi_flag: int
    url: str


class XhsClient:
    RC4_SECRET_VERSION = '1'
    LOCAL_ID_KEY = 'a1'
    # 小红书拼写成MINI_BROSWER_INFO_KEY了
    MINI_BROWSER_INFO_KEY = 'b1'
    VERSION = "3.6.8"

    X4_REGEX = r'x4:"(\d+\.\d+\.\d+)"'
    VENDOR_DYNAMIC_REGEX = r'<script src="([^"]*vendor-dynamic[^"]*\.js)"[^>]*>'

    CAPTCHA_URL = 'https://www.xiaohongshu.com/web-login/captcha'

    def __init__(self):

        def hook_request(request: httpx.Request, cookies=None):
            if request.content:
                data = json.loads(request.content)
            else:
                data = None
            if cookies is not None:
                cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                request.headers['cookie'] = cookie_str
            request.headers.update(self.get_xhs_headers(request.url, data))

        encrypt_js_path = 'encrypt.js'
        args = ['--disable-web-security', '--start-maximized']
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, args=args)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.366'
        context = browser.new_context(no_viewport=True, user_agent=user_agent)
        context.add_init_script(path=encrypt_js_path)
        page = context.new_page()
        stealth_sync(page)
        page.goto('https://www.xiaohongshu.com')
        vendor_dynamic_js_url = 'https://' + re.search(XhsClient.VENDOR_DYNAMIC_REGEX, page.content()).group(1)
        page.goto(vendor_dynamic_js_url)
        self.x4 = re.search(XhsClient.X4_REGEX, page.content()).group(1)

        page.goto('https://www.xiaohongshu.com')
        try:
            page.wait_for_function('typeof window._webmsxyw === "function"')
            page.wait_for_function(f'localStorage.getItem("{XhsClient.MINI_BROWSER_INFO_KEY}")')
        except Exception as e:
            print(e)
        self.page = page
        self.client = httpx.Client(headers={
            "User-Agent": user_agent,
            "Origin": "https://www.xiaohongshu.com",
            "Referer": "https://www.xiaohongshu.com/",
            "Content-Type": "application/json;charset=UTF-8"
        }, event_hooks={
            'request': [lambda request: hook_request(request, context.cookies())]})
        self.login_info = None

    def auto_rotate_captcha(self, params=None):
        self.page.goto(f'{self.CAPTCHA_URL}?{urlencode(params)}')
        self.page.wait_for_selector('#red-captcha-rotate')
        self.page.wait_for_selector('#red-captcha-rotate-bg')
        {
            "rid": "6e6681b1ad4a47dfb1a5795879a682b1",
            "verifyType": 102,
            "verifyBiz": "461",
            "verifyUuid": "e4f4a545-aecc-42a2-9cca-82d423737f0d*dkmfewty",
            "biz": "sns_web",
            "sourceSite": "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed",
            "version": "1.0.1",
            "captchaInfo": "{\"mouseEnd\":\"LzsGcjlcYK4=\",\"time\":\"hl2rMcVuN14=\",\"track\":\"JS68ffFcGnarpPAR7b+he/f71HkwjUH9bm7lYsnqErw+rCWg1cUxqH1SDpUXnry7oDLVXrKi+E3mE4jEF/libURUDu8GM7o73gskat1epfMYidwBghNQsjZzP14d0jnj+rhNY/WlKmTzYFpVctMyXuB5Oy6tXnZjoMczuD0xqWtEhyWTlD5dzBWl/TG4YXSBdPWxZwfjZYMMDpTxWLej3LowM2RxfrNndwiM8ar1lEV8QYMl3eVdbJfxx4fFcqzf4lXEnKFCGt89NWgE4EtP5P/opwd+9Zv5I1Lo5YHg2PYhmj4pdzq7lITnzmZe8K4HqyV1htY7LQS/EUDuYF6grexppUcvYqPn7iIqlN2jCqjfbQh93OU4sVnquVVG33k2ajyt5SCdMwlpsRqUSYjnOV2nQ/CBgbaLVKiSJQR65jVTzsJO/B2cFdUC+QZeJ2u49jMzWRwftpUI5h+KVsfzrm6jPINXQ40fqyW5M2s2uYvuCBmiHDTesn/UZDM7FP30VBnzVmfmQhv7yrGRwfECebFhDKpKixlpvRbf/aPzUfwFFAVbSg4/AA==\",\"width\":\"Yv/ZbBx9c9k=\"}"
        }
        # 宽336
        print(111111111111111)

    def create_qr_code(self) -> XhsQrCode:
        data = {
            "qr_type": 1
        }
        json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        response = self.client.post('https://edith.xiaohongshu.com/api/sns/web/v1/login/qrcode/create',
                                    content=json_data)
        response_json = response.json()
        return XhsQrCode(**XhsResponse(**response_json).data)

    def get_cookie_dict(self):
        return self.playwright_cookies_to_dict(self.page.context.cookies())

    def check_login(self):
        response = self.client.get('https://edith.xiaohongshu.com/api/sns/web/v2/user/me')
        response_json = response.json()
        xhs_response = XhsResponse(**response_json)
        if xhs_response.code == -1:
            return False
        return 'guest' not in xhs_response.data

    def query_qr_code_status(self, qr_id, code) -> (CodeStatus, LoginInfo):
        response = self.client.get(
            f'https://edith.xiaohongshu.com/api/sns/web/v1/login/qrcode/status?qr_id={qr_id}&code={code}')
        response_json = response.json()
        xhs_response = XhsResponse(**response_json)
        if xhs_response.code == -1:
            # 登录异常，异常后间隔几秒即可
            print(xhs_response)
            time.sleep(10)
            return CodeStatus.WAIT_SCAN, None
        if response.status_code == 471:
            # 471说明登录需要旋转验证码
            print(xhs_response)
            return CodeStatus.SUCCESS, None
        login_info = None
        if 'login_info' in xhs_response.data:
            login_info = LoginInfo(**xhs_response.data['login_info'])
        return CodeStatus(xhs_response.data['code_status']), login_info

    def wait_until_login(self, qr_code: XhsQrCode, interval: int = 2):
        code_status, login_info = self.query_qr_code_status(qr_code.qr_id, qr_code.code)
        match code_status:
            case CodeStatus.WAIT_SCAN | CodeStatus.SCANNED:
                time.sleep(interval)
                self.wait_until_login(qr_code)
                return False
            case CodeStatus.SUCCESS:
                self.login_info = login_info
                return True
            case CodeStatus.EXPIRED:
                # 5分钟过期
                print('expired')
                return False

    def get_xhs_headers(self, url: str, data: dict = None) -> dict:
        parsed_url = urlparse(str(url))
        path_with_query = parsed_url.path + ('?' + parsed_url.query if parsed_url.query else '')
        try:
            res = self.page.evaluate("([url, data]) => window._webmsxyw(url, data)", [str(path_with_query), data])
        except Exception as e:
            print(e)
        x_t = res["X-t"]
        x_s = res["X-s"]
        cookies = self.page.context.cookies()
        local_id = next((cookie['value'] for cookie in cookies if cookie['name'] == XhsClient.LOCAL_ID_KEY), None)
        try:
            mini_browser_info = self.page.evaluate(f'localStorage.getItem("{XhsClient.MINI_BROWSER_INFO_KEY}")')
        except Exception as e:
            print(e)
        x_s_common = self.get_x_s_common(x_t, x_s, XhsClient.get_sig_count(x_t and x_s or ""),
                                         local_id, mini_browser_info)
        headers = {
            'X-T': str(x_t),
            'X-S': x_s,
            'X-S-Common': x_s_common,
            'X-B3-Traceid': XhsClient.generate_x_b3_traceid(),
        }
        return headers

    def get_x_s_common(self, x_t, x_s, x_sign, local_id, mini_browser_info):
        """
        var u = e.headers["X-t"] || ""
          , s = e.headers["X-s"] || ""
          , c = e.headers["X-Sign"] || ""
          , l = getSigCount(u && s || c)
          , f = localStorage.getItem(MINI_BROWSER_INFO_KEY)
          , p = localStorage.getItem(RC4_SECRET_VERSION_KEY) || RC4_SECRET_VERSION
          , h = {
            s0: getPlatformCode(o),
            s1: "",
            x0: p,
            x1: version,
            x2: o || "PC",
            x3: "xhs-pc-web",
            x4: "4.0.6",
            x5: js_cookie.Z.get(LOCAL_ID_KEY),
            x6: u,
            x7: s,
            x8: f,
            x9: encrypt_mcr(concat_default()(r = concat_default()(n = "".concat(u)).call(n, s)).call(r, f)),
            x10: l
        };
        e.headers["X-S-Common"] = encrypt_b64Encode(encrypt_encodeUtf8(stringify_default()(h)))

        :param x_t:
        :param x_s:
        :param x_sign:
        :param local_id:
        :param mini_browser_info:
        :return:
        """

        h = {
            's0': PlatformCode.other.value,
            's1': '',
            'x0': XhsClient.RC4_SECRET_VERSION,
            'x1': XhsClient.VERSION,
            'x2': PlatformCode.Windows.value or 'PC',
            'x3': 'xhs-pc-web',
            'x4': self.x4,
            'x5': local_id,
            'x6': x_t,
            'x7': x_s,
            'x8': mini_browser_info,
            'x9': self.page.evaluate(f'encrypt_mcr("{str(x_t) + x_s + mini_browser_info}")'),
            'x10': x_sign
        }
        print(h)
        return self.page.evaluate(f'encrypt_b64Encode(encrypt_encodeUtf8(JSON.stringify({h})))')

    def get_sig_count(self):
        """
        function getSigCount(t) {
            var e = Number(sessionStorage.getItem(SIGN_COUNT_KEY)) || 0;
            return t && (e++,
            sessionStorage.setItem(SIGN_COUNT_KEY, e.toString())),
            e
        }
        :return:
        """
        return 1

    @staticmethod
    def generate_search_id():
        e = int(time.time() * 1000) << 64
        t = int(random.uniform(0, 2147483646))
        return XhsClient.__to_base_36((e + t))

    @staticmethod
    def generate_x_b3_traceid():
        characters = "abcdef0123456789"
        return ''.join(random.choice(characters) for _ in range(16))

    @staticmethod
    def __to_base_36(number):
        """
        AI generated
        :param number:
        :return:
        """
        if not isinstance(number, int):
            raise ValueError("Input must be an integer")

        if number == 0:
            return '0'

        digits = '0123456789abcdefghijklmnopqrstuvwxyz'
        result = ''

        while number:
            number, remainder = divmod(number, 36)
            result = digits[remainder] + result

        return result

    @staticmethod
    def playwright_cookies_to_dict(cookies):
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict

    @staticmethod
    def handle_post_data(data):
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
