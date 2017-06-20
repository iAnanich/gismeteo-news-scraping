# -*- coding: utf-8 -*-

from ..spider import TemplateSpider


class VulcanSpider(TemplateSpider):
    name = 'vulcan'

    _start_path = ''
    _start_domain = 'izverzhenie-vulkana.ru'
    _protocol = 'http'

    _css_selector_article = 'div[style="padding-left: 15; padding-right: 15;"]'
    _xpath_selector_list_tags = ['div[@style="padding-top: 15; padding-bottom:30;"]/p[@style="color: #ffffff;"]/a/text()', ]
    _xpath_selector_list_text = ['div[@class="sp-text"]//p/text()',
                                 'div[@class="sp-text"]/article/text()',
                                 'div[@class="sp-text"]//span/text()', ]
    _xpath_selector_list_header = ['div[@style="padding-top: 15; padding-bottom:30;"]/h1/text()', ]
    _css_selector_news_list = 'div[style="padding-left: 0; padding-right: 15; padding-bottom: 31; float: left;height:640;overflow:hidden;"]'
    _xpath_selector_path = 'table/tr[2]/td/a/@href'

    def _convert_path_to_index(self, path: str) -> str:
        return path.split('/')[-1][:-5]   # return page name without `.html` at the end.
