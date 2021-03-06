# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EventItem(scrapy.Item):
    header = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
    text = scrapy.Field()
    video = scrapy.Field()
    phoro = scrapy.Field()

    index = scrapy.Field()
