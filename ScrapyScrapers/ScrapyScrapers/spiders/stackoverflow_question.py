# -*- coding: utf-8 -*-
import scrapy


class StackoverflowQuestionSpider(scrapy.Spider):
    name = 'stackoverflow_question'
    allowed_domains = ['stackoverflow.com']
    start_urls = ['https://stackoverflow.com/questions/tagged/web-scraping?sort=newest&pagesize=50']

    def parse(self, response):
        for question in response.css('div.question-summary'):
            item = {}
            item['Title'] = question.css('div.summary>h3>a::text').get()
            item['Votes'] = question.css('span.vote-count-post>strong::text').get()
            item['Answers'] = question.css('div.status>strong::text').get()
            item['Views'] = question.css('div.views::attr(title)').get('').split()[0]
            item['AskedTime'] = question.css('div.user-action-time>span::attr(title)').get()
            item['AskedBy'] = question.css('div.user-details>a::text').get()
            item['Reputation'] = question.css('span.reputation-score::text').get()
            item['Link'] = response.urljoin(question.css('div.summary>h3>a::attr(href)').get())
            item['Excerpt'] = question.css('div.excerpt::text').get('').replace('...', '').strip()
            item['Tags'] = ','.join(question.css('div.tags>a::text').extract())
            yield item