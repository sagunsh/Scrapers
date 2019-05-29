import os

from selenium import webdriver


def start_driver(headless=False, maximized=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    if maximized:
        options.add_argument('--start-maximized')
    driver = webdriver.Chrome(executable_path=os.path.abspath('../chromedriver_72'), chrome_options=options)
    return driver