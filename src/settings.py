from platform import system
import json
import os
from util import Singleton


class Settings(dict, Singleton):

    def __init__(self, name=''):
        self.path = Settings.get_default_path() + str(name) + '.json'
        if os.path.isfile(self.path):
            with open(self.path) as fl:
                data = fl.read()
            super(self.__class__, self).__init__(json.loads(data))
        else:
            super(self.__class__, self).__init__(Settings.get_default_settings())
            self.save()

    @staticmethod
    def get_auto_profile():
        path = Settings.get_default_path() + 'toxygen.json'
        if os.path.isfile(path):
            with open(path) as fl:
                data = fl.read()
            auto = json.loads(data)
            return auto['path'], auto['name']
        else:
            return None

    @staticmethod
    def set_auto_profile(path, name):
        p = Settings.get_default_path() + 'toxygen.json'
        data = json.dumps({'path': path, 'name': name})
        with open(p, 'w') as fl:
                fl.write(data)

    @staticmethod
    def get_default_settings():
        return {
            'theme': 'default',
            'ipv6_enabled': True,
            'udp_enabled': True,
            'proxy_type': 0,
            'proxy_host': '0',
            'proxy_port': 0,
            'start_port': 0,
            'end_port': 0,
            'tcp_port': 0,
            'notifications': True,
            'sound_notifications': False,
            'language': 'en-en',
            'save_history': False,
            'allow_inline': True,
            'allow_auto_accept': False,
            'show_online_friends': False,
            'auto_accept_from_friends': [],
            'friends_aliases': [],
            'typing_notifications': True,
            'calls_sound': True
        }

    def save(self):
        text = json.dumps(self)
        with open(self.path, 'w') as fl:
            fl.write(text)

    @staticmethod
    def get_default_path():
        if system() == 'Linux':
            return os.getenv('HOME') + '/.config/tox/'
        elif system() == 'Windows':
            return os.getenv('APPDATA') + '/Tox/'
