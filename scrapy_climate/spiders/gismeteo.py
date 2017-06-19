# -*- coding: utf-8 -*-

import scrapy

from ..items import EventItem
from ..tools import convert_list_to_string, fetch_scraped_indexes


class GismeteoSpider(scrapy.Spider):
    name = 'gismeteo'

    _start_path = 'news/'
    _start_domain = 'www.gismeteo.ua'
    _protocol = 'https'

    allowed_domains = [_start_domain, ]
    start_urls = ['{}://{}/{}'.format(_protocol, _start_domain, _start_path), ]

    _scraped_indexes = fetch_scraped_indexes(name)

    _css_selector_article = '.article'
    _xpath_selector_tags = 'div[@class="article__tags links-grey"]/a/text()'
    _xpath_selector_text = 'div[@class="article__i ugc"]/div/text()'
    _xpath_selector_header = 'div[@class="article__h"]/h1/text()'
    _css_selector_news_list = '.item'
    _xpath_selector_path = 'div[@class="item__title"]/a/@href'

    ### "parse" methods
    def parse(self, response: scrapy.http.Response):
        # extract url from main article in img
        spotted_event = response.css('.main-news')[0]
        path = spotted_event.xpath('div/div/a/@href').extract_first()
        yield from self._yield_request(path)
        # extract urls from list
        yield from self._yield_requests_from_response(response)

    def parse_article(self, response: scrapy.http.Response):
        # locate article
        article = self._find_article_in_responce(response)
        # produce item
        yield from self._yield_article_item(
            response,
            text=self._extract_text(article),
            header=self._extract_header(article),
            tags=self._extract_tags(article),
        )

    ### helpers
    def _clear_text_field(self, text: str) -> str:
        string = str(text).replace('\xa0', ' ')
        return string.replace('\n', '')

    def _convert_path_to_index(self, path: str) -> str:
        """ function that extracts unique part from given url."""
        # left only event index
        return path.split('/')[-2].split('-')[0]

    ### "yield" methods that returns generators
    def _yield_request(self, path: str):
        url = 'https://{host}{path}'.format(host=self.allowed_domains[0], path=path)
        index = self._convert_path_to_index(path)
        if index not in self._scraped_indexes:
            yield scrapy.http.Request(url=url,
                                      callback=self.parse_article,
                                      meta={'index': index})

    def _yield_article_item(self, response: scrapy.http.Response, **kwargs):
        yield EventItem(
            url=response.url,
            index=response.meta['index'],
            **kwargs
        )

    def _yield_requests_from_response(self, response: scrapy.http.Response):
        """ Yields requests with `parse_article` callback.
        Takes response, finds, extracts news list, extracts from every path and generates requests."""
        for selector in response.css(self._css_selector_news_list):
            path = selector.xpath(self._xpath_selector_path).extract_first()
            yield from self._yield_request(path)

    ### "find" methods that returns Selectors
    def _find_article_in_responce(self, response: scrapy.http.Response) -> scrapy.selector.SelectorList:
        return response.css(self._css_selector_article)

    def _find_news_list_in_responce(self, response: scrapy.http.Response) -> scrapy.selector.SelectorList:
        return response.css(self._css_selector_news_list)

    def _find_tags(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return article.xpath(self._xpath_selector_tags)

    def _find_text(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return article.xpath(self._xpath_selector_text)

    def _find_header(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return article.xpath(self._xpath_selector_header)

    ### "extract" methods that returns strings
    def _extract_tags(self, article: scrapy.selector.SelectorList) -> str:
        return convert_list_to_string(self._find_tags(article).extract(), ',')

    def _extract_text(self, article: scrapy.selector.SelectorList) -> str:
        return convert_list_to_string(self._find_text(article).extract(), '', handler=self._clear_text_field)

    def _extract_header(self, article: scrapy.selector.SelectorList) -> str:
        return self._find_header(article).extract_first()
