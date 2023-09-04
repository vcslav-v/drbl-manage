import json
import os
from time import sleep

from loguru import logger
from selenium import webdriver

from drbl_manage import do_app


class Browser:
    def __init__(self, antcpt=True) -> None:
        self.app_instance = do_app.DOApp()

        browser_options = webdriver.chrome.options.Options()
        chrome_prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
        browser_options.experimental_options["prefs"] = chrome_prefs
        browser_options.add_argument('--kiosk')
        browser_options.set_capability('browserName', 'chrome')
        browser_options.add_extension('anticaptcha.crx')

        driver = webdriver.Remote(
            command_executor=self.app_instance.url,
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
        self.app_instance.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.app_instance.close()
        if exc_type:
            logger.error(exc_tb)
