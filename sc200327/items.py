# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsListItem(scrapy.Item):
    url = scrapy.Field()
    header = scrapy.Field()
    description = scrapy.Field()
    tag = scrapy.Field()


class LatestNewsIndexItem(scrapy.Item):
    index = scrapy.Field()


class EventItem(scrapy.Item):
    header = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
    text = scrapy.Field()
