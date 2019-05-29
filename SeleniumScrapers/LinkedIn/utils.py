import os
import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

BASE_URL = 'https://www.linkedin.com/'


def start_driver(headless=False, maximized=True):
    options = webdriver.ChromeOptions()
    if maximized:
        options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=os.path.abspath('../chromedriver_72'), chrome_options=options)
    return driver


def login(driver, email, password):
    xpath_email = '//*[@id="login-email"]'
    xpath_password = '//*[@id="login-password"]'
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_email)))
        driver.find_element_by_xpath(xpath_email).send_keys(email)
        time.sleep(2)
        driver.find_element_by_xpath(xpath_password).send_keys(password)
        WebDriverWait(driver, random.randint(5, 10))
        driver.find_element_by_xpath('//*[@id="login-submit"]').click()
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="notifications-tab-icon"]')))
        return True
    except:
        if 'Welcome to your professional community' in driver.page_source:
            try:
                driver.find_element_by_xpath('//*[text()="Sign in"]').click()
            except NoSuchElementException:
                return False

            xpath_email = '//*[@id="username"]'
            xpath_password = '//*[@id="password"]'
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_email)))
            driver.find_element_by_xpath(xpath_email).send_keys(email)
            time.sleep(2)
            driver.find_element_by_xpath(xpath_password).send_keys(password)
            WebDriverWait(driver, random.randint(5, 10))
            driver.find_element_by_xpath('//*[text()="Sign in"]').click()
            WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="notifications-tab-icon"]')))
            return True
        else:
            return False


if __name__ == '__main__':
    driver = start_driver()
    login(driver, 'email', 'passwd')
    driver.quit()
