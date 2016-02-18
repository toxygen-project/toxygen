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
        else:
            raise OSError('Unknown system.')

        # load saved data
        if path is None:
            path = Settings.get_default_path()
        full_path = path + name + '.tox'
        with open(full_path, 'rb') as fl:
            savedata = fl.read()
        settings = Settings()

        # creating tox options struct
        tox_err_options = c_int()
        self.libtoxcore.tox_options_new.restype = POINTER(ToxOptions)
        self.tox_options = self.libtoxcore.tox_options_new(addressof(tox_err_options))
        if tox_err_options == TOX_ERR_OPTIONS_NEW['TOX_ERR_OPTIONS_NEW_MALLOC']:
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
        tox_err = c_int()
        self.libtoxcore.tox_new.restype = POINTER(c_void_p)
        self._tox_pointer = self.libtoxcore.tox_new(self.tox_options, addressof(tox_err))
        if tox_err == TOX_ERR_NEW['TOX_ERR_NEW_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_MALLOC']:
            raise MemoryError('The function was unable to allocate enough '
                              'memory to store the internal structures for the Tox object.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_PORT_ALLOC']:
            raise MemoryError('The function was unable to bind to a port. This may mean that all ports have already'
                              ' been bound, e.g. by other Tox instances, or it may mean a permission error. You may'
                              ' be able to gather more information from errno.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_TYPE']:
            raise ArgumentError('proxy_type was invalid.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_HOST']:
            raise ArgumentError('proxy_type was valid but the proxy_host passed had an invalid format or was NULL.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_BAD_PORT']:
            raise ArgumentError('proxy_type was valid, but the proxy_port was invalid.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_PROXY_NOT_FOUND']:
            raise ArgumentError('The proxy address passed could not be resolved.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_LOAD_ENCRYPTED']:
            raise ArgumentError('The byte array to be loaded contained an encrypted save.')
        elif tox_err == TOX_ERR_NEW['TOX_ERR_NEW_LOAD_BAD_FORMAT']:
            raise ArgumentError('The data format was invalid. This can happen when loading data that was saved by an'
                                ' older version of Tox, or when the data has been corrupted. When loading from badly'
                                ' formatted data, some data may have been loaded, and the rest is discarded. Passing'
                                ' an invalid length parameter also causes this error.')

    def get_savedata_size(self):
        return self.libtoxcore.tox_get_savedata_size(self._tox_pointer)

    def get_savedata(self, savedata=None):
        if savedata is None:
            savedata_size = self.get_savedata_size()
            savedata = create_string_buffer(savedata_size)
        self.libtoxcore.tox_get_savedata(self._tox_pointer, savedata)
        return savedata

    def bootstrap(self, address, port, public_key):
        tox_err_bootstrap = c_int()
        result = self.libtoxcore.tox_bootstrap(self._tox_pointer, c_char_p(address), c_uint16(port),
                                               c_char_p(public_key), addressof(tox_err_bootstrap))
        if tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_OK']:
            return bool(result)
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_HOST']:
            raise ArgumentError('The address could not be resolved to an IP '
                                'address, or the IP address passed was invalid.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_PORT']:
            raise ArgumentError('The port passed was invalid. The valid port range is (1, 65535).')

    def add_tcp_relay(self, address, port, public_key):
        tox_err_bootstrap = c_int()
        result = self.libtoxcore.tox_add_tcp_relay(self._tox_pointer, c_char_p(address), c_uint16(port),
                                                   c_char_p(public_key), addressof(tox_err_bootstrap))
        if tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_OK']:
            return bool(result)
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_NULL']:
            raise ArgumentError('One of the arguments to the function was NULL when it was not expected.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_HOST']:
            raise ArgumentError('The address could not be resolved to an IP '
                                'address, or the IP address passed was invalid.')
        elif tox_err_bootstrap == TOX_ERR_BOOTSTRAP['TOX_ERR_BOOTSTRAP_BAD_PORT']:
            raise ArgumentError('The port passed was invalid. The valid port range is (1, 65535).')

    def self_get_connection_status(self):
        return self.libtoxcore.tox_self_get_connection_status(self._tox_pointer)

    def callback_self_connection_status(self, callback, user_data):
        tox_self_connection_status_cb = CFUNCTYPE(None, c_void_p, c_int, c_void_p)
        c_callback = tox_self_connection_status_cb(callback)
        self.libtoxcore.tox_callback_self_connection_status(self._tox_pointer, c_callback, c_void_p(user_data))

    def __del__(self):
        self.libtoxcore.tox_kill(self._tox_pointer)
        self.libtoxcore.tox_options_free(self.tox_options)


if __name__ == '__main__':
    t = Tox('tox_save')
