# -*- coding: utf-8 -*-
from datetime import date

import scrapy
from scrapy import Request


class NepseSpider(scrapy.Spider):
    name = 'nepse'
    allowed_domains = ['nepalstock.com']
    fields = ['company_name', 'number_of_transaction', 'max_price', 'min_price',
              'closing_price', 'traded_shares', 'amount', 'previous_closing']

    def start_requests(self):
        today = date.today().strftime("%Y-%m-%d")  # '2018-3-09'
        url = 'http://www.nepalstock.com/main/todays_price/?startDate={}&_limit=1000'.format(today)
        yield Request(url, callback=self.parse, meta={'Date': today})

    def parse(self, response):
        if 'No Data Available!' in response.text:
            print('No data for {}'.format(response.meta['Date']))
            return
        else:
            table = response.css('table.table>tr')
            for tr in table[2:-4]:
                item = dict(zip(self.fields, tr.css('td::text').extract()[1:9]))
                item['difference'] = round(float(item['closing_price']) - float(item['previous_closing']), 2)
                item['date'] = response.meta['Date']
                yield item
