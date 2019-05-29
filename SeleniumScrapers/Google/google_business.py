import argparse
import re
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils import start_driver

base_url = 'https://www.google.com/'


def parse_data(driver):
    item = {}
    item['business_name'] = driver.find_element_by_css_selector('div.kno-ecr-pt span').text

    try:
        item['overall_rating'] = driver.find_element_by_css_selector('span.rtng').text
    except NoSuchElementException:
        item['overall_rating'] = ''

    try:
        num_reviews = re.findall('([\d,]+)\s?Google reviews', driver.page_source, re.IGNORECASE)
        item['num_of_reviews'] = int(num_reviews[0].replace(',', '')) if num_reviews else 0
    except:
        item['num_of_reviews'] = ''

    try:
        item['website'] = driver.find_element_by_xpath(
            '//a[@class="ab_button" and text()="Website"]').get_attribute('href')
    except NoSuchElementException:
        item['website'] = ''

    try:
        item['direction'] = urljoin(base_url, driver.find_element_by_xpath(
            '//a[@class="ab_button" and text()="Directions"]').get_attribute('data-url'))
    except NoSuchElementException:
        item['direction'] = ''

    try:
        item['address'] = driver.find_element_by_xpath(
            '//span[@class="w8qArf" and contains(., "Address")]/following-sibling::span[contains(@class, "LrzXr")]').text
    except NoSuchElementException:
        item['address'] = ''

    try:
        item['phone'] = driver.find_element_by_xpath(
            '//span[@class="w8qArf" and contains(., "Phone")]/following-sibling::span[contains(@class, "LrzXr")]').text
    except:
        item['phone'] = ''
    return item


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes Hotel Reviews from Google')
    parser.add_argument('-hd', '--headless', help='Run in headless or not [Default False]', nargs='?', default=False,
                        type=bool)
    parser.add_argument('-mx', '--maximize', help='Maximize the browser or not [Default True]', nargs='?', default=True,
                        type=bool)
    parser.add_argument('-q', '--query', help='Query to search on google', required=True)
    args = parser.parse_args()
    headless = args.headless
    maximized = args.maximize
    query = args.query

    # open google.com
    driver = start_driver(headless=headless, maximized=maximized)
    driver.get(base_url)

    # send query and enter
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.NAME, 'q')))
    driver.find_element_by_name('q').send_keys(query + Keys.ENTER)

    # change language to english
    try:
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.LINK_TEXT, 'Change to English')))
        driver.find_element_by_link_text('Change to English').click()
    except:  # if already in english
        pass
    # scrape hotel item and insert into db
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.kno-ecr-pt')))
    item = parse_data(driver)
    item['query'] = query
    print(item)
    driver.quit()
