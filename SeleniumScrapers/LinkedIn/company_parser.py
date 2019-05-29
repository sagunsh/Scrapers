import argparse
import csv
import re
import sys
from urllib.parse import urljoin

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import start_driver, login


def validate_url(url):
    ''' validate a linkedin company url and return about page '''
    if not url.endswith('/'):
        url = url + '/'
    if re.match('https?://www.linkedin.com/company/[\w-]+/?(?:about/?)?$', url):  # match company url
        if re.match('https?://www.linkedin.com/company/[\w-]+/about/?', url):  # match about url
            return url
        else:
            return urljoin(url, 'about/')
    else:
        return False


def parse_company(driver, url):
    driver.get(url)

    about_url = validate_url(url)
    driver.get(about_url)
    item = {}
    keys = ['Website', 'Industry', 'Company size', 'Headquarters', 'Type', 'Founded', 'Specialties']
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.org-top-card-summary__title')))
    except TimeoutException:
        for key in keys:
            new_key = 'CompanyWebsite' if key == 'Website' else key.title().replace(' ', '')
            item[new_key] = ''
        return item

    item['Name'] = driver.find_element_by_css_selector('h1.org-top-card-summary__title').get_attribute('title')

    try:
        item['Tagline'] = driver.find_element_by_css_selector('p.mt2').text
    except NoSuchElementException:
        item['Tagline'] = ''

    try:
        num_employees = re.findall('\d+', driver.find_element_by_css_selector(
            'a[data-control-name="topcard_see_all_employees"]>span').text)[0]
        item['Number of Employees'] = num_employees[0] if num_employees else '0'
    except NoSuchElementException:
        item['Number of Employees'] = ''

    for key in keys:
        new_key = 'CompanyWebsite' if key == 'Website' else key.title().replace(' ', '')
        try:
            item[new_key] = driver.find_element_by_xpath(f'//dt[text()="{key}"]//following-sibling::dd[1]').text
        except NoSuchElementException:
            item[new_key] = ''

    try:
        item['Overview'] = driver.find_element_by_css_selector('p.mb5').text
    except NoSuchElementException:
        item['Overview'] = ''
    print(item)
    return item


def parse_company_from_file(driver, file):
    companies = open(file).read().split('\n')
    with open('company.csv', 'a') as file:
        writer = None
        for url in companies:
            item = parse_company(driver, url)
            if not writer:
                writer = csv.DictWriter(file, fieldnames=item.keys())
                writer.writeheader()
            writer.writerow(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses a company page')
    parser.add_argument('-hd', '--headless', help='Run in headless or not [Default False]',
                        nargs='?', default=False, type=bool)
    parser.add_argument('-u', '--url', help='LinkedIn URL of company')
    parser.add_argument('-f', '--file', help='File containing LinkedIn urls on each line')
    parser.add_argument('-e', '--email', help='LinkedIn Email', required=True)
    parser.add_argument('-p', '--password', help='LinkedIn Password', required=True)
    args = parser.parse_args()

    if not (args.url or args.file):
        print('Either url or file needs to be supplied')
        sys.exit(1)

    driver = start_driver()
    login(driver, args.email, args.password)
    if args.file:
        items = parse_company_from_file(driver, args.file)
    else:
        item = parse_company(driver, args.url)
        # write to file
        with open('company.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=item.keys())
            writer.writeheader()
            writer.writerows(item)

    driver.quit()
