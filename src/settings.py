import getpass
import platform
import json


class Settings(object):

    def __init__(self):
        path = Settings.get_default_path() + 'toxygen.json'
        with open(path) as fl:
            data = fl.read()
        self.data = json.loads(data)

    def __get__(self, attr):
        return self.data[attr]

    @staticmethod
    def get_default_path():
        name = platform.system()
        if name == 'Linux':
            user = getpass.getuser()
            return '/home/{}/.config/tox/'.format(user)
