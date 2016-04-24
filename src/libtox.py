from platform import system
from ctypes import CDLL


class LibToxCore(object):

    def __init__(self):
        if system() == 'Linux':
            # be sure that libtoxcore and libsodium are installed in your os
            self._libtoxcore = CDLL('libtoxcore.so')
        elif system() == 'Windows':
            self._libtoxcore = CDLL('libs/libtox.dll')
        else:
            raise OSError('Unknown system.')

    def __getattr__(self, item):
        return self._libtoxcore.__getattr__(item)


class LibToxAV(object):

    def __init__(self):
        if system() == 'Linux':
            # be sure that /usr/lib/libtoxav.so exists
            self._libtoxav = CDLL('libtoxav.so')
        elif system() == 'Windows':
            # on Windows av api is in libtox.dll
            self._libtoxav = CDLL('libs/libtox.dll')
        else:
            raise OSError('Unknown system.')

    def __getattr__(self, item):
        return self._libtoxav.__getattr__(item)
