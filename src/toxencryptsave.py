import libtox
import util


# TODO: add enums and methods

class LibToxEncryptSave(util.Singleton):

    libtoxencryptsave = libtox.LibToxEncryptSave()

    def __init__(self, password=''):
        self._password = password

    def set_password(self, value):
        self._password = value
