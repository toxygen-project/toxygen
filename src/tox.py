# -*- coding: utf-8 -*-
from ctypes import *
from settings import Settings
import os


class ToxOptions(Structure):
    _fields_ = [
        ("ipv6_enabled", c_bool),
        ("udp_enabled", c_bool),
        ("proxy_type", c_int),
        ("proxy_host", c_char_p),
        ("proxy_port", c_uint16),
        ("start_port", c_uint16),
        ("end_port", c_uint16),
        ("tcp_port", c_uint16),
        ("savedata_type", c_int),
        ("savedata_data", c_char_p),
        ("savedata_length", c_size_t)
        ]


class Tox(object):

    def __init__(self, name, path=None):
        if path is None:
            path = Settings.get_default_path()
        full_path = path + name + '.tox'
        with open(full_path, 'rb') as fl:
            data = fl.read()
            size = len(data)
            print size
        # TODO: different names for different OS
        temp = os.path.abspath(__file__)
        temp = os.path.realpath(temp)
        temp = os.path.dirname(temp) + '/libs/'
        os.chdir(temp)
        self.libtoxcore = CDLL(temp + 'libtoxcore.so')
        print self.libtoxcore.__dict__
        self.libtoxcore.tox_options_new.restype = POINTER(ToxOptions)
        # TODO: load from settings
        self.tox_options = self.libtoxcore.tox_options_new(0)
        self.tox_options.contents.savedata_length = size
        self.tox_options.contents.savedata_data = c_char_p(data)
        self.libtoxcore.tox_new.restype = POINTER(c_void_p)
        self.tox = self.libtoxcore.tox_new(self.tox_options, None)  # Tox *tox
        print self.tox.contents


if __name__ == "__main__":
    t = Tox('tox_save')


