import json
import os
import sys

from . import settings as s


class ArgumentsMaster:
    """ Class for control of given at start arguments, and some environment variables.
    Contains only STR objects
    Arguments can be get from spider too."""
    jobkey_env_varname = 'SHUB_JOBKEY'
    options_filename = s.OPTIONS_FILENAME

    def __init__(self):
        self._env_dict = self._parse_env()
        self._args_dict = self._parse_arguments()
        self._file_dict = self._parse_file()

    def get_value(self, key: str):
        try:
            value = self._args_dict[key]
        except KeyError:
            try:
                value = self._file_dict[key]
            except KeyError:
                raise RuntimeError('Unable to find expected argument: ' + key)
            else:
                return value
        else:
            return value

    def _parse_env(self) -> dict:
        tupl = os.getenv(self.jobkey_env_varname, '0/0/0').split('/')
        return {
            'CURRENT_PROJECT_ID': tupl[0],
            'CURRENT_SPIDER_ID': tupl[1],
            'CURRENT_JOB_ID': tupl[2],
        }

    def _parse_arguments(self) -> dict:
        arguments = sys.argv
        dictionary = {}
        for i in range(len(arguments)):
            if arguments[i] == '-a':
                args = arguments[i+1].split('=')
                dictionary[args[0]] = args[1]
        return dictionary

    def _parse_file(self) -> dict:
        return json.load(open(self.get_path_to_file(self.options_filename), 'r'))

    @staticmethod
    def get_path_to_file(file_name: str) -> str:
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)

    @property
    def current_project_id(self) -> str:
        return self._env_dict['CURRENT_PROJECT_ID']

    @property
    def current_spider_id(self) -> str:
        return self._env_dict['CURRENT_SPIDER_ID']

    @property
    def current_job_id(self) -> str:
        return self._env_dict['CURRENT_JOB_ID']

    @property
    def spreadsheet_title(self) -> str:
        return self.get_value('SPREADSHEET_TITLE')

    @property
    def api_key(self) -> str:
        return self.get_value('SCRAPY_CLOUD_API_KEY')

    @property
    def spider_to_worksheet_dict(self) -> str:
        return self.get_value('SPIDER_TO_WORKSHEET_DICTIONARY')

    @property
    def project_id(self) -> str:
        return self.get_value('SCRAPY_CLOUD_PROJECT_ID')


options = ArgumentsMaster()
