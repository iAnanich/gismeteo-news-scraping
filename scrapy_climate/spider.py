# -*- coding: utf-8 -*-

import scrapy

from .items import EventItem
from .tools import convert_list_to_string, fetch_scraped_indexes


class TemplateSpider(scrapy.Spider):
    name = None
    """ Spider name. """
    _start_path = None
    """ Relative path to page with news list. Used for `start_urls` field. 
    Minimal value = '/' """
    _start_domain = None
    """ First and only element of `allowed_domains` field. """
    _protocol = None
    """ 'http' or 'https' """

    _xpath_selector_list_tags = None
    _xpath_selector_list_text = None
    _xpath_selector_list_header = None
    """ These three `_xpath_selector_list_*` are used to find needed data by multiple selectors
    in different places. Must contain list of strings or tuple of strings."""
    _xpath_selector_path = None
    """ `_xpath_selector_path` is used to find relative href to article page when scraping from
    news list page. Must contain string."""
    _css_selector_news_list = None
    _css_selector_article = None
    """ These two `_css_selector_*` fields are used to locate news list div tag on news list page and
    to locate article div tag on article page. Must contain string."""

    ### "parse" methods
    def parse(self, response: scrapy.http.Response):
        self._scraped_indexes = self._scraped_in_past
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
        raise NotImplementedError

    def _check_field_implementation(self, field_name: str):
        value = self.__getattribute__(field_name)
        if value is not None:
            return value
        else:
            raise NotImplementedError('Need to define "{}" field.'.format(field_name))

    @property
    def _scraped_in_past(self):
        return fetch_scraped_indexes(self.name)

    ### "yield" methods that returns generators
    def _yield_request(self, path_or_url: str):
        if '://' in path_or_url:
            url = path_or_url
            # extracting relative path from url
            _protocol = self._protocol + '://'
            path = path_or_url[path_or_url[len(_protocol):].find('/') + len(_protocol) + 1:]
        else:
            path = path_or_url
            url = '{protocol}://{host}/{path}'.format(protocol=self._protocol, host=self.allowed_domains[0], path=path)
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
    def _find_by_xpath_list(self, article: scrapy.selector.SelectorList, xpath_string_selectors_list: list or tuple) -> scrapy.selector.SelectorList:
        selector_list = article.xpath(xpath_string_selectors_list[0])
        for string_selector in xpath_string_selectors_list[1:]:
            selector_list.extend(article.xpath(string_selector))
        return selector_list

    def _find_article_in_responce(self, response: scrapy.http.Response) -> scrapy.selector.SelectorList:
        return response.css(self._css_selector_article)

    def _find_news_list_in_responce(self, response: scrapy.http.Response) -> scrapy.selector.SelectorList:
        return response.css(self._css_selector_news_list)

    def _find_tags_in_article(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return self._find_by_xpath_list(article, self._xpath_selector_list_tags)

    def _find_text_in_article(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return self._find_by_xpath_list(article, self._xpath_selector_list_text)

    def _find_header_in_article(self, article: scrapy.selector.SelectorList) -> scrapy.selector.SelectorList:
        return self._find_by_xpath_list(article, self._xpath_selector_list_header)

    ### "extract" methods that returns strings
    def _extract_tags(self, article: scrapy.selector.SelectorList) -> str:
        return convert_list_to_string(self._find_tags_in_article(article).extract(), ',')

    def _extract_text(self, article: scrapy.selector.SelectorList) -> str:
        return convert_list_to_string(self._find_text_in_article(article).extract(), '', handler=self._clear_text_field)

    def _extract_header(self, article: scrapy.selector.SelectorList) -> str:
        return self._find_header_in_article(article).extract_first()

    @property
    def allowed_domains(self):
        return [self._check_field_implementation('_start_domain'), ]

    @property
    def start_urls(self):
        return ['{}://{}/{}'.format(self._check_field_implementation('_protocol'),
                                    self._check_field_implementation('_start_domain'),
                                    self._check_field_implementation('_start_path')), ]

