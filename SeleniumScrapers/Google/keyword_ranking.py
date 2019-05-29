import argparse
import csv
import os
from urllib.parse import urlparse, urljoin

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from utils import start_driver

base_url = 'https://www.google.com/'


def scrape_rank(driver, query):
    filename = query + '.csv'
    if os.path.isfile(filename):
        os.remove(filename)

    rank = 0
    results = set()

    with open(filename, 'a') as file:
        writer = None

        url = 'https://www.google.com/search?q={}'
        driver.get(url.format(query))

        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.r > a:nth-child(1)')))
            links = driver.find_elements_by_css_selector('div.r > a:nth-child(1)')
        except TimeoutException:
            return

        for i, link in enumerate(links):
            page = link.get_attribute('href')
            if page in results:
                continue

            results.add(page)
            item = {}
            rank += 1
            item['rank'] = rank
            item['query'] = query
            item['page'] = page
            item['index_page'] = urlparse(page).netloc

            if not writer:
                writer = csv.DictWriter(file, fieldnames=item.keys())
                writer.writeheader()
            print(item)
            writer.writerow(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrapes google by querying a domain name and checks '
                                                 'if it is present in the first page')
    parser.add_argument('-hd', '--headless', help='Run in headless or not [Default False]', nargs='?', default=False,
                        type=bool)
    parser.add_argument('-mx', '--maximize', help='Maximize the browser or not [Default True]', nargs='?', default=True,
                        type=bool)
    parser.add_argument('-q', '--query', help='Query to search on google', required=True)

    args = parser.parse_args()
    headless = args.headless
    maximized = args.maximize
    query = args.query

    driver = start_driver(headless=headless, maximized=maximized)
    scrape_rank(driver, query)
    driver.quit()
