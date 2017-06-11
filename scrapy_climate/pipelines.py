# -*- coding: utf-8 -*-

import json
import logging

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy

from .args import options
from .items import EventItem, ScrapedUrlsItem
from .storage import StorageMaster, StorageSession
from .tools import fetch_latest_job


class Sc200327Pipeline(object):
    _field_name = 'indexes_json_string'
    _max_list_length = 100

    def __init__(self):
        self.storage_session = None
        self._scraped_indexes_list = []

    def open_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session = StorageSession(StorageMaster().get_worksheet_by_spider(spider),
                                              spider).open_session()
        self._fetch_latest_urls(spider)

    def close_spider(self, spider: scrapy.spiders.Spider):
        self.storage_session.close_session()

    def process_item(self, item: scrapy.item.Item, spider: scrapy.spiders.Spider):
        if isinstance(item, EventItem):
            index = item['index']
            if index not in self._scraped_indexes_list:
                self.storage_session.append_item(item)
                self._scraped_indexes_list.append(index)
                return item
            else:
                raise scrapy.exceptions.DropItem('Item has been scraped yet: ' + index)
        elif isinstance(item, ScrapedUrlsItem):
            indexes = item['tmp_list']
            self._scraped_indexes_list = indexes
            diff = len(indexes) - self._max_list_length
            if diff > 0:
                for i in range(diff):
                    indexes.pop(i)
            item[self._field_name] = json.dumps(indexes)
            item['tmp_list'] = None
            return item
        else:
            logging.warning('Unknown item type: ' + item.__repr__())
            return item

    def _fetch_latest_urls(self, spider):
        table = fetch_latest_job(
            spider=spider.name,
            fields=self._field_name,
            project=options.project_id,
            key=options.api_key
        )
        if len(table) == 1:  # if there is only field name
            logging.warning('No items from previous jobs')
        else:  # needed item must be at the end
            list_json_string = table[-1][0]
            if list_json_string == '':
                logging.warning('No {} field from previous job')
            else:
                self._scraped_indexes_list = json.loads(list_json_string)
