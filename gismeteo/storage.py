import logging
from datetime import datetime

import gspread
import scrapy
from oauth2client.service_account import ServiceAccountCredentials as Creds

from . import settings as s
from .args import options


class StorageMaster:
    secret_file_name = s.GOOGLE_API_SECRET_FILENAME
    sheet_name = options.spreadsheet_title
    spider_to_worksheet_dict = options.spider_to_worksheet_dict

    def __init__(self):
        self._path_to_secret = options.get_path_to_file(self.secret_file_name)
        self._credentials = self._get_credentials()
        self._client = self._get_client()
        self.spreadsheet = self._client.open(self.sheet_name)

    def _get_credentials(self) -> Creds:
        return Creds.from_json_keyfile_name(self._path_to_secret, ['https://spreadsheets.google.com/feeds'])

    def _get_client(self) -> gspread.Client:
        return gspread.authorize(self._credentials)

    def get_worksheet_by_spider(self, spider: scrapy.spiders.Spider) -> gspread.Worksheet:
        try:
            index = self.spider_to_worksheet_dict[spider.name]
        except KeyError:
            raise RuntimeError('No worksheet configured for this spider: {}'.format(spider.name))
        try:
            worksheet = self.spreadsheet.get_worksheet(index)
            assert worksheet is not None
        except AssertionError:
            raise RuntimeError('No worksheet exist for this spider: {}/{}'.format(spider.name, index))
        return worksheet


class StorageSession:
    def __init__(self, worksheet: gspread.Worksheet, spider: scrapy.spiders.Spider):
        self._spider = spider
        self._worksheet = worksheet
        self._rows = None
        self._job_url = 'https://app.scrapinghub.com/p/{project_id}/{spider_id}/{job_id}'.format(
            project_id=options.current_project_id,
            spider_id=options.current_spider_id,
            job_id=options.current_job_id,
        )

    def open_session(self):
        logging.debug('<<< Session for #{spider_id} spider in "{worksheet_title}" worksheet STARTed.'.format(
            spider_id=options.current_spider_id,
            worksheet_title=self._worksheet.title,
        ))
        self._add_starting_row()
        self._rows = []
        return self

    def append_item(self, item: scrapy.item.Item) -> None:
        self._rows.append(Row(item).as_list())

    def close_session(self) -> None:
        self._add_ending_row()
        self._write_data()
        logging.debug('>>> Session for #{spider_id} spider in "{worksheet_title}" worksheet ENDed.'.format(
            spider_id=options.current_spider_id,
            worksheet_title=self._worksheet.title,
        ))

    def _write_data(self) -> None:
        for row in self._rows:
            self._worksheet.append_row(row)

    def _add_starting_row(self):
        self._worksheet.append_row(Row(
            url='-----',
            header='{date} / START "{name}" spider'.format(
                date=self._datetime(),
                name=self._spider.name,
            ),
            tags=self._job_url,
            text='-----',
        ).as_list())

    def _add_ending_row(self):
        self._rows.append(Row(
            url='-----',
            header='{date} / {count} articles scraped'.format(
                date=self._datetime(),
                count=str(len(self._rows)),
            ),
            tags=self._job_url,
            text='-----',
        ).as_list())

    def _datetime(self):
        return datetime.now().strftime('%m.%d %a %H:%M')


class Row:
    """ Place to configure fields order in a table"""
    columns_order = ['url', 'header', 'tags', 'text']

    def __init__(self, item: scrapy.item.Item or dict = None,
                 url: str = None,
                 header: str = None,
                 tags: str = None,
                 text: str = None):
        if item is not None:
            self.item = item
        else:
            self.item = dict(url=url, header=header, tags=tags, text=text)

    def as_list(self) -> list:
        lst = []
        for column in self.columns_order:
            lst.append(self.item[column])
        return lst
