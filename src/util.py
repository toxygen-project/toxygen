import os
import time
from platform import system


program_version = '0.1.2'


def log(data):
    with open(curr_directory() + '/logs.log', 'a') as fl:
        fl.write(str(data) + '\n')


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))


def curr_time():
    return time.strftime('%H:%M')


def convert_time(t):
    sec = int(t) - time.timezone
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return '%02d:%02d' % (h, m)


# obsolete
def get_style(style):
    if style != 'default':
        return style
    else:
        if system() == 'Windows':
            return 'windows'
        else:
            return 'gtk'


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls):
        return cls._instance
