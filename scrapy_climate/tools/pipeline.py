import logging

from .item import ArticleItem
from .args import options
from .cloud import CloudInterface
from .spider import SingleSpider
from .storage import StorageMaster, StorageSession


def _check_need_in_storage() -> bool:
    option = options.enable_gspread
    if option in ['True', '1']:
        return True
    elif option in ['False', '0']:
        return False
    else:
        raise RuntimeError('Cannot recognise is need to use `storage`: {}'
                           .format(option))

ENABLE_STORAGE = _check_need_in_storage()


class StoragePipeline(object):

    def __init__(self):
        self.storage_session = None
        self.cloud = None

    def open_spider(self, spider: SingleSpider):
        self.cloud = CloudInterface()
        spider.connect_cloud(self.cloud)

        if ENABLE_STORAGE:
            self.storage_session = StorageSession(
                StorageMaster().get_worksheet_by_spider(spider), spider)
            self.storage_session.open_session()

    def close_spider(self, spider: SingleSpider):
        if self.storage_session:
            self.storage_session.close_session()

    def process_item(self, item: ArticleItem, spider: SingleSpider):
        if isinstance(item, ArticleItem):
            if self.storage_session:
                self.storage_session.append_item(item)
            return item
        else:
            msg = 'Unknown item type: ' + item.__repr__()
            logging.warning(msg)
            print('WARNING ::', msg)
            return item
