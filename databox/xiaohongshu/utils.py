import base64
import ctypes
import json
import random
import time

from playwright.sync_api import sync_playwright

from databox.xiaohongshu.constants import PlatformCode


class XiaohongshuUtil:
    RC4_SECRET_VERSION = '1'
    LOCAL_ID_KEY = 'a1'
    # 小红书拼写成MINI_BROSWER_INFO_KEY了
    MINI_BROWSER_INFO_KEY = 'b1'
    VERSION = "3.6.8"

    @staticmethod
    def get_xiaohongshu_headers(url, data):
        stealth_js_path = './stealth.min.js'
        args = ['--disable-web-security', '--start-maximized']
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, args=args)
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        context = browser.new_context(no_viewport=True, user_agent=user_agent, extra_http_headers={
            'Access-Control-Allow-Origin': '*',
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            'Cache-Control': 'no-cache'
        })
        context.add_init_script(stealth_js_path)
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
        page = context.new_page()
        page.goto('https://www.xiaohongshu.com')
        page.wait_for_function('typeof window._webmsxyw === "function"')
        res = page.evaluate("([url, data]) => window._webmsxyw(url, data)", [url, data])
        x_t = res["X-t"]
        x_s = res["X-s"]
        cookies = context.cookies()
        local_id = next((cookie['value'] for cookie in cookies if cookie['name'] == XiaohongshuUtil.LOCAL_ID_KEY), None)
        mini_browser_info = next(
            (cookie['value'] for cookie in cookies if cookie['name'] == XiaohongshuUtil.MINI_BROWSER_INFO_KEY), None)
        x_s_common = XiaohongshuUtil.get_x_s_common(x_t, x_s, XiaohongshuUtil.get_sig_count(x_t and x_s or ""),
                                                    local_id, mini_browser_info)
        return {
            'X-T': x_t,
            'X-S': x_s,
            'X-S-Common': x_s_common,
            'X-B3-Traceid': XiaohongshuUtil.generate_x_b3_traceid(),
        }

    @staticmethod
    def get_x_s_common(x_t, x_s, x_sign, local_id, mini_browser_info):
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
            's0': PlatformCode.Windows.value,
            's1': '',
            'x0': XiaohongshuUtil.RC4_SECRET_VERSION,
            'x1': XiaohongshuUtil.VERSION,
            'x2': PlatformCode.Windows.value or 'PC',
            'x3': 'xhs-pc-web',
            'x4': '4.1.2',
            'x5': local_id,
            'x6': x_t,
            'x7': x_s,
            'x8': mini_browser_info,
            'x9': XiaohongshuUtil.mrc(str(x_t) + x_s),
            'x10': x_sign
        }
        return base64.b64encode(json.dumps(h).encode('utf-8')).decode()

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

    def __base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        """Converts an integer to a base36 string."""
        if not isinstance(number, int):
            raise TypeError('number must be an integer')

        base36 = ''
        sign = ''

        if number < 0:
            sign = '-'
            number = -number

        if 0 <= number < len(alphabet):
            return sign + alphabet[number]

        while number != 0:
            number, i = divmod(number, len(alphabet))
            base36 = alphabet[i] + base36

        return sign + base36

    @staticmethod
    def generate_search_id():
        e = int(time.time() * 1000) << 64
        t = int(random.uniform(0, 2147483646))
        return XiaohongshuUtil.__to_base_36((e + t))

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
    def mrc(e):
        ie = [
            0, 1996959894, 3993919788, 2567524794, 124634137, 1886057615, 3915621685,
            2657392035, 249268274, 2044508324, 3772115230, 2547177864, 162941995,
            2125561021, 3887607047, 2428444049, 498536548, 1789927666, 4089016648,
            2227061214, 450548861, 1843258603, 4107580753, 2211677639, 325883990,
            1684777152, 4251122042, 2321926636, 335633487, 1661365465, 4195302755,
            2366115317, 997073096, 1281953886, 3579855332, 2724688242, 1006888145,
            1258607687, 3524101629, 2768942443, 901097722, 1119000684, 3686517206,
            2898065728, 853044451, 1172266101, 3705015759, 2882616665, 651767980,
            1373503546, 3369554304, 3218104598, 565507253, 1454621731, 3485111705,
            3099436303, 671266974, 1594198024, 3322730930, 2970347812, 795835527,
            1483230225, 3244367275, 3060149565, 1994146192, 31158534, 2563907772,
            4023717930, 1907459465, 112637215, 2680153253, 3904427059, 2013776290,
            251722036, 2517215374, 3775830040, 2137656763, 141376813, 2439277719,
            3865271297, 1802195444, 476864866, 2238001368, 4066508878, 1812370925,
            453092731, 2181625025, 4111451223, 1706088902, 314042704, 2344532202,
            4240017532, 1658658271, 366619977, 2362670323, 4224994405, 1303535960,
            984961486, 2747007092, 3569037538, 1256170817, 1037604311, 2765210733,
            3554079995, 1131014506, 879679996, 2909243462, 3663771856, 1141124467,
            855842277, 2852801631, 3708648649, 1342533948, 654459306, 3188396048,
            3373015174, 1466479909, 544179635, 3110523913, 3462522015, 1591671054,
            702138776, 2966460450, 3352799412, 1504918807, 783551873, 3082640443,
            3233442989, 3988292384, 2596254646, 62317068, 1957810842, 3939845945,
            2647816111, 81470997, 1943803523, 3814918930, 2489596804, 225274430,
            2053790376, 3826175755, 2466906013, 167816743, 2097651377, 4027552580,
            2265490386, 503444072, 1762050814, 4150417245, 2154129355, 426522225,
            1852507879, 4275313526, 2312317920, 282753626, 1742555852, 4189708143,
            2394877945, 397917763, 1622183637, 3604390888, 2714866558, 953729732,
            1340076626, 3518719985, 2797360999, 1068828381, 1219638859, 3624741850,
            2936675148, 906185462, 1090812512, 3747672003, 2825379669, 829329135,
            1181335161, 3412177804, 3160834842, 628085408, 1382605366, 3423369109,
            3138078467, 570562233, 1426400815, 3317316542, 2998733608, 733239954,
            1555261956, 3268935591, 3050360625, 752459403, 1541320221, 2607071920,
            3965973030, 1969922972, 40735498, 2617837225, 3943577151, 1913087877,
            83908371, 2512341634, 3803740692, 2075208622, 213261112, 2463272603,
            3855990285, 2094854071, 198958881, 2262029012, 4057260610, 1759359992,
            534414190, 2176718541, 4139329115, 1873836001, 414664567, 2282248934,
            4279200368, 1711684554, 285281116, 2405801727, 4167216745, 1634467795,
            376229701, 2685067896, 3608007406, 1308918612, 956543938, 2808555105,
            3495958263, 1231636301, 1047427035, 2932959818, 3654703836, 1088359270,
            936918000, 2847714899, 3736837829, 1202900863, 817233897, 3183342108,
            3401237130, 1404277552, 615818150, 3134207493, 3453421203, 1423857449,
            601450431, 3009837614, 3294710456, 1567103746, 711928724, 3020668471,
            3272380065, 1510334235, 755167117,
        ]
        o = -1

        def right_without_sign(num, bit=0) -> int:
            val = ctypes.c_uint32(num).value >> bit
            MAX32INT = 4294967295
            return (val + (MAX32INT + 1)) % (2 * (MAX32INT + 1)) - MAX32INT - 1

        for n in range(57):
            o = ie[(o & 255) ^ ord(e[n])] ^ right_without_sign(o, 8)
        return o ^ -1 ^ 3988292384
