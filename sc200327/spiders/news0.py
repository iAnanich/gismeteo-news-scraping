# -*- coding: utf-8 -*-
import scrapy
import requests as r
from ..items import News0Item
import sys


class News0Spider(scrapy.Spider):
    name = 'news0'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response):
        news = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/div[7]/div/div/div')
        if len(news.extract()) == 0:
            raise scrapy.exceptions.CloseSpider(reason='Non news list.')
        latest_id = fetch_latest_id()
        for selector in news:
            relative_url = selector.xpath('div[@class="item__title"]/a/@href').extract_first()
            id = extract_id_from_relative_url(relative_url)
            if id >= latest_id:  # do not continue items generations if scraped item found
                break
            header = selector.xpath('div[@class="item__title"]/a/text()').extract_first()
            description = selector.xpath('div[@class="item__descr"]/text()').extract_first()
            tag = selector.xpath('p[@class="item__date links-black"]/a/text()').extract_first()
            c_description = clear_description(description)
            url = 'https://{host}{path}'.format(host=self.allowed_domains[0], path=relative_url)
            yield News0Item(header=header, description=c_description, tag=tag, url=url, id=id)


def extract_id_from_relative_url(relative_url: str) -> int:
    return int(relative_url.split('/')[3].split('-')[0])


def clear_description(description: str) -> str:
    return description.replace('\xa0', ' ')


def fetch_latest_id() -> int:
    content = str(r.get('https://app.scrapinghub.com/api/items.csv?project={project}&spider={spider}&include_headers=1&fields={fields}&apikey={key}'.format(
        project='200327',
        spider='news0',
        fields='id',
        key=get_api_key(),
    )).content)  # looks like 'b\'"id"\\n\''
    if content == """b'{"status": "error", "message": "Authentication failed"}'""":
        raise RuntimeError('Wrong API_KEY provided.')
    ids = content.split('"\\n"')[1:]
    if len(ids) == 0:
        return 0
    else:
        return int(ids[0])


def get_api_key() -> str:
    for arg in sys.argv:
        if 'API_KEY=' in arg:
            return arg[arg.find('=')+1:]
    else:
        raise RuntimeError('No "API_KEY" argument found.')
