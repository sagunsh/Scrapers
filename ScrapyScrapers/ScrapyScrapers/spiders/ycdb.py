# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class YcdbSpider(scrapy.Spider):
    name = 'ycdb'
    allowed_domains = ['ycdb.co']
    start_urls = ['https://www.ycdb.co/']

    def parse(self, response):
        for batch in set(response.css('a.mt-1 ::attr(href)').extract()):
            yield Request(response.urljoin(batch), callback=self.parse_batch)

    def parse_batch(self, response):
        for company in response.css('table>tbody>tr>td.ellipsis>a::attr(href)').extract():
            yield Request(response.urljoin(company), callback=self.parse_company)

    def parse_company(self, response):
        item = {}
        item['title'] = response.css('h1 ::text').extract_first()

        for r in response.css('p.lighter'):
            key, val = map(str.strip, ''.join(r.css(' ::text').extract()).strip().split(':'))
            item[key.lower()] = val

        for key in ['batch', 'category', 'founded', 'location']:
            if key not in item:
                item[key] = ''

        item['link'] = response.url
        item['logo'] = response.css('div.container.pt-4>img::attr(src)').extract_first()
        item['description'] = response.css('div.pt-4>p::text').extract_first()
        item['website'] = response.css('a.btn-block ::attr(href)').extract_first()
        item['crunchbase'] = response.xpath(
            '//p[@class="font-large text-muted"]/a[contains(@href, "crunchbase.com")]/@href').extract_first()
        item['twitter'] = response.xpath(
            '//p[@class="font-large text-muted"]/a[contains(@href, "twitter.com")]/@href').extract_first()
        item['linkedin'] = response.xpath(
            '//p[@class="font-large text-muted"]/a[contains(@href, "linkedin.com")]/@href').extract_first()
        item['facebook'] = response.xpath(
            '//p[@class="font-large text-muted"]/a[contains(@href, "facebook.com")]/@href').extract_first()
        item['instagram'] = response.xpath(
            '//p[@class="font-large text-muted"]/a[contains(@href, "instagram.com")]/@href').extract_first()
        yield item
