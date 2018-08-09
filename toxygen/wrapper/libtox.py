from ctypes import CDLL
import utils.util as util


class LibToxCore:

    def __init__(self):
        platform = util.get_platform()
        if platform == 'Windows':
            self._libtoxcore = CDLL(util.join_path(util.get_libs_directory(), 'libtox.dll'))
        elif platform == 'Darwin':
            self._libtoxcore = CDLL('libtoxcore.dylib')
        else:
            # libtoxcore and libsodium must be installed in your os
            try:
                self._libtoxcore = CDLL('libtoxcore.so')
            except:
                self._libtoxcore = CDLL(util.join_path(util.get_libs_directory(), 'libtoxcore.so'))

    def __getattr__(self, item):
        return self._libtoxcore.__getattr__(item)


class LibToxAV:

    def __init__(self):
        platform = util.get_platform()
        if platform == 'Windows':
            # on Windows av api is in libtox.dll
            self._libtoxav = CDLL(util.join_path(util.get_libs_directory(), 'libtox.dll'))
        elif platform == 'Darwin':
            self._libtoxav = CDLL('libtoxcore.dylib')
        else:
            # /usr/lib/libtoxcore.so must exists
            try:
                self._libtoxav = CDLL('libtoxcore.so')
            except:
                self._libtoxav = CDLL(util.join_path(util.get_libs_directory(), 'libtoxcore.so'))

    def __getattr__(self, item):
        return self._libtoxav.__getattr__(item)


class LibToxEncryptSave:

    def __init__(self):
        platform = util.get_platform()
        if platform == 'Windows':
            # on Windows profile encryption api is in libtox.dll
            self._lib_tox_encrypt_save = CDLL(util.join_path(util.get_libs_directory(), 'libtox.dll'))
        elif platform == 'Darwin':
            self._lib_tox_encrypt_save = CDLL('libtoxcore.dylib')
        else:
            # /usr/lib/libtoxcore.so must exists
            try:
                self._lib_tox_encrypt_save = CDLL('libtoxcore.so')
            except:
                self._lib_tox_encrypt_save = CDLL(util.join_path(util.get_libs_directory(), 'libtoxcore.so'))

    def __getattr__(self, item):
        return self._lib_tox_encrypt_save.__getattr__(item)
