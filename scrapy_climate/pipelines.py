# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

from .items import LatestNewsIndexItem
from .storage import StorageMaster, StorageSession


class Sc200327Pipeline(object):

    def open_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session = StorageSession(StorageMaster().get_worksheet_by_spider(spider),
                                              spider).open_session()

    def close_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session.close_session()

    def process_item(self, item: scrapy.item.Item, spider: scrapy.spiders.Spider):
        if not isinstance(item, LatestNewsIndexItem):
            self.storage_session.append_item(item)
        return item
