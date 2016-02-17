from platform import system
import json
import os


class Settings(object):

    def __init__(self):
        self.path = Settings.get_default_path() + 'toxygen.json'
        if os.path.exists(self.path):
            with open(self.path) as fl:
                data = fl.read()
            self.data = json.loads(data)
        else:
            self.create_default_settings()
            self.save()

    def create_default_settings(self):
        self.data = {
            "theme": "default",
            "ipv6_enabled": True,
            "udp_enabled": True,
            "proxy_type": 0,
            "proxy_host": "0",
            "proxy_port": 0,
            "start_port": 0,
            "end_port": 0,
            "tcp_port": 0,
            "notifications": True,
            "sound_notifications": False,
            "language": "en-en",
            "save_history": False,
            "allow_inline": True,
            "allow_auto_accept": False,
            "auto_accept_from_friends": [],
            "friends_aliases": [],
            "typing_notifications": True
        }

    def __get__(self, attr):
        return self.data[attr]

    def __set__(self, attr, value):
        self.data[attr] = value

    def save(self):
        text = json.dumps(self.data)
        with open(self.path, 'w') as fl:
            fl.write(text)

    @staticmethod
    def get_default_path():
        if system() == 'Linux':
            return os.getenv('HOME') + '/.config/tox/'
        elif system() == 'Windows':
            return os.getenv('APPDATA') + '/Tox/'

