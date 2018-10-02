import pathlib

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class ICloudSystem:

    def __init__(self, driver_path, timeout=60):

        path = pathlib.Path(driver_path)
        if not path.is_file():
            raise ValueError('driver not found')
        self.driver = webdriver.Chrome(executable_path=path)

        self.timeout = timeout

    def login(self, username, password):
        # op = Options()
        # op.headless = self.settings.getbool('CHROME_DRIVER_HEAD_LESS', True)
        self.driver.get('https://www.icloud.com/')
        WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.presence_of_element_located((By.ID, 'auth-frame'))
        )
        self.driver.switch_to.frame('auth-frame')
        WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located((By.ID, 'account_name_text_field'))
        )
        self.driver.find_element_by_id('account_name_text_field').send_keys(username)
        self.driver.implicitly_wait(1)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located((By.ID, 'password_text_field'))
        )
        self.driver.find_element_by_id('remember-me').click()
        self.driver.find_element_by_id('password_text_field').send_keys(password)
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        # 查找我的iphone
        self.driver.get('https://www.icloud.com/#find')
        WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located((By.NAME, 'find')))
        self.driver.switch_to.frame('find')
        WebDriverWait(self.driver, self.timeout).until(
            expected_conditions.visibility_of_element_located((By.ID, 'map-div')))

    def get_cookies(self):
        cookies = {}
        for driver_cookie in self.driver.get_cookies():
            cookies[driver_cookie['name']] = driver_cookie['value']
        return cookies

    def close(self):
        self.driver.close()
