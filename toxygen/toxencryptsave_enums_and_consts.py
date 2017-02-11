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
