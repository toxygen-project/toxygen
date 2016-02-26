from settings import Settings
import os
from tox import Tox
from util import Singleton
from toxcore_enums_and_consts import *
from ctypes import *


class ProfileHelper(object):
    """
    Class with static methods for search, load and save profiles
    """
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
        ProfileHelper._path = path + name + '.tox'
        with open(ProfileHelper._path, 'rb') as fl:
            data = fl.read()
        if data:
            print 'Data loaded from: {}'.format(ProfileHelper._path)
            return data
        else:
            raise IOError('Save file not found. Path: {}'.format(ProfileHelper._path))

    @staticmethod
    def save_profile(data, name=None):
        if name is not None:
            ProfileHelper._path = Settings.get_default_path() + name + '.tox'
        with open(ProfileHelper._path, 'wb') as fl:
            fl.write(data)
        print 'Data saved to: {}'.format(ProfileHelper._path)


class Contact(object):
    """
    Class encapsulating TOX contact
    Properties: name (alias of contact or name), status_message, status (connection status)
    number - unique number of friend in list, widget - widget for update
    """

    def __init__(self, name, status_message, number, widget):
        # TODO: remove number
        self._name, self._status_message, self._number = name, status_message, number
        self._status, self._widget = None, widget
        widget.name.setText(name)
        widget.status_message.setText(status_message)

    def getName(self):
        return self._name

    def setName(self, value):
        self._name = value
        self._widget.name.setText(value)

    name = property(getName, setName)

    def getStatusMessage(self):
        return self._status_message

    def setStatusMessage(self, value):
        self._status_message = value
        self._widget.status.setText(value)

    status_message = property(getStatusMessage, setStatusMessage)

    def getStatus(self):
        return self._status

    def setStatus(self, value):
        self._status = value

    status = property(getStatus, setStatus)


class Friend(Contact):
    """
    Friend in list of friends. Can be hidden, unread messages added
    """

    def __init__(self, *args):
        super(Friend, self).__init__(*args)
        self._new_messages = False

    def setVisibility(self, value):
        self._widget.setVisibility(value)

    def setMessages(self, value):
        self._new_messages = value

    messages = property(None, setMessages)

    def getNumber(self):
        return self._number

    number = property(getNumber)


class Profile(Contact, Singleton):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    # TODO: add slices
    def __init__(self, tox, widgets, widget):
        self._widget = widget
        self.tox = tox
        data = tox.self_get_friend_list()
        self.friends, num, self._active_friend = [], 0, -1
        for i in data:
            name = tox.friend_get_name(i) or 'Tox user'  # tox.friend_get_public_key(i)
            status_message = tox.friend_get_status_message(i)
            self.friends.append(Friend(name, status_message, i, widgets[num]))
            num += 1

    def getActive(self):
        return self._active_friend

    def setActive(self, value):
        if 0 <= value < self.tox.self_get_friend_list_size():
            self._active_friend = value

    active_friend = property(getActive, setActive)

    def getActiveNumber(self):
        return self.friends[self._active_friend].getNumber()

    def isActiveOnline(self):
        if not self._active_friend + 1:  # no active friend
            return False
        else:
            # TODO: callbacks!
            return True
            status = self.friends[self._active_friend].getStatus()
            return status is not None


def tox_factory(data=None, settings=None):
    """
    :param data: user data from .tox file. None = no saved data, create new profile
    :param settings: current application settings. None = defaults settings will be used
    :return: new tox instance
    """
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
    else:  # create new profile
        tox_options.contents.savedata_type = TOX_SAVEDATA_TYPE['NONE']
        tox_options.contents.savedata_data = None
        tox_options.contents.savedata_length = 0
    return Tox(tox_options)
