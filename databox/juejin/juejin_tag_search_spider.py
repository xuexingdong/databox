import hashlib
from urllib.parse import urlencode

import arrow
from scrapy import Spider, Request


class JuejinTagSpider(Spider):
    name = 'juejin_tag'

    API_HOST = 'https://api.leancloud.cn'
    API_VERSION = '1.1'

    # 掘金在leancloud的APP_ID和APP_KEY，以及一个和有关JS的标识
    # APP_ID可以在请求头中看到，每次都是一样的
    # APP_KEY 需要对vendor.js进行断点分析
    # AV是固定开头,js1.5.4具体含义不明，反正是个常量
    APP_ID = 'mhke0kuv33myn4t4ghuid4oq2hjj12li374hvcif202y5bm6'
    APP_KEY = 'mldfccqgjjmsk3xumif9j0qgls0vq6f2g7r3abouitfyboci'
    X_LC_UA = 'AV/js1.5.4'

    SEARCH_BY_TAG = API_HOST + '/' + API_VERSION + '/classes/Entry'

    def start_requests(self):
        tag = 'Vue.js'
        params = {
            'where':   '{"tagsTitleArray":{"$in":["' + tag + '"]}}',
            'include': 'user',
            'limit':   20,
            'skip':    0,
            'order':   '-rankIndex'
        }
        # X-LC-Sign 的值是由 sign,timestamp[,master] 组成的字符串。
        # 将 timestamp 加上 App Key 或 Master Key 组成的字符串，再对它做 MD5 签名后的结果。
        m = hashlib.md5()
        # 其实随便传一个不为空的字符串都行，比如timestamp_13 = '1'也是可以通过验证的
        timestamp_13 = str(int(arrow.now().float_timestamp * 1000))
        m.update((timestamp_13 + self.APP_KEY).encode())
        sign = m.hexdigest()
        # 带上这三个需要验证的请求头
        headers = {
            'X-LC-Id':   self.APP_ID,
            'X-LC-Sign': sign + ',' + timestamp_13,
            'X-LC-UA':   self.X_LC_UA
        }
        yield Request(self.SEARCH_BY_TAG + '?' + urlencode(params), headers=headers, meta={
            'params': params
        })

    def parse(self, response):
        print(response.text)
        params = response.meta.params
        params['skip'] += params['limit']
        yield Request(self.SEARCH_BY_TAG + '?' + urlencode(params), headers=response.request.headers)
