# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

from .items import EventItem
from .spiders.combine import CombineSpider
from .spiders.event import EventSpider
from .storage import StorageMaster, StorageSession


class Sc200327Pipeline(object):

    def __init__(self):
        self.use_storage = False
        self.storage_session = None

    def open_spider(self, spider: scrapy.spiders.Spider):
        if isinstance(spider, (EventSpider, CombineSpider)):
            self.storage_session = StorageSession(StorageMaster().spreadsheet).open_session()
            self.use_storage = True

    def close_spider(self, spider: scrapy.spiders.Spider):
        if self.use_storage:
            self.storage_session.close_session()

    def process_item(self, item: scrapy.item.Item, spider: scrapy.spiders.Spider):
        if self.use_storage and isinstance(item, EventItem):
            self.storage_session.append_item(item)
        return item
