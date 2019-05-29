# -*- coding: utf-8 -*-
import re
from datetime import datetime
from dateutil.parser import parse

import scrapy
from scrapy import Request


class AviationsafetySpider(scrapy.Spider):
    name = 'aviation_safety'
    allowed_domains = ['aviation-safety.net']

    def start_requests(self):
        url = 'https://aviation-safety.net/database/dblist.php?Year={}'
        for year in range(1919, datetime.today().year):
            yield Request(url.format(year))

    def parse(self, response):
        for link in response.css('table>tr>td:nth-child(1) a::attr(href)').extract():
            yield Request(response.urljoin(link), callback=self.parse_detail)

        for page in set(response.css('div.pagenumbers a::attr(href)').extract()):
            yield Request(response.urljoin(page))

    def parse_detail(self, response):
        item = {}

        table = response.xpath('//div[@class="innertube"]/table')
        data_xpath = 'tr/td[contains(., "{}:")]/following-sibling::td//text()'

        data_keys = ['Status', 'Time', 'Type', 'Operator', 'Registration', 'C/n / msn', 'Total airframe hrs',
                     'Cycles', 'Aircraft damage', 'Aircraft fate', 'Phase', 'Nature', 'Flightnumber']
        for key in data_keys:
            item[key] = table.xpath(data_xpath.format(key)).extract_first()

        try:
            dt = parse(table.xpath(data_xpath.format('Date')).extract_first())
            item['Weekday'] = dt.strftime('%A')
            item['Date'] = dt.strftime('%Y-%m-%d')
        except:
            item['Weekday'] = 'N/A'
            item['Date'] = table.xpath(data_xpath.format('Date')).extract_first()

        item['First Flight'] = table.xpath(data_xpath.format('First flight')).extract_first('').split('(')[0]
        item['Engine'] = ''.join(table.xpath(data_xpath.format('Engines')).extract())

        crew = table.xpath(data_xpath.format('Crew')).extract_first()
        passengers = table.xpath(data_xpath.format('Passengers')).extract_first()
        item['Crew Fatalities'], item['Crew Occupants'] = self.parse_fatalities(crew)
        item['Passengers Fatalities'], item['Passengers Occupants'] = self.parse_fatalities(passengers)

        item['Location'] = ''.join(table.xpath(data_xpath.format('Location')).extract())
        item['Destination airport'] = ''.join(table.xpath(data_xpath.format('Destination airport')).extract())
        item['Departure airport'] = ''.join(table.xpath(data_xpath.format('Departure airport')).extract())

        item['Narrative'] = '\n'.join(response.xpath('//span[text()="Narrative:"]/following-sibling::span[1]/text()').extract())
        item['Link'] = response.url

        yield item

    @staticmethod
    def parse_fatalities(value):
        if value:
            data = re.findall('Fatalities:\s?(\d+)?\s?/\s?Occupants:\s?(\d+)?', value)
            if data:
                return data[0]

        return 'N/A', 'N/A'
