# -*- coding: utf-8 -*-
""" Module for mixins for spiders.

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

from scrapy.http import Response
from scrapy.selector import SelectorList

from .tools import convert_list_to_string


class ParserMixin:

    # CSS selectors for finding "news-list tag"/"article tag"
    # on "news-list page"/"article page" in the response
    # Must be a string.
    _css_selector_news_list = None
    _css_selector_article = None

    # XPATH selector used to find path or url to "article page" under
    # "news-list tag". It is relative selector.
    # Must be a string.
    _xpath_selector_path_or_url = None

    # XPATH selector lists used to find needed data on the "article page"
    # under "article tag". There are relative selectors.
    # Must be a string.
    _xpath_selector_list_tags = None
    _xpath_selector_list_text = None
    _xpath_selector_list_header = None

    # ================
    #  "find" methods
    # ================
    # uses `SelectorList` to find specific HTML tag on the page or inside
    # another HTML tag
    def _find_article_in_response(self, response: Response) -> SelectorList:
        return response.css(self._css_selector_article)

    def _find_news_list_in_response(self, response: Response) -> SelectorList:
        return response.css(self._css_selector_news_list)

    def _find_tags_in_article(self, article: SelectorList) -> SelectorList:
        return self._find_by_xpath_list(article,
                                        self._xpath_selector_list_tags)

    def _find_text_in_article(self, article: SelectorList) -> SelectorList:
        return self._find_by_xpath_list(article,
                                        self._xpath_selector_list_text)

    def _find_header_in_article(self, article: SelectorList) -> SelectorList:
        return self._find_by_xpath_list(article,
                                        self._xpath_selector_list_header)

    # ===================
    #  "extract" methods
    # ===================
    # uses `SelectorList.extract` method to extract data from HTML tag
    def _extract_tags(self, article: SelectorList) -> str:
        return convert_list_to_string(
            self._find_tags_in_article(article).extract(), ',')

    def _extract_text(self, article: SelectorList) -> str:
        return convert_list_to_string(
            self._find_text_in_article(article).extract(),
            separator='',
            handler=self._clear_text_field,)

    def _extract_header(self, article: SelectorList) -> str:
        return self._find_header_in_article(article).extract_first()

    def _extract_url_or_path_from_block(self, block: SelectorList) -> str:
        return block.xpath(self._xpath_selector_path_or_url).extract_first()

    # =========
    #  helpers
    # =========
    @staticmethod
    def _find_by_xpath_list(
            article: SelectorList,
            xpath_string_selectors_list: list or tuple) -> SelectorList:
        """
        Iterates over XPATH string selectors in
        `xpath_string_selector_list` uses them for `article` selector and
        returns SelectorList of results.
        :param article: SelectorList that matches "article tag"
        :param xpath_string_selectors_list: list or tuple of string XPATH
        selectors for `article` selector
        :return: SelectorList with selector fo every given string selector
        in `xpath_string_selector_list` in `article` selector
        """
        return SelectorList([article.xpath(selector)
                             for selector in xpath_string_selectors_list])[0]

    def _clear_text_field(self, text: str) -> str:
        """
        Function clears text from different special characters that must be
        in the worksheet.
        :param text: string that must be cleared from unneeded characters
        :return: cleared string
        """
        return str(text).replace('\xa0', ' ').replace('\n', '')
