import argparse
import csv
import random
import time
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import start_driver, login, base_url


def scrape_connections(driver, max_connections):
    driver.get('https://www.linkedin.com/mynetwork/invite-connect/connections/')
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.mn-connection-card')))

    connections = driver.find_element_by_css_selector('h1.t-18').text.split()[0].replace(',', '').strip()
    print('Total connections = {}'.format(connections))

    # infinite scroll
    lastHeight = driver.execute_script("return document.body.scrollHeight")
    while True:
        loaded_connections = len(driver.find_elements_by_css_selector('div.mn-connection-card'))
        print('{}/{} connections loaded'.format(loaded_connections, connections))
        if loaded_connections == connections or loaded_connections >= max_connections:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(5, 10))
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            time.sleep(random.uniform(5, 10))
            newHeight = driver.execute_script("return document.body.scrollHeight")
            if newHeight == lastHeight:
                break
        lastHeight = newHeight

    items = []
    for conn in driver.find_elements_by_css_selector('div.mn-connection-card')[:max_connections]:
        item = {
            'name': conn.find_element_by_css_selector('span.mn-connection-card__name').text,
            'profile': urljoin(base_url,
                               conn.find_element_by_css_selector('a.mn-connection-card__link').get_attribute('href')),
            'occupation': conn.find_element_by_css_selector('span.mn-connection-card__occupation').text,
            'connected': conn.find_element_by_css_selector('time.time-badge').text,
        }
        print(item)
        items.append(item)
    return items


if __name__ == '__main__':
    """ Scrape LinkedIn Connection of an Account """
    parser = argparse.ArgumentParser(description='Scrapes your Linkedin connections')
    parser.add_argument('-n', '--number', help='Number of connections to scrape [Default 100]',
                        nargs='?', default=100, type=int)
    parser.add_argument('-hd', '--headless', help='Run in headless or not [Default False]',
                        nargs='?', default=False, type=bool)
    parser.add_argument('-m', '--maximize', help='Maximize the browser or not [Default True]',
                        nargs='?', default=True, type=bool)
    parser.add_argument('-e', '--email', help='LinkedIn Email', required=True)
    parser.add_argument('-p', '--password', help='LinkedIn Password', required=True)
    args = parser.parse_args()

    driver = start_driver()
    login(driver, args.email, args.password)
    items = scrape_connections(driver, args.number)

    # write to file
    with open('li_connections.csv', 'w') as file:
        writer = csv.DictWriter(file, fieldnames=items[0].keys())
        writer.writeheader()
        writer.writerows(items)

    driver.quit()
