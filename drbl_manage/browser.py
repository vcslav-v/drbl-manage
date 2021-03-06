import json
import os
from random import choice
from time import sleep
from urllib.parse import urlparse

import requests
from loguru import logger
from selenium import webdriver

from drbl_manage import db_tools


class Browser:
    def __init__(self, selenium_ip, antcpt=True, proxy=True) -> None:
        logger.debug(selenium_ip)
        browser_options = webdriver.chrome.options.Options()
        chrome_prefs = {}
        # chrome_prefs["profile.default_content_settings"] = {"images": 2}
        # chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        browser_options.experimental_options["prefs"] = chrome_prefs
        browser_options.add_argument('--kiosk')
        if proxy:
            proxy_server = self._get_proxy()
            browser_options.add_argument(f'proxy-server={proxy_server}')
        browser_options.set_capability('browserName', 'chrome')
        browser_options.set_capability('enableVNC', True)
        browser_options.set_capability('enableVideo', False)
        browser_options.add_extension('anticaptcha.crx')
        driver = webdriver.Remote(
                command_executor=f'http://{selenium_ip}:4444/wd/hub',
                options=browser_options,
            )
        if antcpt:
            driver.get('https://antcpt.com/blank.html')
            message = {
                    'receiver': 'antiCaptchaPlugin',
                    'type': 'setOptions',
                    'options': {'antiCaptchaApiKey': os.environ.get('AC_KEY')},
                }
            sleep(10)
            driver.execute_script(
                'return window.postMessage({});'.format(json.dumps(message)),
            )
            sleep(5)
        self.driver = driver

    def close(self):
        self.driver.close()

    def _get_proxy(self) -> str:
        response = requests.get(os.environ.get('PROXY_API_KEY'))
        proxies = json.loads(response.text)
        proxy = choice(proxies)
        return '{hostname}:{port}'.format(**proxy)

    def set_cookies(self, site_url: str, username: str):
        self.driver.get(site_url)
        domain = urlparse(site_url).netloc
        cookies = db_tools.get_cookies(domain, username)
        if cookies:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.get(site_url)

    def save_cookies(self, site_url: str, username: str):
        domain = urlparse(site_url).netloc
        cookies = self.driver.get_cookies()
        db_tools.set_cookies(domain, username, cookies)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            logger.error(exc_tb)
