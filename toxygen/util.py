import os
import time
import shutil
import sys
import re


program_version = '0.3.0'


def cached(func):
    saved_result = None

    def wrapped_func():
        nonlocal saved_result
        if saved_result is None:
            saved_result = func()

        return saved_result

    return wrapped_func


def log(data):
    try:
        with open(curr_directory() + '/logs.log', 'a') as fl:
            fl.write(str(data) + '\n')
    except:
        pass


@cached
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
    offset = time.timezone + time_offset() * 60
    sec = int(t) - offset
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return '%02d:%02d' % (h, m)


@cached
def time_offset():
    hours = int(time.strftime('%H'))
    minutes = int(time.strftime('%M'))
    sec = int(time.time()) - time.timezone
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    result = hours * 60 + minutes - h * 60 - m
    return result


def append_slash(s):
    if len(s) and s[-1] not in ('\\', '/'):
        s += '/'
    return s


@cached
def is_64_bit():
    return sys.maxsize > 2 ** 32


def is_re_valid(regex):
    try:
        re.compile(regex)
    except re.error:
        return False
    else:
        return True


class Singleton:
    _instance = None

    def __init__(self):
        self.__class__._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance
