from platform import system
from ctypes import CDLL
import util


class LibToxCore:

    def __init__(self):
        if system() == 'Windows':
            self._libtoxcore = CDLL(util.curr_directory() + '/libs/libtox.dll')
        elif system() == 'Darwin':
            self._libtoxcore = CDLL('libtoxcore.dylib')
        else:
            # libtoxcore and libsodium must be installed in your os
            try:
                self._libtoxcore = CDLL('libtoxcore.so')
            except:
                self._libtoxcore = CDLL(util.curr_directory() + '/libs/libtoxcore.so')

    def __getattr__(self, item):
        return self._libtoxcore.__getattr__(item)


class LibToxAV:

    def __init__(self):
        if system() == 'Windows':
            # on Windows av api is in libtox.dll
            self._libtoxav = CDLL(util.curr_directory() + '/libs/libtox.dll')
        elif system() == 'Darwin':
            self._libtoxav = CDLL('libtoxav.dylib')
        else:
            # /usr/lib/libtoxav.so must exists
            try:
                self._libtoxav = CDLL('libtoxav.so')
            except:
                self._libtoxav = CDLL(util.curr_directory() + '/libs/libtoxav.so')

    def __getattr__(self, item):
        return self._libtoxav.__getattr__(item)


class LibToxEncryptSave:

    def __init__(self):
        if system() == 'Windows':
            # on Windows profile encryption api is in libtox.dll
            self._lib_tox_encrypt_save = CDLL(util.curr_directory() + '/libs/libtox.dll')
        elif system() == 'Darwin':
            self._lib_tox_encrypt_save = CDLL('libtoxencryptsave.dylib')
        else:
            # /usr/lib/libtoxencryptsave.so must exists
            try:
                self._lib_tox_encrypt_save = CDLL('libtoxencryptsave.so')
            except:
                self._lib_tox_encrypt_save = CDLL(util.curr_directory() + '/libs/libtoxencryptsave.so')

    def __getattr__(self, item):
        return self._lib_tox_encrypt_save.__getattr__(item)
