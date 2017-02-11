import libtox
from ctypes import c_size_t, create_string_buffer, byref, c_int, ArgumentError, c_char_p, c_bool
from toxencryptsave_enums_and_consts import *


class ToxEncryptSave:

    def __init__(self):
        self.libtoxencryptsave = libtox.LibToxEncryptSave()

    def is_data_encrypted(self, data):
        """
        Checks if given data is encrypted
        """
        func = self.libtoxencryptsave.tox_is_data_encrypted
        func.restype = c_bool
        result = func(c_char_p(bytes(data)))
        return result

    def pass_encrypt(self, data, password):
        """
        Encrypts the given data with the given password.

        :return: output array
        """
        out = create_string_buffer(len(data) + TOX_PASS_ENCRYPTION_EXTRA_LENGTH)
        tox_err_encryption = c_int()
        self.libtoxencryptsave.tox_pass_encrypt(c_char_p(data),
                                                c_size_t(len(data)),
                                                c_char_p(bytes(password, 'utf-8')),
                                                c_size_t(len(password)),
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

    def pass_decrypt(self, data, password):
        """
        Decrypts the given data with the given password.

        :return: output array
        """
        out = create_string_buffer(len(data) - TOX_PASS_ENCRYPTION_EXTRA_LENGTH)
        tox_err_decryption = c_int()
        self.libtoxencryptsave.tox_pass_decrypt(c_char_p(bytes(data)),
                                                c_size_t(len(data)),
                                                c_char_p(bytes(password, 'utf-8')),
                                                c_size_t(len(password)),
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
