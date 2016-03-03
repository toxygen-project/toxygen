from list_items import MessageItem
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
        self._name, self._status_message = name, status_message
        self._status, self._widget = None, widget
        widget.name.setText(name)
        widget.status_message.setText(status_message)

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value.decode('utf-8')
        self._widget.name.setText(self._name)
        self._widget.name.repaint()

    name = property(get_name, set_name)

    def get_status_message(self):
        return self._status_message

    def set_status_message(self, value):
        self._status_message = value.decode('utf-8')
        self._widget.status_message.setText(self._status_message)
        self._widget.status_message.repaint()

    status_message = property(get_status_message, set_status_message)

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._widget.connection_status.data = self._status = value
        self._widget.connection_status.repaint()

    status = property(get_status, set_status)


class Friend(Contact):
    """
    Friend in list of friends. Can be hidden, property 'has unread messages' added
    """

    def __init__(self, number, *args):
        super(Friend, self).__init__(*args)
        self._number = number
        self._new_messages = False
        self._visible = True

    def get_visibility(self):
        return self._visible

    def set_visibility(self, value):
        self._visible = value
        self._widget.setVisible(value)

    visibility = property(get_visibility, set_visibility)

    def get_messages(self):
        return self._new_messages

    def set_messages(self, value):
        self._new_messages = value

    messages = property(get_messages, set_messages)

    def get_number(self):
        return self._number

    number = property(get_number)
    # TODO: check if setNumber needed

    def __del__(self):
        del self._widget


class Profile(Contact):
    """
    Profile of current toxygen user. Contains friends list, tox instance, list of messages
    """
    def __init__(self, tox, widgets, widget, messages_list):
        self._widget = widget
        self._messages = messages_list
        self.tox = tox
        self._name = tox.self_get_name()
        self._status_message = tox.self_get_status_message()
        self._status = None
        self.show_online = Settings.get_instance()['show_online_friends']
        data = tox.self_get_friend_list()
        self._friends, num, self._active_friend = [], 0, -1
        for i in data:
            name = tox.friend_get_name(i) or tox.friend_get_public_key(i)
            status_message = tox.friend_get_status_message(i)
            self._friends.append(Friend(i, name, status_message, widgets[num]))
            num += 1
        Profile._instance = self
        self.set_name(tox.self_get_name().encode('utf-8'))
        self.set_status_message(tox.self_get_status_message().encode('utf-8'))
        self.filtration(self.show_online)

    @staticmethod
    def get_instance():
        return Profile._instance

    def change_status(self):
        if self._status is not None:
            status = (self._status + 1) % 3
            super(self.__class__, self).set_status(status)
            self.tox.self_set_status(status)

    def set_name(self, value):
        super(self.__class__, self).set_name(value)
        self.tox.self_set_name(self._name.encode('utf-8'))

    def set_status_message(self, value):
        super(self.__class__, self).set_status_message(value)
        self.tox.self_set_status_message(self._status_message.encode('utf-8'))

    def filtration(self, show_online=True, filter_str=''):
        # TODO: hide elements in list
        filter_str = filter_str.lower()
        for friend in self._friends:
            friend.visibility = (friend.status is not None or not show_online) and (filter_str in friend.name.lower())
        self.show_online, self.filter_string = show_online, filter_str

    def get_friend_by_number(self, num):
        return filter(lambda x: x.number == num, self._friends)[0]

    # -----------------------------------------------------------------------------------------------------------------
    # Work with active friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_active(self):
        return self._active_friend

    def set_active(self, value):
        try:
            visible_friends = filter(lambda elem: elem[1].visibility, enumerate(self._friends))
            self._active_friend = visible_friends[value][0]
            self._messages.clear()
            self._messages.repaint()
            # TODO: load history
        except:  # no friend found. ignore
            log('Incorrect friend value: ' + str(value))

    active_friend = property(get_active, set_active)

    def get_active_friend_data(self):
        if self._active_friend != -1:
            friend = self._friends[self._active_friend]
            return friend.name, friend.status_message
        else:
            log('Something is wrong in get_active_friend_data')
            return '', ''

    def get_active_number(self):
        return self._friends[self._active_friend].number

    def get_active_name(self):
        return self._friends[self._active_friend].name

    def is_active_online(self):
        return self._active_friend + 1 and self._friends[self._active_friend].status is not None

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def new_message(self, id, message_type, message):
        if id == self._active_friend:  # add message to list
            user_name = Profile.get_instance().get_active_name()
            item = MessageItem(message.decode('utf-8'), curr_time(), user_name, message_type)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, 100))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.scrollToBottom()
            self._messages.repaint()
        else:
            friend = filter(lambda x: x.number == id, self._friends)[0]
            friend.set_messages(True)

    def send_message(self, text):
        if self.is_active_online() and text:
            if text.startswith('/me'):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[3:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            self.tox.friend_send_message(self._active_friend, message_type, text.encode('utf-8'))
            item = MessageItem(text, curr_time(), self._name, message_type)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, 100))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.scrollToBottom()
            self._messages.repaint()
            return True
        else:
            return False

    # -----------------------------------------------------------------------------------------------------------------
    # Work with friends (add, remove)
    # -----------------------------------------------------------------------------------------------------------------

    def delete_friend(self, num):
        self.tox.friend_delete(num)
        friend = filter(lambda x: x.number == num, self._friends)[0]
        del friend


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
