# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request


class EuStartupsSpider(scrapy.Spider):
    name = 'eu_startups'
    allowed_domains = ['eu-startups.com']
    start_urls = ['https://www.eu-startups.com/directory/?wpbdp_view=all_listings']

    def parse(self, response):
        for listing in response.css('a.view-listing ::attr(href)').extract():
            yield Request(listing, callback=self.parse_detail)

        next_page = response.css('span.next>a::attr(href)').extract_first()
        if next_page:
            yield Request(next_page)

    def parse_detail(self, response):
        item = {}
        item['name'] = response.css('div.wpbdp-field-association-title>span.value>a::text').extract_first()
        item['website'] = response.css('div.wpbdp-field-website>span.value::text').extract_first().strip()
        item['source'] = response.url
        item['founded'] = response.css('div.wpbdp-field-founded>span.value::text').extract_first(),
        item['location'] = response.css('div.wpbdp-field-based_in>span.value::text').extract_first()
        item['description'] = response.css('div.wpbdp-field-business_description>span.value::text').extract_first()
        item['long_description'] = '\n'.join(
            response.css('div.wpbdp-field-long_business_description>span.value p::text').extract()).strip()
        yield item
