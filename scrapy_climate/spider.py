# -*- coding: utf-8 -*-
""" Module for spider class templates.

    Entities:
    * news-list page - page on the web-site that have HTML tag (e. g.
    "news-list tag") with multiple childes, where every child HTML tag
    contains a link to an "article page"
    * news-list tag - HTML tag  with multiple childes, where every child HTML
    tag contains a link to an "article page"
    * article page - page on the same web-site that have HTML tag (e. g.
    "article tag") with childes that have all needed data as header, tags etc.
    * article tag - HTML tag  with childes that have all data for scraping
    * index - part of the article page URL that can be used to identify the
    article page to not scrape it twice
    * callback - method which takes request and yields another request or item
"""

import scrapy

from urllib.parse import urlparse, urlunparse
from scrapy.http import Response, Request

from .items import ArticleItem
from .tools import fetch_scraped_indexes
from .mixins import ParserMixin


class TemplateSpider(scrapy.Spider, ParserMixin):
    """
    This class must not be used properly, only for inheritance.

    It implements Scrapy spider callbacks for scraping articles from news-like
    web-site, without duplicates (see `fetch_scraped_indexes` function in the
    `tools` module.)

    What must be implemented for usage?
    * class fields: `name`, `_start_path`, `_start_domain`, `_scheme`
    * class fields from mixins: `_css_selector_article`,
    `_css_selector_news_list`, `xpath_selector_list_header`,
    `_xpath_selector_list_tags`, `_xpath_selector_path_or_url`
    * methods: `_convert_path_to_index`

    How it works at all:
    1. first request is to `start_urls`'s first (and only) URL, that depends
    on `_start_path` and `_start_domain` and `_scheme` class fields.
    2. `parse` callback spider calls `fetch_scraped_indexes` to get
    list of scraped yet articles and stores it
    3. then `_yield_requests_from_response` extracts links to "article pages"
    from response by calling `_find_news_list_in_response` to locate the
    "news-list tag" and `_extract_ul_or_path` to get URL or path to an
    "article page" that passes to `_yield_request` method
    4. `_yield_request` method parses given `url_or_path` argument to yield
    request to "article page" with `parse_article` callback
    5. `parse_article` finds `article` selector and passes extracted header,
    tags etc. to `_yield_article_item` method
    6. `_yield_article_item` method ads to item arguments that can be
    extracted just from response.
    """

    # Just a spider name used by Scrapy to identify it.
    # Must be a string.
    name = None

    # URL path to the "news-list page". Used for `start_urls` field.
    # Must be a string. Minimal value: ''
    _start_path = None

    # URL host of the web-site. Used for `allowed_domains` field.
    # Must be a string. Example: 'www.example.com'
    _start_domain = None

    # URL scheme. Allowed values: 'http', 'https'
    _scheme = None

    def __init__(self, *args, **kwargs):
        # fetch scraped in the past "indexes" by getting value from property
        self._scraped_indexes = self._scraped_in_past
        # instantiate `scrapy.Spider` class
        super().__init__(*args, **kwargs)

    # =================
    #  "parse" methods
    # =================
    # there are "callbacks" that scrapes data from page (response)
    def parse(self, response: Response):
        """
        "callback" for "news-list page" that yields requests to "article pages"
        with `parse_article` "callback".
        :param response: `scrapy.http.Response` from "news-list page"
        :return: yields requests to "article pages"
        """
        # parse response and yield requests with `parse_article` "callback"
        yield from self._yield_requests_from_response(response)

    def parse_article(self, response: Response):
        """
        "callback" for "article page" that yields `ArticleItem` items.
        :param response: `Scrapy.http.Response` instance from "article page"
        :return: yields `ArticleItem` instance
        """
        # locate article
        article = self._find_article_in_response(response)
        # produce item
        yield from self._yield_article_item(
            response,
            text=self._extract_text(article),
            header=self._extract_header(article),
            tags=self._extract_tags(article),
        )

    # ============
    #  generators
    # ============
    # these methods are used to yield requests of items
    def _yield_request(self, path_or_url: str):
        """
        Yields `scrapy.http.Request` with `parse_article` "callback" and meta
        "index" if "index" wasn't scraped yet. Method checks if passed
        `path_or_url` argument is an URL or URL path, but in both cases method
        know both URL and path, because URL is required to instantiate request
        and path is required to extract "index" from it.
        :param path_or_url: URL itself or URL path
        :return: yields `scrapy.http.Request` with `parse_article` "callback"
        """
        if '://' in path_or_url:
            url = path_or_url
            path = urlparse(url)[2]
        else:
            path = path_or_url
            url = urlunparse([self._scheme, self._start_domain, path,
                              None, None, None])
        index = self._convert_path_to_index(path)
        if index not in self._scraped_indexes:
            yield Request(url=url,
                          callback=self.parse_article,
                          meta={'index': index})

    def _yield_requests_from_response(self, response: Response):
        """
        Parses response from "news-list page" and yields requests to
        "article pages" that aren't scraped yet.
        :param response: `scrapy.http.Response` from "news-list page"
        :return: yield `scrapy.http.Request` instance
        """
        for block in list(self._find_news_list_in_response(response)):
            yield from self._yield_request(
                self._extract_url_or_path_from_block(block))

    def _yield_article_item(self, response: Response, **kwargs):
        """
        Yields `ArticleItem` instances with `url` and `index` arguments
        extracted from given `response` object.
        :param response: `scrapy.http.Response` from "article page"
        :param kwargs: fields for `ArticleItem`
        :return: yields `ArticleItem` instance
        """
        yield ArticleItem(
            url=response.url,
            index=response.meta['index'],
            **kwargs
        )

    # ============
    #  properties
    # ============
    # these properties checks if child class has implemented all needed fields
    @property
    def allowed_domains(self):
        return [self._check_field_implementation('_start_domain'), ]

    @property
    def start_urls(self):
        return ['{}://{}/{}'.format(
            self._check_field_implementation('_scheme'),
            self._check_field_implementation('_start_domain'),
            self._check_field_implementation('_start_path')), ]

    # =========
    #  helpers
    # =========
    def _convert_path_to_index(self, path: str) -> str:
        """
        Extracts "index" (see entities in the `TemplateSpider` class'
        docstring) from given URL path.
        :param path: URL path string
        :return: `index` string
        """
        raise NotImplementedError

    def _check_field_implementation(self, field_name: str):
        """
        Checks if class have implemented field (attribute) with given name
        (string value of `field_name`)
        :param field_name: string that matches class field name
        :raises NotImplementedError: if class doesn't have implemented field
        with `field_name` name
        :return: value if field value isn't `None`, else raises exception
        """
        value = self.__getattribute__(field_name)
        if value is not None:
            return value
        else:
            raise NotImplementedError('Need to define "{}" field.'
                                      .format(field_name))

    @property
    def _scraped_in_past(self):
        """
        Uses `tools.fetch_scraped_indexes` to fetch "indexes" scraped from
        last week by using Scrapy Cloud API.
        :return: list of "indexes" strings
        """
        return fetch_scraped_indexes(self.name)
