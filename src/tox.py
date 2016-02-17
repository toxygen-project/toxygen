# -*- coding: utf-8 -*-
from ctypes import *
from settings import Settings
from platform import system
from toxcore_enums import *
import os


class ToxOptions(Structure):
    _fields_ = [
        ('ipv6_enabled', c_bool),
        ('udp_enabled', c_bool),
        ('proxy_type', c_int),
        ('proxy_host', c_char_p),
        ('proxy_port', c_uint16),
        ('start_port', c_uint16),
        ('end_port', c_uint16),
        ('tcp_port', c_uint16),
        ('savedata_type', c_int),
        ('savedata_data', c_char_p),
        ('savedata_length', c_size_t)
        ]


class Tox(object):

    def __init__(self, name, path=None):
        # load toxcore
        if system() == 'Linux':
            temp = os.path.dirname(os.path.abspath(__file__)) + '/libs/'
            os.chdir(temp)
            self.libtoxcore = CDLL(temp + 'libtoxcore.so')
        elif system() == 'Windows':
            self.libtoxcore = CDLL('libs/libtox.dll')
        self.libtoxcore.tox_options_new.restype = POINTER(ToxOptions)

        # load saved data
        if path is None:
            path = Settings.get_default_path()
        full_path = path + name + '.tox'
        with open(full_path, 'rb') as fl:
            savedata = fl.read()
        settings = Settings()

        # creating tox options struct
        tox_err = c_int()
        self.tox_options = self.libtoxcore.tox_options_new(addressof(tox_err))
        if tox_err == TOX_ERR_OPTIONS_NEW['TOX_ERR_OPTIONS_NEW_MALLOC']:
            raise MemoryError('The function failed to allocate enough memory for the options struct.')

        # filling tox options struct
        self.tox_options.contents.ipv6_enabled = settings['ipv6_enabled']
        self.tox_options.contents.udp_enabled = settings['udp_enabled']
        self.tox_options.contents.proxy_type = settings['proxy_type']
        self.tox_options.contents.proxy_host = settings['proxy_host']
        self.tox_options.contents.proxy_port = settings['proxy_port']
        self.tox_options.contents.start_port = settings['start_port']
        self.tox_options.contents.end_port = settings['end_port']
        self.tox_options.contents.tcp_port = settings['tcp_port']
        self.tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['TOX_SAVEDATA_TYPE_TOX_SAVE']
        self.tox_options.contents.savedata_data = c_char_p(savedata)
        self.tox_options.contents.savedata_length = len(savedata)

        # creating tox object
        self.libtoxcore.tox_new.restype = POINTER(c_void_p)
        self.tox_pointer = self.libtoxcore.tox_new(self.tox_options, None)


if __name__ == '__main__':
    t = Tox('tox_save')
