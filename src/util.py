import os

program_version = '0.0.1 (alpha)'


def log(data):
    with open('logs.log', 'a') as fl:
        fl.write(str(data))


def string_to_bin(tox_id):
    return tox_id.decode('hex')


def bin_to_string(raw_id):
    res = ''.join('{:02x}'.format(ord(x)) for x in raw_id)
    return res.upper()


def curr_directory():
    return os.path.dirname(os.path.realpath(__file__))
