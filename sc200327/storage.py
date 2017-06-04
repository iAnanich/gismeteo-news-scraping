import os
from datetime import datetime

import gspread
import scrapy
from oauth2client.service_account import ServiceAccountCredentials as Creds

from .args import start_arguments


class StorageMaster:
    secret_file_name = 'client-secret.json'
    sheet_name = start_arguments.spreadsheet_tittle

    def __init__(self):
        self._path_to_secret = self.get_path_to_file(self.secret_file_name)
        self._credentials = self._get_credentials()
        self._client = self._get_client()
        self._spreadsheet = self._client.open(self.sheet_name)

    @staticmethod
    def get_path_to_file(file_name: str) -> str:
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)

    def _get_credentials(self) -> Creds:
        return Creds.from_json_keyfile_name(self._path_to_secret, ['https://spreadsheets.google.com/feeds'])

    def _get_client(self) -> gspread.Client:
        return gspread.authorize(self._credentials)

    @property
    def spreadsheet(self) -> gspread.Spreadsheet:
        return self._spreadsheet


class StorageSession:
    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self._spreadsheet = spreadsheet
        spider = int(start_arguments.spider_id)
        self._worksheet = self._spreadsheet.get_worksheet(spider - 1)
        if self._worksheet is None:
            raise RuntimeError('No Worksheet with this id: ' + str(spider - 1))
        self._rows = None

    def open_session(self):
        print('<<< Session for #{spider} spider in "{tittle}" worksheet STARTed.'.format(
            spider=start_arguments.spider_id,
            tittle=self._worksheet.title,
        ))
        self._rows = []
        return self

    def append_item(self, item: scrapy.item.Item) -> None:
        self._rows.append(Row(item).as_list())

    def close_session(self) -> None:
        self._add_ending_row()
        self._write_data()
        print('>>> Session for #{spider} spider in "{tittle}" worksheet ENDed.'.format(
            spider=start_arguments.spider_id,
            tittle=self._worksheet.title,
        ))

    def _write_data(self) -> None:
        for row in self._rows:
            self._worksheet.append_row(row)

    def _add_ending_row(self):
        self._rows.append(Row({
            'url': 'https://app.scrapinghub.com/p/{project}/{spider}/{job}'.format(
                project=start_arguments.project_id,
                spider=start_arguments.spider_id,
                job=start_arguments.job_id,
            ),
            'header': str(datetime.now()),
            'tags': '{} articles scraped'.format(str(len(self._rows))),
            'text': '-----',
        }).as_list())


class Row:

    def __init__(self, item: scrapy.item.Item or dict):
        self.item = item

    def as_list(self) -> list:
        """ Place to configure fields order in a table"""
        return [
            self.item['url'],
            self.item['header'],
            self.item['tags'],
            self.item['text'],
        ]
