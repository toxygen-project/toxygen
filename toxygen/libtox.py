from platform import system
from ctypes import CDLL
import util


class LibToxCore:

    def __init__(self):
        if system() == 'Linux':
            # libtoxcore and libsodium must be installed in your os
            self._libtoxcore = CDLL('libtoxcore.so')
        elif system() == 'Windows':
            self._libtoxcore = CDLL(util.curr_directory() + '/libs/libtox.dll')
        else:
            raise OSError('Unknown system.')

    def __getattr__(self, item):
        return self._libtoxcore.__getattr__(item)


class LibToxAV:

    def __init__(self):
        if system() == 'Linux':
            # that /usr/lib/libtoxav.so must exists
            self._libtoxav = CDLL('libtoxav.so')
        elif system() == 'Windows':
            # on Windows av api is in libtox.dll
            self._libtoxav = CDLL(util.curr_directory() + '/libs/libtox.dll')
        else:
            raise OSError('Unknown system.')

    def __getattr__(self, item):
        return self._libtoxav.__getattr__(item)


class LibToxEncryptSave:

    def __init__(self):
        if system() == 'Linux':
            # /usr/lib/libtoxencryptsave.so must exists
            self._lib_tox_encrypt_save = CDLL('libtoxencryptsave.so')
        elif system() == 'Windows':
            # on Windows profile encryption api is in libtox.dll
            self._lib_tox_encrypt_save = CDLL(util.curr_directory() + '/libs/libtox.dll')
        else:
            raise OSError('Unknown system.')

    def __getattr__(self, item):
        return self._lib_tox_encrypt_save.__getattr__(item)
