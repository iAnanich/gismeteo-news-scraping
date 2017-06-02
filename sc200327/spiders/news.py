# -*- coding: utf-8 -*-
import scrapy
from ..items import NewsListItem
from .tools import (parse_news,
                    fetch_latest_id,)


class NewsListAllSpider(scrapy.Spider):
    name = 'news-list-all'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response):
        news = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/div[7]/div/div/div')
        for selector in news:
            yield NewsListItem(**parse_news(selector, self.allowed_domains[0]))


class NewsListSpider(scrapy.Spider):
    name = 'news-list'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response):
        news = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/div[7]/div/div/div')
        latest_id = fetch_latest_id()
        for selector in news:
            kwargs = parse_news(selector, self.allowed_domains[0])
            if kwargs['id'] <= latest_id:  # do not continue items generations if scraped item found
                break
            yield NewsListItem(**kwargs)
