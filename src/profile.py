from settings import Settings
import os
from tox import Tox
from toxcore_enums_and_consts import *
from ctypes import *


class Profile(object):

    @staticmethod
    def find_profiles():
        path = Settings.get_default_path()
        result = []
        # check default path
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        path = os.path.dirname(os.path.abspath(__file__))
        # check current directory
        for fl in os.listdir(path):
            if fl.endswith('.tox'):
                name = fl[:-4]
                result.append((path, name))
        return result

    @staticmethod
    def open_profile(path, name):
        Profile._path = path + name + '.tox'
        with open(Profile._path, 'rb') as fl:
            data = fl.read()
        if data:
            print 'Data loaded from: {}'.format(Profile._path)
            return data
        else:
            raise IOError('Save file not found. Path: {}'.format(Profile._path))

    @staticmethod
    def save_profile(data, name=None):
        if name is not None:
            Profile._path = Settings.get_default_path() + name + '.tox'
        with open(Profile._path, 'wb') as fl:
            fl.write(data)
        print 'Data saved to: {}'.format(Profile._path)


def tox_factory(data=None, settings=None):
    if settings is None:
        settings = Settings.get_default_settings()
    tox_options = Tox.options_new()
    tox_options.contents.udp_enabled = settings['udp_enabled']
    tox_options.contents.proxy_type = settings['proxy_type']
    tox_options.contents.proxy_host = settings['proxy_host']
    tox_options.contents.proxy_port = settings['proxy_port']
    tox_options.contents.start_port = settings['start_port']
    tox_options.contents.end_port = settings['end_port']
    tox_options.contents.tcp_port = settings['tcp_port']
    if data:  # load existing profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['TOX_SAVE']
        tox_options.contents.savedata_data = c_char_p(data)
        tox_options.contents.savedata_length = len(data)
    else: # create new profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['NONE']
        tox_options.contents.savedata_data = None
        tox_options.contents.savedata_length = 0
    return Tox(tox_options)
