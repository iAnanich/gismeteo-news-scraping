import sys


class ArgumentsMaster:

    def __init__(self):
        self._args_dict = self._get_arguments()
        self.check_arguments()

    @staticmethod
    def _get_arguments() -> dict:
        arguments = sys.argv
        dictionary = {}
        for i in range(len(arguments)):
            if arguments[i] == '-a':
                args = arguments[i+1].split('=')
                dictionary[args[0]] = args[1]
        return dictionary

    def check_arguments(self):
        """ Define arguments name here"""
        try:
            self.api_key = self._args_dict['API_KEY']
            self.project_id = self._args_dict['PROJECT_ID']
            self.worksheet_tittle = self._args_dict['WORKSHEET_TITTLE']
        except Exception as e:
            raise RuntimeError('Unable to find expected argument:' + str(e))


start_arguments = ArgumentsMaster()
