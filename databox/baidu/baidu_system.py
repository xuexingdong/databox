import base64
import os
import pathlib
import random
import time
from math import floor

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from requests_html import HTMLSession, HTMLResponse
from selenium.webdriver.chrome import webdriver


class BaiduSystem:
    # 百度账号域名
    PASSPORT_HOST = 'https://passport.baidu.com'
    # 百度账号首页
    URL_HOMEPAGE = PASSPORT_HOST + '/v2/?login'
    # 获取token
    URL_TOKEN = PASSPORT_HOST + '/v2/api/?getapi'
    # 预检查登录相关信息，可以看出需不需要验证码
    URL_CHECK_LOGIN = PASSPORT_HOST + '/v2/api/?logincheck'
    # 获取rsa加密公钥
    URL_PUBLIC_KEY = PASSPORT_HOST + '/v2/getpublickey'
    # 查看验证码
    URL_VERIFYCODE_IMG = PASSPORT_HOST + '/cgi-bin/genimage?{codestring}'
    # 更换验证码
    URL_CHANGE_VERIFYCODE_IMG = PASSPORT_HOST + '/v2/?reggetcodestr&token={token}&tpl=pp&apiver=v3&vcodetype={vcodetype}'
    # 校验验证码
    URL_CHECK_VCODE = PASSPORT_HOST + '/v2/?checkvcode'
    # 具体登录的地址
    URL_LOGIN = PASSPORT_HOST + '/v2/api/?login'

    # 百度fingerprint.js，浏览器指纹生成的一个唯一标识，目前尚未破解，设为一个固定值即可。

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }

    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.session = HTMLSession()
        # 访问首页，获取必要cookie
        self.session.get(self.URL_HOMEPAGE)
        # 生成gid
        self.gid = self.gen_gid()

    def login(self, username, password, tpl='pp', apiver='v3'):
        """
        登录百度账号 关键是token和cookie的BAIDUID要对应，dv要符合规则
        :param username: 手机/邮箱/用户名
        :param password: 密码
        :param tpl: 登录模板，默认pp代表passport这个地址
        :param apiver: 登录的api版本，目前是v3
        :return:
        """
        init_tt = self._get_13_timestamp()
        token = self.get_token(tpl, apiver)
        if not token:
            return False
        rsa_key, pubkey = self.get_key_and_pubkey(token, apiver)
        if not pubkey:
            return False
        rsa_password = self.rsa_password(password, pubkey)
        post_data = {
            'staticpage':   'https://passport.baidu.com/static/passpc-account/html/v3Jump.html',
            'charset':      'UTF-8',
            'token':        token,
            'tpl':          tpl,
            'subpro':       '',
            'apiver':       apiver,
            'codestring':   '',
            'safeflg':      0,
            'u':            self.PASSPORT_HOST,
            'isPhone':      '',
            'detect':       1,
            'gid':          self.gid,
            'quick_user':   0,
            'logintype':    'basicLogin',
            'logLoginType': 'pc_loginBasic',
            'idc':          '',
            'loginmerge':   True,
            'username':     username,
            'password':     rsa_password,
            'mem_pass':     'on',
            'rsakey':       rsa_key,
            'crypttype':    12,
            'loginversion': 'v4',
            'countrycode':  '',
            'callback':     '',
        }
        dv = self.get_dv(self.driver_path)
        codestring, vcodetype = self.check_login(token, tpl, apiver, username, dv)
        fp_uid = self.gen_fp_uid()
        # 需要验证码
        if codestring:
            # TODO
            vcodetype = vcodetype
            image_content = self.session.get(self.URL_VERIFYCODE_IMG.format(codestring=codestring)).content
            with open(username + '.jpg', 'wb') as f:
                f.write(image_content)
            verifycode = input("Enter your verifycode: ")
            post_data['codestring'] = codestring
            post_data['verifycode'] = verifycode
            self.session.cookies['FP_UID'] = fp_uid
            # 验证码检查
            if not self.check_vcode(token, verifycode, codestring):
                return False
        # TODO 这是指登录的时间，必须等至少10秒，否则触发错误码120021，等待的过程如何破解
        time.sleep(10)
        login_tt = self._get_13_timestamp()
        post_data['tt'] = login_tt
        post_data['ppui_logintime'] = login_tt - init_tt
        post_data['dv'] = dv
        post_data['fp_uid'] = fp_uid
        post_data['fp_info'] = ''

        r = self.session.post(self.URL_LOGIN, data=post_data, headers=self.HEADERS)
        print(r.text)
        return r.text.find('err_no=0')

    def get_username(self):
        # TODO
        r = requests.get('https://passport.baidu.com/center', cookies=self.session.cookies)
        r.encoding = 'utf-8'
        return r.text

    def get_token(self, tpl, apiver):
        # 把访问token接口的时间作为初始时间，后面计算ppui_logintime的时候需要
        params = {
            'tpl':          tpl,
            'apiver':       apiver,
            'tt':           self._get_13_timestamp(),
            'class':        'login',
            'gid':          self.gid,
            'loginversion': 'v4',
            'logintype':    'basicLogin'
        }
        r: HTMLResponse = self.session.get(self.URL_TOKEN, params=params)
        token = r.html.search('\"token\" : \"{}\"')[0]
        return token

    def check_login(self, token, tpl, apiver, username, dv):
        params = {
            'tpl':          tpl,
            'token':        token,
            'apiver':       apiver,
            'sub_source':   'leadsetpwd',
            'username':     username,
            'loginversion': 'v4',
            'dv':           dv
        }
        r: HTMLResponse = self.session.get(self.URL_CHECK_LOGIN, params=params)
        res = r.json()
        return res['data']['codeString'], res['data']['vcodetype']

    def get_key_and_pubkey(self, token, apiver):
        params = {
            'apiver': apiver,
            'token':  token,
            'gid':    self.gid
        }
        r: HTMLResponse = self.session.get(self.URL_PUBLIC_KEY, params=params)
        key = r.html.search('\"key\":\'{}\'')[0]
        pubkey = r.html.search('\"pubkey\":\'{}\',')[0].replace('\\n', '\n').replace('\\', '')
        return key, pubkey

    def check_vcode(self, token, verifycode, codestring):
        params = {
            'token':      token,
            'verifycode': verifycode,
            'codestring': codestring
        }
        res = self.session.get(self.URL_CHECK_VCODE, params=params).json()
        return res['errInfo']['no'] == '0'

    @staticmethod
    def rsa_password(password, pubkey):
        # rsa加密
        rsa_key = RSA.importKey(pubkey)
        cipher = PKCS1_v1_5.new(rsa_key)
        rsa_password = base64.encodebytes(cipher.encrypt(password.encode())).decode().replace('\n', '')
        return rsa_password

    @staticmethod
    def get_dv(driver_path):
        path = pathlib.Path(driver_path)
        if not path.is_file():
            raise ValueError('driver not found')
        driver = webdriver.WebDriver(driver_path)
        driver.get(f'file://{os.getcwd()}/get_dv.html')
        dv = driver.find_element_by_id('dv_Input').get_attribute('value')
        driver.quit()
        return dv

    @staticmethod
    def gen_fp_uid():
        e = ''
        t = 0
        n = 0
        while 32 > n:
            if 12 == n:
                e += ' '
            else:
                r = int(floor(16 * random.random()))
                a = r if 16 != n else 3 & r | 8
                t += a
                e += format(a, 'x')
            n += 1
        return e.replace(' ', format(t % 16, 'x')).lower()

    @staticmethod
    def gen_gid():
        """Generate baidu gid"""
        template_str = 'xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'

        def replace_function(char):
            if char not in 'xy':
                return char
            t = int(floor(16 * random.random()))
            n = t if char == 'x' else 3 & t | 8
            return format(n, 'x')

        return ''.join(map(replace_function, template_str)).upper()

    @staticmethod
    def _get_13_timestamp():
        return int(time.time() * 1000)
