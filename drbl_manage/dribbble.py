import os
from random import choice, random
from time import sleep

from faker import Faker
from loguru import logger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from drbl_manage import db_tools, mem
from drbl_manage.browser import Browser
from drbl_manage.models import Account


def do_tasks(selenium_ip, tasks):
    with Browser(selenium_ip) as brwsr:
        account: Account = db_tools.get_acc(mem.pop_acc_id())
        if not account:
            return
        _login(brwsr, account)
        for task in tasks:
            task_key, task_link = task
            try:
                _like(brwsr.driver, task_link)
            except Exception as e:
                logger.error(e)
            else:
                mem.task_done(task_key)
        brwsr.save_cookies('https://dribbble.com', account.username)


def _like(driver, link):
    driver.get(link)
    like_elem = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(By.ID, 'shots-like-button')
    )
    like_elem.click()


@logger.catch
def make_new_user(selenium_ip):
    person = _get_rand_person()
    with Browser(selenium_ip) as brwsr:
        brwsr.driver.get('https://dribbble.com/signup/new')
        _do_sign_up(brwsr.driver, person)
        _do_boarding(brwsr.driver)
        db_tools.add_account(person)
        brwsr.save_cookies('https://dribbble.com', person['username'])


def _login(brwsr: Browser, account: Account):
    brwsr.set_cookies('https://dribbble.com', account.name)
    try:
        WebDriverWait(brwsr.driver, timeout=10).until(
            lambda d: d.find_element(By.XPATH, '//a[@data-site-nav-element="User"]')
        )
    except TimeoutException:
        brwsr.driver.get('https://dribbble.com/session/new')
        username_input_elem = brwsr.driver.find_element(By.ID, 'login')
        username_input_elem.send_keys(account.email)
        pass_input_elem = brwsr.driver.find_element(By.ID, 'password')
        pass_input_elem.send_keys(account.password)
        btn_submit = brwsr.driver.find_element(By.XPATH, '//input[@type="submit"]')
        btn_submit.click()

    WebDriverWait(brwsr.driver, timeout=120).until(
        lambda d: d.find_element(By.XPATH, '//a[@data-site-nav-element="User"]')
    )


def _get_new_email():
    is_new_email = False
    while not is_new_email:
        pivot_point = random()
        email_user = os.environ.get('EMAIL_USER')
        result = email_user[0]
        for char in email_user[1:]:
            if pivot_point > random():
                result += f'.{char}'
            else:
                result += char
        new_email = result + '@gmail.com'
        is_new_email = db_tools.is_new_email(new_email)
    return new_email


def _get_rand_person():
    fake = Faker()
    result = {}
    first_name = fake.first_name()
    last_name = fake.last_name()
    result['name'] = ' '.join([first_name, last_name])
    result['username'] = '_'.join([first_name, last_name, fake.user_name()])
    result['password'] = fake.password(10)

    result['email'] = _get_new_email()
    return result


def _do_sign_up(driver, person):
    name_input_elem = WebDriverWait(driver, timeout=20).until(
        lambda d: d.find_element(By.ID, 'user_name')
    )
    name_input_elem.send_keys(person['name'])
    username_input_elem = driver.find_element(By.ID, 'user_login')
    username_input_elem.send_keys(person['username'])
    mail_input_elem = driver.find_element(By.ID, 'user_email')
    mail_input_elem.send_keys(person['email'])
    pass_input_elem = driver.find_element(By.ID, 'user_password')
    pass_input_elem.send_keys(person['password'])
    flag_elem = driver.find_element(By.XPATH, '//label[@for="user_agree_to_terms"]')
    flag_elem.click()
    btn_submit = driver.find_element(By.XPATH, '//input[@type="submit"]')
    btn_submit.click()

    WebDriverWait(driver, timeout=120).until(
        lambda d: d.find_element(By.XPATH, '//a[@class="avatar-select-trigger"]')
    )


def _do_boarding(driver):
    avatar_select_elem = WebDriverWait(driver, timeout=10).until(
        lambda d: d.find_element(By.XPATH, '//a[@class="avatar-select-trigger"]')
    )
    avatar_select_elem.click()
    userpic_elems = driver.find_elements(By.XPATH, '//li[@class="avatar-select-item"]')
    userpic_elem = choice(userpic_elems)
    userpic_elem.click()

    local_input_elem = driver.find_element(By.ID, 'location')
    local_input_elem.send_keys(choice(['USA', 'Canada', 'England', 'Barselona', 'NY', 'Spain']))

    sleep(3)
    btn_submit = driver.find_element(By.XPATH, '//button[@class="form-sub"]')
    btn_submit.click()

    plan_elems = driver.find_elements(By.XPATH, '//div[@class="image-select-box-choice"]')
    plan_elem = plan_elems[-1]
    plan_elem.click()

    btn_submit = driver.find_element(By.XPATH, '//button[@class="form-sub"]')
    btn_submit.click()
