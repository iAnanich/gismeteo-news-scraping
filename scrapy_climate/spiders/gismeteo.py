# -*- coding: utf-8 -*-

from scrapy_climate.tools import (
    HeaderExtractor,
    TagExtractor,
    LinkExtractor,
    TextExtractor,
)
from scrapy_climate.tools import SingleSpider


class GismeteoSpider(SingleSpider):
    name = 'gismeteo'

    _start_path = 'news/'
    _start_domain = 'www.gismeteo.ua'
    _scheme = 'https'

    _link_extractor = LinkExtractor(
        list_of_string_css_selectors=[
            'div.item__title > a::attr(href)',
            'div.container-img > a::attr(href)'])
    _header_extractor = HeaderExtractor('div.article__h > h1::text')
    _tags_extractor = TagExtractor('div.article__tags > a::text')
    _text_extractor = TextExtractor('div.article__i > div')

    def _convert_path_to_index(self, path: str) -> str:
        return path.split('/')[-2].split('-')[0]
