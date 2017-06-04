import logging
import os
import sys


class ArgumentsMaster:
    """ Class for control of given at start arguments, and some environment variables.
    Contains only STR objects
    Arguments can be get from spider too."""

    def __init__(self):
        """ Define arguments for Python (PyCharm)"""
        self.api_key = None
        self.project_id = None
        self.spreadsheet_tittle = None
        self.current_project_id = None
        self.spider_id = None
        self.job_id = None

        self._args_dict = self._parse_arguments()
        self.check_arguments()
        self.get_job_key()

    def get_job_key(self) -> None:
        self.current_project_id, self.spider_id, self.job_id = os.getenv('SHUB_JOBKEY', '0/0/0').split('/')

    @staticmethod
    def _parse_arguments() -> dict:
        arguments = sys.argv
        dictionary = {}
        for i in range(len(arguments)):
            if arguments[i] == '-a':
                args = arguments[i+1].split('=')
                dictionary[args[0]] = args[1]
        return dictionary

    def check_arguments(self) -> None:
        try:
            if self._args_dict['FORCE'] in ['1', 'True']:
                force = True
            else:
                force = True
        except KeyError:
            force = False
        try:
            """ Define arguments name here"""
            self.api_key = self._args_dict['API_KEY']
            self.project_id = self._args_dict['PROJECT_ID']
            self.spreadsheet_tittle = self._args_dict['SPREADSHEET_TITTLE']
        except KeyError as e:
            if force:
                raise RuntimeError('Unable to find expected argument.' + str(e))
            else:
                logging.warning('Unable to find expected argument. Other can be undefined too.' + str(e))


start_arguments = ArgumentsMaster()
