import os
import time
import shutil
import sys

program_version = '0.2.6'


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


def remove(folder):
    if os.path.isdir(folder):
        shutil.rmtree(folder)


def convert_time(t):
    offset = time.timezone - time.daylight * 3600
    sec = int(t) - offset
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return '%02d:%02d' % (h, m)


def append_slash(s):
    if len(s) and s[-1] not in ('\\', '/'):
        s += '/'
    return s


def is_64_bit():
    return sys.maxsize > 2 ** 32


class Singleton:
    _instance = None

    def __init__(self):
        self.__class__._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance
