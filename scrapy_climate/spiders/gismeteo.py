# -*- coding: utf-8 -*-

import scrapy

from ..spider import TemplateSpider


class GismeteoSpider(TemplateSpider):
    name = 'gismeteo'

    _start_path = 'news/'
    _start_domain = 'www.gismeteo.ua'
    _protocol = 'https'

    _css_selector_article = '.article'
    _xpath_selector_list_tags = ['div[@class="article__tags links-grey"]/a/text()', ]
    _xpath_selector_list_text = ['div[@class="article__i ugc"]/div/text()',
                                 'div[@class="article__i ugc"]/div/div/text()']
    _xpath_selector_list_header = ['div[@class="article__h"]/h1/text()', ]
    _css_selector_news_list = '.item'
    _xpath_selector_path = 'div[@class="item__title"]/a/@href'

    def parse(self, response: scrapy.http.Response):
        self._scraped_indexes = self._scraped_in_past
        # extract url from main article in img
        spotted_event = response.css('.main-news')[0]
        path = spotted_event.xpath('div/div/a/@href').extract_first()
        yield from self._yield_request(path)
        # extract urls from list
        yield from self._yield_requests_from_response(response)

    def _convert_path_to_index(self, path: str) -> str:
        return path.split('/')[-2].split('-')[0]
