from list_items import MessageItem, ContactItem
from settings import Settings
from PySide import QtCore, QtGui
import os
from tox import Tox
from toxcore_enums_and_consts import *
from ctypes import *
from util import curr_time, log, Singleton, curr_directory


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
    widget - widget for update
    """

    def __init__(self, name, status_message, widget, tox_id):
        """
        :param name: name, example: 'Toxygen user'
        :param status_message: status message, example: 'Toxing on toxygen'
        :param widget: ContactItem instance
        :param tox_id: tox id of contact
        """
        self._name, self._status_message = name, status_message
        self._status, self._widget = None, widget
        widget.name.setText(name)
        widget.status_message.setText(status_message)
        self._tox_id = tox_id
        self.load_avatar()

    # -----------------------------------------------------------------------------------------------------------------
    # name - current name or alias of user
    # -----------------------------------------------------------------------------------------------------------------

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value.decode('utf-8')
        self._widget.name.setText(self._name)
        self._widget.name.repaint()

    name = property(get_name, set_name)

    # -----------------------------------------------------------------------------------------------------------------
    # Status message
    # -----------------------------------------------------------------------------------------------------------------

    def get_status_message(self):
        return self._status_message

    def set_status_message(self, value):
        self._status_message = value.decode('utf-8')
        self._widget.status_message.setText(self._status_message)
        self._widget.status_message.repaint()

    status_message = property(get_status_message, set_status_message)

    # -----------------------------------------------------------------------------------------------------------------
    # Status
    # -----------------------------------------------------------------------------------------------------------------

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._widget.connection_status.data = self._status = value
        self._widget.connection_status.repaint()

    status = property(get_status, set_status)

    # -----------------------------------------------------------------------------------------------------------------
    # TOX ID. WARNING: for friend it will return public key, for profile - full address
    # -----------------------------------------------------------------------------------------------------------------

    def get_tox_id(self):
        return self._tox_id

    tox_id = property(get_tox_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars
    # -----------------------------------------------------------------------------------------------------------------

    def load_avatar(self):
        """
        Tries to load avatar of contact or uses default avatar
        """
        avatar_path = (Settings.get_default_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        if not os.path.isfile(avatar_path):  # load default image
            avatar_path = curr_directory() + '/images/avatar.png'
        pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
        pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
        self._widget.avatar_label.setPixmap(avatar_path)
        self._widget.avatar_label.repaint()


class Friend(Contact):
    """
    Friend in list of friends. Can be hidden, properties 'has unread messages' and 'has alias' added
    """

    def __init__(self, number, *args):
        """
        :param number: number of friend.
        """
        super(Friend, self).__init__(*args)
        self._number = number
        self._new_messages = False
        self._visible = True
        self._alias = False

    def __del__(self):
        self.set_visibility(False)
        del self._widget

    # -----------------------------------------------------------------------------------------------------------------
    # Alias support
    # -----------------------------------------------------------------------------------------------------------------

    def set_name(self, value):
        if not self._alias:
            super(self.__class__, self).set_name(value)

    def set_alias(self, alias):
        self._alias = bool(alias)

    # -----------------------------------------------------------------------------------------------------------------
    # Visibility in friends' list
    # -----------------------------------------------------------------------------------------------------------------

    def get_visibility(self):
        return self._visible

    def set_visibility(self, value):
        self._visible = value

    visibility = property(get_visibility, set_visibility)

    # -----------------------------------------------------------------------------------------------------------------
    # Unread messages from friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_messages(self):
        return self._new_messages

    def set_messages(self, value):
        self._widget.connection_status.messages = self._new_messages = value
        self._widget.connection_status.repaint()

    messages = property(get_messages, set_messages)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend's number (can be used in toxcore)
    # -----------------------------------------------------------------------------------------------------------------

    def get_number(self):
        return self._number

    def set_number(self, value):
        self._number = value

    number = property(get_number, set_number)


class Profile(Contact, Singleton):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    def __init__(self, tox, screen):
        """
        :param tox: tox instance
        :param screen: ref to main screen
        """
        self.screen = screen
        self._widget = screen.user_info
        self._messages = screen.messages
        self.tox = tox
        self._name = tox.self_get_name()
        self._status_message = tox.self_get_status_message()
        self._status = None
        settings = Settings.get_instance()
        self.show_online = settings['show_online_friends']
        screen.online_contacts.setChecked(self.show_online)
        aliases = settings['friends_aliases']
        data = tox.self_get_friend_list()
        self._friends, self._active_friend = [], -1
        for i in data:  # creates list of friends
            tox_id = tox.friend_get_public_key(i)
            try:
                alias = filter(lambda x: x[0] == tox_id, aliases)[0][1]
            except:
                alias = ''
            item = self.create_friend_item()
            name = alias or tox.friend_get_name(i) or tox_id
            status_message = tox.friend_get_status_message(i)
            friend = Friend(i, name, status_message, item, tox_id)
            friend.set_alias(alias)
            self._friends.append(friend)
        self.set_name(tox.self_get_name().encode('utf-8'))
        self.set_status_message(tox.self_get_status_message().encode('utf-8'))
        self.filtration(self.show_online)
        self._tox_id = tox.self_get_address()
        self.load_avatar()

    # -----------------------------------------------------------------------------------------------------------------
    # Edit current user's data
    # -----------------------------------------------------------------------------------------------------------------

    def change_status(self):
        """
        Changes status of user (online, away, busy)
        """
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

    # -----------------------------------------------------------------------------------------------------------------
    # Filtration
    # -----------------------------------------------------------------------------------------------------------------

    def filtration(self, show_online=True, filter_str=''):
        """
        Filtration of friends list
        :param show_online: show online only contacts
        :param filter_str: show contacts which name contains this substring
        """
        filter_str = filter_str.lower()
        for index, friend in enumerate(self._friends):
            friend.visibility = (friend.status is not None or not show_online) and (filter_str in friend.name.lower())
            if friend.visibility:
                self.screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 70))
            else:
                self.screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 0))
        self.show_online, self.filter_string = show_online, filter_str
        settings = Settings.get_instance()
        settings['show_online_friends'] = self.show_online
        settings.save()

    def update_filtration(self):
        """
        Update list of contacts when 1 of friends change connection status
        """
        self.filtration(self.show_online, self.filter_string)

    def get_friend_by_number(self, num):
        return filter(lambda x: x.number == num, self._friends)[0]

    # -----------------------------------------------------------------------------------------------------------------
    # Work with active friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_active(self):
        return self._active_friend

    def set_active(self, value=None):
        """
        :param value: number of new active friend in friend's list or None to update active user's data
        """
        if value is None and self._active_friend == -1:  # nothing to update
            return
        try:
            if value is not None:
                self._active_friend = value
                self._friends[self._active_friend].set_messages(False)
                self.screen.messages.clear()
                self.screen.messageEdit.clear()
            friend = self._friends[self._active_friend]
            self.screen.account_name.setText(friend.name)
            self.screen.account_status.setText(friend.status_message)
            avatar_path = (Settings.get_default_path() + 'avatars/{}.png').format(friend.tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
            if not os.path.isfile(avatar_path):  # load default image
                avatar_path = curr_directory() + '/images/avatar.png'
            pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
            pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio)
            self.screen.account_avatar.setPixmap(avatar_path)
            self.screen.account_avatar.repaint()
            # TODO: load history
        except:  # no friend found. ignore
            log('Incorrect friend value: ' + str(value))

    active_friend = property(get_active, set_active)

    def get_active_number(self):
        return self._friends[self._active_friend].number

    def get_active_name(self):
        return self._friends[self._active_friend].name

    def is_active_online(self):
        return self._active_friend + 1 and self._friends[self._active_friend].status is not None

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def new_message(self, friend_num, message_type, message):
        """
        Current user gets new message
        :param friend_num: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        # TODO: save message to history
        if friend_num == self.get_active_number():  # add message to list
            user_name = Profile.get_instance().get_active_name()
            item = MessageItem(message.decode('utf-8'), curr_time(), user_name, message_type, self._messages)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, item.getHeight()))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.repaint()
        else:
            friend = filter(lambda x: x.number == friend_num, self._friends)[0]
            friend.set_messages(True)

    def send_message(self, text):
        """
        Send message to active friend
        :param text: message text
        """
        # TODO: save message to history
        if self.is_active_online() and text:
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            self.tox.friend_send_message(self._active_friend, message_type, text.encode('utf-8'))
            item = MessageItem(text, curr_time(), self._name, message_type, self._messages)
            elem = QtGui.QListWidgetItem(self._messages)
            elem.setSizeHint(QtCore.QSize(500, item.getHeight()))
            self._messages.addItem(elem)
            self._messages.setItemWidget(elem, item)
            self._messages.scrollToBottom()
            self._messages.repaint()
            self.screen.messageEdit.clear()

    # -----------------------------------------------------------------------------------------------------------------
    # Work with friends (add, remove)
    # -----------------------------------------------------------------------------------------------------------------

    def create_friend_item(self):
        """
        Method-factory
        :return: new widget for friend instance
        """
        item = ContactItem()
        elem = QtGui.QListWidgetItem(self.screen.friends_list)
        elem.setSizeHint(QtCore.QSize(250, 70))
        self.screen.friends_list.addItem(elem)
        self.screen.friends_list.setItemWidget(elem, item)
        return item

    def send_friend_request(self, tox_id, message):
        """
        Function tries to send request to contact with specified id
        :param tox_id: id of new contact
        :param message: additional message
        :return: True on success else error string
        """
        try:
            message = message or 'Add me to your contact list'
            result = self.tox.friend_add(tox_id, message.encode('utf-8'))
            tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
            item = self.create_friend_item()
            friend = Friend(result, tox_id, '', item, tox_id)
            self._friends.append(friend)
            return True
        except Exception as ex:  # wrong data
            log('Send friend failed with ' + str(ex))
            return str(ex)

    def process_friend_request(self, tox_id, message):
        """
        Accept or ignore friend request
        :param tox_id: tox id of contact
        :param message: message
        """
        try:
            info = 'User {} wants to add you to contact list. Message:\n{}'.format(tox_id, message)
            reply = QtGui.QMessageBox.question(None, 'Friend request', info, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:  # accepted
                num = self.tox.friend_add_norequest(tox_id)  # num - friend number
                item = self.create_friend_item()
                friend = Friend(num, tox_id, '', item, tox_id)
                self._friends.append(friend)
        except Exception as ex:  # something is wrong
            log('Accept friend request failed! ' + str(ex))

    def delete_friend(self, num):
        """
        Removes friend from contact list
        :param num: number of friend
        """
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
