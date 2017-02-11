import util
import toxencryptsave


class ToxES(util.Singleton):

    def __init__(self):
        super().__init__()
        self._toxencryptsave = toxencryptsave.ToxEncryptSave()
        self._passphrase = None

    def set_password(self, passphrase):
        self._passphrase = passphrase

    def has_password(self):
        return bool(self._passphrase)

    def is_password(self, password):
        return self._passphrase == password

    def is_data_encrypted(self, data):
        return len(data) > 0 and self._toxencryptsave.is_data_encrypted(data)

    def pass_encrypt(self, data):
        return self._toxencryptsave.pass_encrypt(data, self._passphrase)

    def pass_decrypt(self, data):
        return self._toxencryptsave.pass_decrypt(data, self._passphrase)
