from ctypes import *
from settings import Settings


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
        ("savedata_data", POINTER(c_uint8)),
        ("savedata_length", c_size_t)
        ]


class Tox(object):

    def __init__(self, name):
        path = Settings.get_default_path() + name + '.tox'
        with open(path, 'rb') as fl:
            data = fl.read()
            size = len(data)
            print size
        libtoxcore = CDLL('libtoxcore.so')
        libtoxcore.tox_options_new.restype = POINTER(ToxOptions)
        self.tox_options = libtoxcore.tox_options_new(0)
        libtoxcore.tox_new.restype = POINTER(c_void_p)
        tox = libtoxcore.tox_new(None, None)
        self.libtoxcore = libtoxcore

if __name__ == "__main__":
    t = Tox('tox_save')


