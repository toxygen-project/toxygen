
class ToxES:

    def __init__(self, tox_encrypt_save):
        self._tox_encrypt_save = tox_encrypt_save
        self._password = None

    def set_password(self, password):
        self._password = password

    def has_password(self):
        return bool(self._password)

    def is_password(self, password):
        return self._password == password

    def is_data_encrypted(self, data):
        return len(data) > 0 and self._tox_encrypt_save.is_data_encrypted(data)

    def pass_encrypt(self, data):
        return self._tox_encrypt_save.pass_encrypt(data, self._password)

    def pass_decrypt(self, data):
        return self._tox_encrypt_save.pass_decrypt(data, self._password)
