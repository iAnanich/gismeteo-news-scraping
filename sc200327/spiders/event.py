# -*- coding: utf-8 -*-
import scrapy
from .tools import (fetch_latest_job,
                    get_arguments,
                    convert_list_to_string,
                    clear_text)
from .news import NewsListSpider
from ..items import EventItem


class EventSpider(scrapy.Spider):
    name = 'event'
    allowed_domains = ['www.gismeteo.ua']
    _cloud_run_arguments = get_arguments()

    def __init__(self, *args, **kwargs):
        # fetch urls from latest job
        table = fetch_latest_job(
            fields='url',
            project=self._cloud_run_arguments['PROJECT_ID'],
            key=self._cloud_run_arguments['API_KEY'],
            spider=NewsListSpider.name
        )[1:-1]  # get urls from NewsListItem items, because last one - NewsLatestIdItem
        urls = [x[0] for x in table]
        if len(urls) == 0:
            raise RuntimeError('No urls in previous jobs.')
        else:
            print(urls)
            self.start_urls = urls

        super().__init__()

    def parse(self, response: scrapy.http.Request):
        # locate article
        article = response.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]')
        # generate `tags` string
        tags_list = article.xpath('div[@class="article__tags links-grey"]/a/text()').extract()
        tags = convert_list_to_string(tags_list, ',')
        # generate `text` string
        text_blocks = article.xpath('div[@class="article__i ugc"]/div/text()').extract()#.re(r'"\s*(.*)"')
        text = convert_list_to_string(text_blocks, '', handler=clear_text)
        # produce item
        yield EventItem(
            url=response.url,
            header=article.xpath('div[@class="article__h"]/h1/text()').extract_first(),
            tags=tags,
            text=text,
        )
