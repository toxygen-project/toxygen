import mainscreen
from settings import Settings
from PySide import QtCore, QtGui
import os
from tox import Tox
from toxcore_enums_and_consts import *
from ctypes import *
from util import curr_time, log


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

    def __init__(self, name, status_message, widget):
        self._name, self._status_message= name, status_message
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
        self._widget.status_message.setText(value)

    status_message = property(getStatusMessage, setStatusMessage)

    def getStatus(self):
        return self._status

    def setStatus(self, value):
        # TODO: status repaint
        self._status = value

    status = property(getStatus, setStatus)


class Friend(Contact):
    """
    Friend in list of friends. Can be hidden, unread messages added
    """

    def __init__(self, number, *args):
        super(Friend, self).__init__(*args)
        self._number = number
        self._new_messages = False
        self._visible = True

    def getVisibility(self):
        return self._visible

    def setVisibility(self, value):
        self._widget.setVisibility(value)
        self._visible = value

    visibility = property(getVisibility, setVisibility)

    def setMessages(self, value):
        self._new_messages = value

    messages = property(None, setMessages)

    def getNumber(self):
        return self._number

    number = property(getNumber)
    # TODO: check if setNumber needed


class Profile(Contact):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    # TODO: add unicode support in messages
    def __init__(self, tox, widgets, widget, messages_list):
        self._widget = widget
        self._messages = messages_list
        self.tox = tox
        self._name = tox.self_get_name()
        self._status_message = tox.self_get_status_message()
        self._status = None
        data = tox.self_get_friend_list()
        self.friends, num, self._active_friend = [], 0, -1
        for i in data:
            name = tox.friend_get_name(i) or tox.friend_get_public_key(i)
            status_message = tox.friend_get_status_message(i)
            self.friends.append(Friend(i, name, status_message, widgets[num]))
            num += 1
        Profile._instance = self

    @staticmethod
    def getInstance():
        return Profile._instance

    def getActive(self):
        return self._active_friend

    def setActive(self, value):
        try:
            visible_friends = filter(lambda num, friend: friend.visibility, enumerate(self.friends))
            self._active_friend = visible_friends[value][0]
            self._messages.clear()
            # TODO: load history
        except:  # no friend found. ignore
            log('Incorrect friend value: ' + str(value))

    active_friend = property(getActive, setActive)

    def getActiveFriendData(self):
        friend = self.friends[self._active_friend]
        return friend.name, friend.status_message

    def getActiveNumber(self):
        return self.friends[self._active_friend].number

    def getActiveName(self):
        return self.friends[self._active_friend].name

    def isActiveOnline(self):
        if not self._active_friend + 1:  # no active friend
            return False
        else:
            # TODO: callbacks!
            return True
            status = self.friends[self._active_friend].status
            return status is not None

    def filtration(self, show_online=True, filter_str=''):
        for friend in self.friends:
            friend.visibility = (friend.status is not None or not show_online) and (filter_str in friend.name)

    def newMessage(self, id, message_type, message):
        if id == self._active_friend:  # add message to list
            user_name = Profile.getInstance().getActiveName()
            item = mainscreen.MessageItem(message, curr_time(), user_name, message_type)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, 100))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.scrollToBottom()
            self._messages.repaint()
        else:
            friend = filter(lambda x: x.getNumber() == id, self.friends)[0]
            friend.setMessages(True)

    def sendMessage(self, text):
        if self.isActiveOnline() and text:
            if text.startswith('/me'):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[3:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            self.tox.friend_send_message(self._active_friend, message_type, text)
            item = mainscreen.MessageItem(text, curr_time(), self._name, message_type)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, 100))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.scrollToBottom()
            self._messages.repaint()
            return True
        else:
            return False

    def changeStatus(self):
        if self._status is not None:
            self._status += 1
            self._status %= 3


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
