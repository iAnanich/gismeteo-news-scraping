# -*- coding: utf-8 -*-
import scrapy


class News0Spider(scrapy.Spider):
    name = 'news0'
    allowed_domains = ['www.gismeteo.com']
    start_urls = ['http://www.gismeteo.com/news/']

    def parse(self, response):
        pass
