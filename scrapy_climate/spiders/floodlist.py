# -*- coding: utf-8 -*-

from ..spider import TemplateSpider


class FloodListSpider(TemplateSpider):
    name = 'floodlist'

    _start_path = 'news'
    _start_domain = 'floodlist.com'
    _protocol = 'http'

    _css_selector_article = 'article[id*="post-"]'
    _xpath_selector_list_tags = ['div[@class="entry-content"]/p[@class="entry-tags"]/a/text()', ]
    _xpath_selector_list_text = ['div[@class="entry-content"]/p/text()', ]
    _xpath_selector_list_header = ['h1/text()', ]
    _css_selector_news_list = 'article[id*="post-"]'
    _xpath_selector_path = 'h2/a/@href'

    def _convert_path_to_index(self, path: str) -> str:
        return path.split('/')[-1]  # return last path part
