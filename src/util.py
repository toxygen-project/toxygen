import os
import time

program_version = '0.0.1 (alpha)'


def log(data):
    with open('logs.log', 'a') as fl:
        fl.write(str(data) + '\n')


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))


def curr_time():
    return time.strftime("%H:%M")


class Singleton(object):

    def __new__(cls, *args):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Singleton, cls,).__new__(cls, *args)
        return cls.instance
