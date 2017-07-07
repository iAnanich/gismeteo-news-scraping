import argparse
import logging
from datetime import datetime

import gspread
from . import Row, master


def new_worksheet(title: str =None, index: int =-1, force: bool =False) -> gspread.Worksheet:
    spreadsheet = master().spreadsheet
    worksheets_list = spreadsheet.worksheets()
    if title is None:
        title = 'created by script ' + str(datetime.now())
    if index in range(len(worksheets_list)):
        if force:
            del_worksheet = spreadsheet.get_worksheet(index)
            logging.warning('Replacing existed worksheet: "{}" #{}'.format(worksheets_list, index))
            spreadsheet.del_worksheet(del_worksheet)
        else:
            raise RuntimeError('defined index is already in use')
    # append new worksheet
    worksheet = spreadsheet.add_worksheet(title=title, rows=1,
                                          cols=len(Row.columns_order),)
    for i, string in enumerate(Row.columns_order):
        worksheet.update_cell(row=1, col=i+1, val=string)
    return worksheet


if __name__ == '__main__':
    new_worksheet()
