# -*- coding: utf-8 -*-

from scrapy_climate.tools import (
    HeaderExtractor,
    TagExtractor,
    LinkExtractor,
    TextExtractor,
)
from scrapy_climate.tools import SingleSpider


class GismeteoTextExtractor(TextExtractor):

    def extract_from(self, selector):
        selected = self.select_from(selector)
        elements = []
        for div in selected:
            link = div.css('div > a::text')
            picture = div.css('div > div.pic-descr::text')
            if link:
                link_extracted = link.extract_first()
                href_extracted = div.css('div > a::attr(href)').extract_first()
                for item in div.css('::text').extract():
                    if item == link_extracted:
                        elements.append(' [{0}]({1}) '.format(
                            link_extracted,
                            href_extracted, ))
                    else:
                        elements.append(item)
            elif picture:
                elements.append('<photo>')
            else:
                elements.append(div.css('div::text').extract_first())
        formatted = self._convert(elements)
        return formatted


class GismeteoUASpider(SingleSpider):

    name = 'gismeteo_ua'

    _start_path = 'news/'
    _start_domain = 'www.gismeteo.ua'
    _scheme = 'https'

    _link_extractor = LinkExtractor(
        list_of_string_css_selectors=[
            'div.item__title > a::attr(href)',
            'div.container-img > a::attr(href)'])
    _header_extractor = HeaderExtractor('div.article__h > h1::text')
    _tags_extractor = TagExtractor('div.article__tags > a::text')
    _text_extractor = GismeteoTextExtractor('div.article__i > div')

    def _convert_path_to_index(self, path: str) -> str:
        return path.split('/')[-2].split('-')[0]


class GismeteoRUSpider(GismeteoUASpider):

    name = 'gismeteo_ru'

    _start_domain = 'www.gismeteo.ru'
