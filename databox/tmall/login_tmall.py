import json
import pathlib
import sys
import time

import qrcode
import requests
from scrapy.commands import ScrapyCommand
from scrapy_redis import connection
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from databox import utils
from databox.tmall.enums import TmallQrCodeScanStatus


class Command(ScrapyCommand):
    def __init__(self):
        super().__init__()
        self.lg_token = ''
        self.cookies = None
        self.driver_path = ''

    def run(self, args, opts):
        self.driver_path = self.settings.get('CHROME_DRIVER_PATH')
        path = pathlib.Path(self.driver_path)
        if not path.is_file():
            print('driver not found')
            sys.exit(-1)
        status = None
        while status != TmallQrCodeScanStatus.CONFIRM:
            res = requests.get('https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do').json()
            # qrcode_img_url是存储二维码图片的地址
            qrcode_img_url, self.lg_token, ad_token = 'https:' + res['url'], res['lgToken'], res['adToken']
            qrcode_url = common_utils.decode_qrcode_img_url(qrcode_img_url)
            status = TmallQrCodeScanStatus.WAITING
            # 控制台打印二维码
            self._print_qrcode(qrcode_url)
            # 判断用户是否扫码
            while status != TmallQrCodeScanStatus.EXPIRED and status != TmallQrCodeScanStatus.SUCCESS:
                status = self._get_qrcode_status_by_lg_token()
                time.sleep(3)
            # 判断用户是否点击登录
            while status != TmallQrCodeScanStatus.EXPIRED and status != TmallQrCodeScanStatus.CONFIRM:
                status = self._get_qrcode_status_by_lg_token()
                time.sleep(3)
            print('success')
            print(self.cookies)
            break

    def _get_qrcode_status_by_lg_token(self) -> TmallQrCodeScanStatus:
        res = requests.get(
            'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=' + self.lg_token).json()
        status = TmallQrCodeScanStatus(res['code'])
        if status == TmallQrCodeScanStatus.CONFIRM:
            # selenium打开url进行二次验证
            driver = webdriver.WebDriver(self.driver_path)
            op = Options()
            op.headless = self.settings.getbool('CHROME_DRIVER_HEAD_LESS', True)
            driver.get(res['url'])
            # 预留30秒二次验证时间
            sec = 30
            try:
                # 寻找当前用户div
                WebDriverWait(driver, sec).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'div.site-nav-user'))
                )
            except TimeoutException as _:
                print('failed')
                driver.quit()
                sys.exit(-1)
            driver_cookies = driver.get_cookies()
            driver.quit()

            self.cookies = {}
            for driver_cookie in driver_cookies:
                self.cookies[driver_cookie['name']] = driver_cookie['value']
            conn = connection.from_settings(self.settings)
            conn.set('databox:cookies:tmall', json.dumps(self.cookies))
        return TmallQrCodeScanStatus(res['code'])

    @staticmethod
    def _print_qrcode(qrcode_url):
        qr = qrcode.QRCode()
        qr.border = 1
        qr.add_data(qrcode_url)
        qr.make()
        qr.print_ascii(invert=True)
