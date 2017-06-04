# -*- coding: utf-8 -*-
import scrapy

from .tools import (fetch_latest_job,
                    clear)
from ..args import start_arguments
from ..items import NewsListItem, LatestNewsIndexItem


class NewsListSpider(scrapy.Spider):
    name = 'news-list'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response):
        latest_index = self._fetch_latest_scraped_id()
        indexes = [latest_index]
        # locate `div` with news
        news = response.xpath('/html/body/div[2]/div/div[1]/div[2]/div[1]/div/div/div[7]/div/div/div')
        for selector in news:
            path = selector.xpath('div[@class="item__title"]/a/@href').extract_first()
            index = int(path.split('/')[3].split('-')[0])

            if index <= latest_index:
                # do not continue items generation if scraped item found
                break
            else:
                header = selector.xpath('div[@class="item__title"]/a/text()').extract_first()
                tag = selector.xpath('p[@class="item__date links-black"]/a/text()').extract_first()
                description = clear(selector.xpath('div[@class="item__descr"]/text()').extract_first())
                url = 'https://{host}{path}'.format(host=self.allowed_domains[0], path=path)
                indexes.append(index)
                yield NewsListItem(header=header, url=url, description=description, tag=tag)
        yield LatestNewsIndexItem(index=max(indexes))

    def _fetch_latest_scraped_id(self) -> int:
        table = fetch_latest_job(
            spider=self.name,
            fields='index',
            project=start_arguments.project_id,
            key=start_arguments.api_key
        )
        if len(table) == 1:
            RuntimeWarning('No items from previous jobs')
            return 0
        elif table[-1][0] == '':
            RuntimeWarning('No "index" field from previous jobs:' + str(table))
            return 0
        else:
            return int(table[-1][0])
