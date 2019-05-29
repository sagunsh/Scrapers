# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import scrapy
from scrapy import Request


class NepalEarthquakeSpider(scrapy.Spider):
    name = 'nepal_earthquake'
    allowed_domains = ['seismonepal.gov.np']
    start_urls = ['http://seismonepal.gov.np/earthquakes']

    def parse(self, response):
        url = 'http://seismonepal.gov.np/earthquakes/{}'
        for year in response.css('select#year option::text').extract():
            yield Request(url.format(year), callback=self.parse_eq)

    def parse_eq(self, response):
        for row in response.css('tbody#searchResultBody>tr'):
            item = {}
            item['Date (B.S.)'] = row.css('td:nth-child(1) ::text').extract()[2]
            item['Date (A.D.)'] = row.css('td:nth-child(1) ::text').extract()[5]
            item['Local Time'] = self.normalize_time(row.css('td:nth-child(2) ::text').extract()[1])
            utctime = self.normalize_time(row.css('td:nth-child(2) ::text').extract()[3])
            item['UTC Time'] = self.to_utc(item['Local Time'], utctime)
            item['Latitude'] = row.css('td:nth-child(3) ::text').extract_first()
            item['Longitude'] = row.css('td:nth-child(4) ::text').extract_first()
            item['Magnitude'] = row.css('td:nth-child(5) ::text').extract_first()
            item['Remarks'] = row.css('td:nth-child(6) ::text').extract_first()
            item['Epicenter'] = row.css('td:nth-child(7) ::text').extract_first()
            yield item

    @staticmethod
    def normalize_time(time):
        return datetime.strptime(time, '%I:%M %p').strftime('%H:%M') if time.endswith('M') else time

    @staticmethod
    def to_utc(localtime, utctime):
        return (datetime.strptime(localtime, '%H:%M') - timedelta(hours=5, minutes=45)).strftime(
            '%H:%M') if utctime == 'N/A' else utctime
