# -*- coding: utf-8 -*-
import scrapy
from ..items import News0Item


class News0Spider(scrapy.Spider):
    name = 'news0'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response):
        news = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/div[7]/div/div/div')
        if len(news.extract()) == 0:
            raise scrapy.exceptions.CloseSpider(reason='Non news list.')
        for selector in news:
            relative_url = selector.xpath('div[@class="item__title"]/a/@href').extract_first()
            header = selector.xpath('div[@class="item__title"]/a/text()').extract_first()
            description = selector.xpath('div[@class="item__descr"]/text()').extract_first()
            tag = selector.xpath('p[@class="item__date links-black"]/a/text()').extract_first()
            url = 'https://{host}{path}'.format(host=self.allowed_domains[0], path=relative_url)
            yield News0Item(header=header, description=description, tag=tag, url=url)
