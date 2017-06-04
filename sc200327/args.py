import sys


class ArgumentsMaster:
    """ Class for control of given at tart arguments. Arguments can be get from spider."""
    # TODO: try move this logic to spiders

    def __init__(self):
        self.api_key = None
        self.project_id = None
        self.spreadsheet_tittle = None

        self._args_dict = self._parse_arguments()
        self.check_arguments()

    @staticmethod
    def _parse_arguments() -> dict:
        arguments = sys.argv
        dictionary = {}
        for i in range(len(arguments)):
            if arguments[i] == '-a':
                args = arguments[i+1].split('=')
                dictionary[args[0]] = args[1]
        return dictionary

    def check_arguments(self):
        try:
            if self._args_dict['FORCE'] in ['1', 'True']:
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
                RuntimeWarning('Unable to find expected argument. Other can be undefined too.' + str(e))


start_arguments = ArgumentsMaster()
