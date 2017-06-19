# -*- coding: utf-8 -*-

import json
import logging

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

from .args import options
from .items import EventItem
from .storage import StorageMaster, StorageSession


class Sc200327Pipeline(object):

    def __init__(self):
        self.storage_session = None

    def open_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session = StorageSession(StorageMaster().get_worksheet_by_spider(spider),
                                              spider).open_session()

    def close_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session.close_session()

    def process_item(self, item: scrapy.item.Item, spider: scrapy.spiders.Spider):
        if isinstance(item, EventItem):
            self.storage_session.append_item(item)
            return item
        else:
            logging.warning('Unknown item type: ' + item.__repr__())
            return item
