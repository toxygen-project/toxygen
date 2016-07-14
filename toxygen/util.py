import os
import time
import shutil

program_version = '0.2.3'


def log(data):
    with open(curr_directory() + '/logs.log', 'a') as fl:
        fl.write(str(data) + '\n')


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))


def curr_time():
    return time.strftime('%H:%M')


def copy(src, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest)
        else:
            copy(full_file_name, os.path.join(dest, file_name))


def convert_time(t):
    sec = int(t) - time.timezone
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return '%02d:%02d' % (h, m)


class Singleton:
    _instance = None

    def __init__(self):
        self.__class__._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance
