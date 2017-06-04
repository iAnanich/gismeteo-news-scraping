# -*- coding: utf-8 -*-
import scrapy

from .news import NewsListSpider
from .tools import (fetch_latest_job,
                    convert_list_to_string,
                    clear_text)
from ..args import start_arguments
from ..items import EventItem


class EventSpider(scrapy.Spider):
    name = 'event'
    allowed_domains = ['www.gismeteo.ua']

    def __init__(self, *args, **kwargs):
        # fetch urls from latest job
        table = fetch_latest_job(
            fields='url',
            project=start_arguments.project_id,
            key=start_arguments.api_key,
            spider=NewsListSpider.name
        )[1:-1]  # get urls from NewsListItem items, because last one - NewsLatestIdItem
        urls = [x[0] for x in table]
        if len(urls) == 0:
            RuntimeWarning('No urls in previous jobs.')
            self.start_urls = []
        else:
            self.start_urls = urls

        super().__init__()

    def parse(self, response: scrapy.selector.Selector or scrapy.http.Request):
        # locate article
        article = response.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]')
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
