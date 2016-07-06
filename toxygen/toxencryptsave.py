import libtox
import util
from ctypes import c_size_t, create_string_buffer, byref, c_int, ArgumentError, c_char_p, c_bool


TOX_ERR_ENCRYPTION = {
    # The function returned successfully.
    'OK': 0,
    # Some input data, or maybe the output pointer, was null.
    'NULL': 1,
    # The crypto lib was unable to derive a key from the given passphrase, which is usually a lack of memory issue. The
    # functions accepting keys do not produce this error.
    'KEY_DERIVATION_FAILED': 2,
    # The encryption itself failed.
    'FAILED': 3
}

TOX_ERR_DECRYPTION = {
    # The function returned successfully.
    'OK': 0,
    # Some input data, or maybe the output pointer, was null.
    'NULL': 1,
    # The input data was shorter than TOX_PASS_ENCRYPTION_EXTRA_LENGTH bytes
    'INVALID_LENGTH': 2,
    # The input data is missing the magic number (i.e. wasn't created by this module, or is corrupted)
    'BAD_FORMAT': 3,
    # The crypto lib was unable to derive a key from the given passphrase, which is usually a lack of memory issue. The
    # functions accepting keys do not produce this error.
    'KEY_DERIVATION_FAILED': 4,
    # The encrypted byte array could not be decrypted. Either the data was corrupt or the password/key was incorrect.
    'FAILED': 5,
}

TOX_PASS_ENCRYPTION_EXTRA_LENGTH = 80


class ToxEncryptSave(util.Singleton):

    libtoxencryptsave = libtox.LibToxEncryptSave()

    def __init__(self):
        super().__init__()
        self._passphrase = None

    def set_password(self, passphrase):
        self._passphrase = passphrase

    def has_password(self):
        return bool(self._passphrase)

    def is_password(self, password):
        return self._passphrase == password

    def is_data_encrypted(self, data):
        func = self.libtoxencryptsave.tox_is_data_encrypted
        func.restype = c_bool
        result = func(c_char_p(bytes(data)))
        return result

    def pass_encrypt(self, data):
        """
        Encrypts the given data with the given passphrase.

        :return: output array
        """
        out = create_string_buffer(len(data) + TOX_PASS_ENCRYPTION_EXTRA_LENGTH)
        tox_err_encryption = c_int()
        self.libtoxencryptsave.tox_pass_encrypt(c_char_p(data),
                                                c_size_t(len(data)),
                                                c_char_p(bytes(self._passphrase, 'utf-8')),
                                                c_size_t(len(self._passphrase)),
                                                out,
                                                byref(tox_err_encryption))
        tox_err_encryption = tox_err_encryption.value
        if tox_err_encryption == TOX_ERR_ENCRYPTION['OK']:
            return out[:]
        elif tox_err_encryption == TOX_ERR_ENCRYPTION['NULL']:
            raise ArgumentError('Some input data, or maybe the output pointer, was null.')
        elif tox_err_encryption == TOX_ERR_ENCRYPTION['KEY_DERIVATION_FAILED']:
            raise RuntimeError('The crypto lib was unable to derive a key from the given passphrase, which is usually a'
                               ' lack of memory issue. The functions accepting keys do not produce this error.')
        elif tox_err_encryption == TOX_ERR_ENCRYPTION['FAILED']:
            raise RuntimeError('The encryption itself failed.')

    def pass_decrypt(self, data):
        """
        Decrypts the given data with the given passphrase.

        :return: output array
        """
        out = create_string_buffer(len(data) - TOX_PASS_ENCRYPTION_EXTRA_LENGTH)
        tox_err_decryption = c_int()
        self.libtoxencryptsave.tox_pass_decrypt(c_char_p(bytes(data)),
                                                c_size_t(len(data)),
                                                c_char_p(bytes(self._passphrase, 'utf-8')),
                                                c_size_t(len(self._passphrase)),
                                                out,
                                                byref(tox_err_decryption))
        tox_err_decryption = tox_err_decryption.value
        if tox_err_decryption == TOX_ERR_DECRYPTION['OK']:
            return out[:]
        elif tox_err_decryption == TOX_ERR_DECRYPTION['NULL']:
            raise ArgumentError('Some input data, or maybe the output pointer, was null.')
        elif tox_err_decryption == TOX_ERR_DECRYPTION['INVALID_LENGTH']:
            raise ArgumentError('The input data was shorter than TOX_PASS_ENCRYPTION_EXTRA_LENGTH bytes')
        elif tox_err_decryption == TOX_ERR_DECRYPTION['BAD_FORMAT']:
            raise ArgumentError('The input data is missing the magic number (i.e. wasn\'t created by this module, or is'
                                ' corrupted)')
        elif tox_err_decryption == TOX_ERR_DECRYPTION['KEY_DERIVATION_FAILED']:
            raise RuntimeError('The crypto lib was unable to derive a key from the given passphrase, which is usually a'
                               ' lack of memory issue. The functions accepting keys do not produce this error.')
        elif tox_err_decryption == TOX_ERR_DECRYPTION['FAILED']:
            raise RuntimeError('The encrypted byte array could not be decrypted. Either the data was corrupt or the '
                               'password/key was incorrect.')
