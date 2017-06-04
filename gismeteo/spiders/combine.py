# -*- coding: utf-8 -*-
import logging

import scrapy

from .tools import (fetch_latest_job,
                    clear_text,
                    convert_list_to_string)
from ..args import start_arguments
from ..items import LatestNewsIndexItem, EventItem


class CombineSpider(scrapy.Spider):
    name = 'combine'
    allowed_domains = ['www.gismeteo.ua']
    start_urls = ['https://www.gismeteo.ua/news/']

    def parse(self, response: scrapy.http.Response):
        latest_index = self._fetch_latest_scraped_id()
        indexes = [latest_index]
        # locate `div`s with news
        news = response.css('.item')
        for selector in news:
            path = selector.xpath('div[@class="item__title"]/a/@href').extract_first()
            index = int(path.split('/')[3].split('-')[0])
            if index <= latest_index:  # do not continue items generation if scraped item found
                break
            else:
                url = 'https://{host}{path}'.format(host=self.allowed_domains[0], path=path)
                indexes.append(index)
                yield scrapy.http.Request(url=url, callback=self.parse_article)
        yield LatestNewsIndexItem(index=max(indexes))

    def parse_article(self, response: scrapy.http.Response):
        # locate article
        article = response.css('.article')
        # generate `tags` string
        tags_list = article.xpath('div[@class="article__tags links-grey"]/a/text()').extract()
        tags = convert_list_to_string(tags_list, ',')
        # generate `text` string
        text_blocks = article.xpath('div[@class="article__i ugc"]/div/text()').extract()
        text = convert_list_to_string(text_blocks, '', handler=clear_text)
        # produce item
        yield EventItem(
            url=response.url,
            header=article.xpath('div[@class="article__h"]/h1/text()').extract_first(),
            tags=tags,
            text=text,
        )

    def _fetch_latest_scraped_id(self) -> int:
        table = fetch_latest_job(
            spider=self.name,
            fields='index',
            project=start_arguments.project_id,
            key=start_arguments.api_key
        )
        if len(table) == 1:
            logging.warning('No items from previous jobs')
            return 0
        elif table[-1][0] == '':
            logging.warning('No "index" field from previous jobs:' + str(table))
            return 0
        else:
            return int(table[-1][0])
