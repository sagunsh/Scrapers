# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/chart/top']

    def parse(self, response):
        for movie in response.css('tbody.lister-list>tr'):
            item = {}
            item['Rank'] = movie.css('td.titleColumn::text').get().strip().replace('.', '')
            item['Title'] = movie.css('td.titleColumn>a::text').get()
            item['Year'] = movie.css('span.secondaryInfo::text').get().strip('(').strip(')')
            item['Link'] = response.urljoin(movie.css('td.titleColumn>a::attr(href)').get())
            yield Request(item['Link'], callback=self.parse_movie, meta={'item': item})

    def parse_movie(self, response):
        item = response.meta.get('item', {})

        script_json = json.loads(response.css('script[type="application/ld+json"]::text').get())
        item['Genre'] = script_json.get('genre')
        item['Rating'] = script_json.get('aggregateRating', {}).get('ratingValue')
        item['RatingCount'] = script_json.get('aggregateRating', {}).get('ratingCount')
        item['Duration'] = script_json.get('duration', '').replace('PT', '')

        director = script_json.get('director')
        if isinstance(director, dict):
            item['Director'] = script_json.get('director', {}).get('name')
        elif isinstance(director, list):
            directors = []
            for row in director:
                directors.append(row.get('name'))
            item['Director'] = ','.join(directors)
        item['Poster'] = script_json.get('image')
        item['Description'] = script_json.get('description')
        item['Keywords'] = script_json.get('keywords')
        yield item
