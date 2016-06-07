from list_items import MessageItem, ContactItem, FileTransferItem, InlineImageItem
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from tox import Tox
import os
from messages import *
from settings import *
from toxcore_enums_and_consts import *
from ctypes import *
from util import curr_time, log, Singleton, curr_directory, convert_time
from tox_dns import tox_dns
from history import *
from file_transfers import *
import time
import calls
import avwidgets
import plugin_support


class Contact(object):
    """
    Class encapsulating TOX contact
    Properties: name (alias of contact or name), status_message, status (connection status)
    widget - widget for update
    """

    def __init__(self, name, status_message, widget, tox_id):
        """
        :param name: name, example: 'Toxygen user'
        :param status_message: status message, example: 'Toxing on Toxygen'
        :param widget: ContactItem instance
        :param tox_id: tox id of contact
        """
        self._name, self._status_message = name, status_message
        self._status, self._widget = None, widget
        self._widget.name.setText(name)
        self._widget.status_message.setText(status_message)
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
        avatar_path = '{}.png'.format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        os.chdir(ProfileHelper.get_path() + 'avatars/')
        if not os.path.isfile(avatar_path):  # load default image
            avatar_path = 'avatar.png'
            os.chdir(curr_directory() + '/images/')
        pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
        pixmap.load(avatar_path)
        self._widget.avatar_label.setScaledContents(False)
        self._widget.avatar_label.setPixmap(pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))
        self._widget.avatar_label.repaint()

    def reset_avatar(self):
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        if os.path.isfile(avatar_path):
            os.remove(avatar_path)
            self.load_avatar()

    def set_avatar(self, avatar):
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        with open(avatar_path, 'wb') as f:
            f.write(avatar)
        self.load_avatar()

    def get_pixmap(self):
        return self._widget.avatar_label.pixmap()


class Friend(Contact):
    """
    Friend in list of friends. Can be hidden, properties 'has unread messages' and 'has alias' added
    """

    def __init__(self, message_getter, number, *args):
        """
        :param message_getter: gets messages from db
        :param number: number of friend.
        """
        super(Friend, self).__init__(*args)
        self._number = number
        self._new_messages = False
        self._visible = True
        self._alias = False
        self._message_getter = message_getter
        self._corr = []
        self._unsaved_messages = 0
        self._history_loaded = False
        self._receipts = 0

    def __del__(self):
        self.set_visibility(False)
        del self._widget
        if hasattr(self, '_message_getter'):
            del self._message_getter

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def get_receipts(self):
        return self._receipts

    receipts = property(get_receipts)

    def inc_receipts(self):
        self._receipts += 1

    def dec_receipt(self):
        if self._receipts:
            self._receipts -= 1
            self.mark_as_sent()

    def load_corr(self, first_time=True):
        """
        :param first_time: friend became active, load first part of messages
        """
        if (first_time and self._history_loaded) or (not hasattr(self, '_message_getter')):
            return
        data = self._message_getter.get(PAGE_SIZE)
        if data is not None and len(data):
            data.reverse()
        else:
            return
        data = map(lambda tupl: TextMessage(*tupl), data)
        self._corr = data + self._corr
        self._history_loaded = True

    def get_corr_for_saving(self):
        """
        Get data to save in db
        :return: list of unsaved messages or []
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        messages = filter(lambda x: x.get_type() <= 1, self._corr)
        return map(lambda x: x.get_data(), messages[-self._unsaved_messages:]) if self._unsaved_messages else []

    def get_corr(self):
        return self._corr[:]

    def append_message(self, message):
        """
        :param message: text or file transfer message
        """
        self._corr.append(message)
        if message.get_type() <= 1:
            self._unsaved_messages += 1

    def get_last_message_text(self):
        messages = filter(lambda x: x.get_type() <= 1 and x.get_owner() != MESSAGE_OWNER['FRIEND'], self._corr)
        if messages:
            return messages[-1].get_data()[0]
        else:
            return ''

    def unsent_messages(self):
        """
        :return list of unsent messages
        """
        messages = filter(lambda x: x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr)
        return messages

    def mark_as_sent(self):
        try:
            message = filter(lambda x: x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr)[0]
            message.mark_as_sent()
        except Exception as ex:
            log('Mark as sent ex: ' + str(ex))

    def clear_corr(self):
        """
        Clear messages list
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        # don't delete data about active file transfer
        self._corr = filter(lambda x: x.get_type() in (2, 3) and x.get_status() >= 2, self._corr)
        self._unsaved_messages = 0

    def update_transfer_data(self, file_number, status, inline=None):
        """
        Update status of active transfer and load inline if needed
        """
        try:
            tr = filter(lambda x: x.get_type() == MESSAGE_TYPE['FILE_TRANSFER'] and x.is_active(file_number),
                        self._corr)[0]
            tr.set_status(status)
            if inline:  # inline was loaded
                i = self._corr.index(tr)
                self._corr.insert(i, inline)
                return i - len(self._corr)
        except:
            pass

    # -----------------------------------------------------------------------------------------------------------------
    # Alias support
    # -----------------------------------------------------------------------------------------------------------------

    def set_name(self, value):
        """
        Set new name or ignore if alias exists
        :param value: new name
        """
        if not self._alias:
            super(Friend, self).set_name(value)

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
        super(Profile, self).__init__(tox.self_get_name(),
                                      tox.self_get_status_message(),
                                      screen.user_info,
                                      tox.self_get_address())
        self._screen = screen
        self._messages = screen.messages
        self._tox = tox
        self._file_transfers = {}  # dict of file transfers. key - tuple (friend_number, file_number)
        self._call = calls.AV(tox.AV)  # object with data about calls
        self._incoming_calls = set()
        settings = Settings.get_instance()
        self._show_online = settings['show_online_friends']
        screen.online_contacts.setCurrentIndex(int(self._show_online))
        aliases = settings['friends_aliases']
        data = tox.self_get_friend_list()
        self._history = History(tox.self_get_public_key())  # connection to db
        self._friends, self._active_friend = [], -1
        for i in data:  # creates list of friends
            tox_id = tox.friend_get_public_key(i)
            if not self._history.friend_exists_in_db(tox_id):
                self._history.add_friend_to_db(tox_id)
            try:
                alias = filter(lambda x: x[0] == tox_id, aliases)[0][1]
            except:
                alias = ''
            item = self.create_friend_item()
            name = alias or tox.friend_get_name(i) or tox_id
            status_message = tox.friend_get_status_message(i)
            message_getter = self._history.messages_getter(tox_id)
            friend = Friend(message_getter, i, name, status_message, item, tox_id)
            friend.set_alias(alias)
            self._friends.append(friend)
        self.filtration(self._show_online)

    # -----------------------------------------------------------------------------------------------------------------
    # Edit current user's data
    # -----------------------------------------------------------------------------------------------------------------

    def change_status(self):
        """
        Changes status of user (online, away, busy)
        """
        if self._status is not None:
            self.set_status((self._status + 1) % 3)

    def set_status(self, status):
        super(Profile, self).set_status(status)
        if status is not None:
            self._tox.self_set_status(status)

    def set_name(self, value):
        super(Profile, self).set_name(value)
        self._tox.self_set_name(self._name.encode('utf-8'))

    def set_status_message(self, value):
        super(Profile, self).set_status_message(value)
        self._tox.self_set_status_message(self._status_message.encode('utf-8'))

    def new_nospam(self):
        import random
        self._tox.self_set_nospam(random.randint(0, 4294967295))  # no spam - uint32
        self._tox_id = self._tox.self_get_address()
        return self._tox_id

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
            friend.visibility = friend.visibility or friend.messages
            if friend.visibility:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 70))
            else:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 0))
        self._show_online, self._filter_string = show_online, filter_str
        settings = Settings.get_instance()
        settings['show_online_friends'] = self._show_online
        settings.save()

    def update_filtration(self):
        """
        Update list of contacts when 1 of friends change connection status
        """
        self.filtration(self._show_online, self._filter_string)

    def get_friend_by_number(self, num):
        return filter(lambda x: x.number == num, self._friends)[0]

    def get_friend(self, num):
        return self._friends[num]

    # -----------------------------------------------------------------------------------------------------------------
    # Work with active friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_active(self):
        return self._active_friend

    def set_active(self, value=None):
        """
        Change current active friend or update info
        :param value: number of new active friend in friend's list or None to update active user's data
        """
        if value is None and self._active_friend == -1:  # nothing to update
            return
        if value == -1:  # all friends were deleted
            self._screen.account_name.setText('')
            self._screen.account_status.setText('')
            self._active_friend = -1
            self._screen.account_avatar.setHidden(True)
            self._messages.clear()
            self._screen.messageEdit.clear()
            return
        try:
            self.send_typing(False)
            self._screen.typing.setVisible(False)
            if value is not None:
                self._active_friend = value
                friend = self._friends[value]
                self._friends[value].set_messages(False)
                self._screen.messageEdit.clear()
                self._messages.clear()
                friend.load_corr()
                messages = friend.get_corr()[-PAGE_SIZE:]
                for message in messages:
                    if message.get_type() <= 1:
                        data = message.get_data()
                        self.create_message_item(data[0],
                                                 convert_time(data[2]),
                                                 friend.name if data[1] == MESSAGE_OWNER['FRIEND'] else self._name,
                                                 data[3])
                    elif message.get_type() == 2:
                        item = self.create_file_transfer_item(message)
                        if message.get_status() >= 2:  # active file transfer
                            try:
                                ft = self._file_transfers[(message.get_friend_number(), message.get_file_number())]
                                ft.set_state_changed_handler(item.update)
                                ft.signal()
                            except:
                                print 'Incoming not started transfer - no info found'
                    else:  # inline
                        self.create_inline_item(message.get_data())
                self._messages.scrollToBottom()
                if value in self._call:
                    self._screen.active_call()
                elif value in self._incoming_calls:
                    self._screen.incoming_call()
                else:
                    self._screen.call_finished()
            else:
                friend = self._friends[self._active_friend]

            self._screen.account_name.setText(friend.name)
            self._screen.account_status.setText(friend.status_message)
            avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(friend.tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
            if not os.path.isfile(avatar_path):  # load default image
                avatar_path = curr_directory() + '/images/avatar.png'
            os.chdir(os.path.dirname(avatar_path))
            pixmap = QtGui.QPixmap(QtCore.QSize(64, 64))
            pixmap.load(avatar_path)
            self._screen.account_avatar.setScaledContents(False)
            self._screen.account_avatar.setPixmap(pixmap.scaled(64, 64, QtCore.Qt.KeepAspectRatio))
            self._screen.account_avatar.repaint()  # comment?
        except:  # no friend found. ignore
            log('Incorrect friend value: ' + str(value))
            raise

    active_friend = property(get_active, set_active)

    def get_last_message(self):
        return self._friends[self._active_friend].get_last_message_text()

    def get_active_number(self):
        return self._friends[self._active_friend].number if self._active_friend + 1 else -1

    def get_active_name(self):
        return self._friends[self._active_friend].name if self._active_friend + 1 else ''

    def is_active_online(self):
        return self._active_friend + 1 and self._friends[self._active_friend].status is not None

    def update(self):
        if self._active_friend + 1:
            self.set_active(self._active_friend)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend connection status callbacks
    # -----------------------------------------------------------------------------------------------------------------

    def friend_online(self, friend_number):
        for key in filter(lambda x: x[0] == friend_number, self._file_transfers.keys()):
            self.resume_transfer(key[0], key[1], True)

    def friend_exit(self, friend_number):
        """
        Friend with specified number quit
        """
        # TODO: fix and add full file resuming support
        self.get_friend_by_number(friend_number).status = None
        self.friend_typing(friend_number, False)
        if friend_number in self._call:
            self._call.finish_call(friend_number, True)
        for key in filter(lambda x: x[0] == friend_number, self._file_transfers.keys()):
            if type(self._file_transfers[key]) in (ReceiveAvatar, SendAvatar):
                self._file_transfers[key].cancelled()
            else:
                self._file_transfers[key].pause(False)

    # -----------------------------------------------------------------------------------------------------------------
    # Typing notifications
    # -----------------------------------------------------------------------------------------------------------------

    def send_typing(self, typing):
        """
        Send typing notification to a friend
        """
        if Settings.get_instance()['typing_notifications'] and self._active_friend + 1:
            friend = self._friends[self._active_friend]
            if friend.status is not None:
                self._tox.self_set_typing(friend.number, typing)

    def friend_typing(self, friend_number, typing):
        """
        Display incoming typing notification
        """
        if friend_number == self.get_active_number():
            self._screen.typing.setVisible(typing)

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def send_messages(self, friend_number):
        """
        Send 'offline' messages to friend
        """
        friend = self.get_friend_by_number(friend_number)
        friend.load_corr()
        messages = friend.unsent_messages()
        try:
            for message in messages:
                self.split_and_send(friend_number, message.get_data()[-1], message.get_data()[0].encode('utf-8'))
        except:
            pass

    def split_and_send(self, number, message_type, message):
        """
        Message splitting
        :param number: friend's number
        :param message_type: type of message
        :param message: message text
        """
        while len(message) > TOX_MAX_MESSAGE_LENGTH:
            size = TOX_MAX_MESSAGE_LENGTH * 4 / 5
            last_part = message[size:TOX_MAX_MESSAGE_LENGTH]
            if ' ' in last_part:
                index = last_part.index(' ')
            elif ',' in last_part:
                index = last_part.index(',')
            elif '.' in last_part:
                index = last_part.index('.')
            else:
                index = TOX_MAX_MESSAGE_LENGTH - size - 1
            index += size + 1
            self._tox.friend_send_message(number, message_type, message[:index])
            message = message[index:]
        self._tox.friend_send_message(number, message_type, message)

    def new_message(self, friend_num, message_type, message):
        """
        Current user gets new message
        :param friend_num: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        if friend_num == self.get_active_number():  # add message to list
            user_name = Profile.get_instance().get_active_name()
            self.create_message_item(message.decode('utf-8'), curr_time(), user_name, message_type)
            self._messages.scrollToBottom()
            self._friends[self._active_friend].append_message(
                TextMessage(message.decode('utf-8'), MESSAGE_OWNER['FRIEND'], time.time(), message_type))
        else:
            friend = self.get_friend_by_number(friend_num)
            friend.set_messages(True)
            friend.append_message(
                TextMessage(message.decode('utf-8'), MESSAGE_OWNER['FRIEND'], time.time(), message_type))
            if not friend.visibility:
                self.update_filtration()

    def send_message(self, text):
        """
        Send message to active friend
        :param text: message text
        """
        if text.startswith('/plugin '):
            plugin_support.PluginLoader.get_instance().command(text[8:])
            self._screen.messageEdit.clear()
        elif text:
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            friend = self._friends[self._active_friend]
            if friend.status is not None:
                self.split_and_send(friend.number, message_type, text.encode('utf-8'))
            self.create_message_item(text, curr_time(), self._name, message_type)
            self._screen.messageEdit.clear()
            self._messages.scrollToBottom()
            friend.append_message(TextMessage(text, MESSAGE_OWNER['NOT_SENT'], time.time(), message_type))
            friend.inc_receipts()

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def save_history(self):
        """
        Save history to db
        """
        if hasattr(self, '_history'):
            if Settings.get_instance()['save_history']:
                for friend in self._friends:
                    messages = friend.get_corr_for_saving()
                    if not self._history.friend_exists_in_db(friend.tox_id):
                        self._history.add_friend_to_db(friend.tox_id)
                    self._history.save_messages_to_db(friend.tox_id, messages)
                    unsent_count = len(friend.unsent_messages())
                    self._history.update_messages(friend.tox_id, unsent_count)
            self._history.save()
            del self._history

    def clear_history(self, num=None):
        """
        Clear chat history
        """
        if num is not None:
            friend = self._friends[num]
            friend.clear_corr()
            if self._history.friend_exists_in_db(friend.tox_id):
                self._history.delete_messages(friend.tox_id)
                self._history.delete_friend_from_db(friend.tox_id)
        else:  # clear all history
            for number in xrange(len(self._friends)):
                self.clear_history(number)
        if num is None or num == self.get_active_number():
            self._messages.clear()
            self._messages.repaint()

    def load_history(self):
        """
        Tries to load next part of messages
        """
        friend = self._friends[self._active_friend]
        friend.load_corr(False)
        data = friend.get_corr()
        if not data:
            return
        data.reverse()
        data = data[self._messages.count():self._messages.count() + PAGE_SIZE]
        for message in data:
            if message.get_type() <= 1:
                data = message.get_data()
                self.create_message_item(data[0],
                                         convert_time(data[2]),
                                         friend.name if data[1] == MESSAGE_OWNER['FRIEND'] else self._name,
                                         data[3],
                                         False)
            elif message.get_type() == 2:
                item = self.create_file_transfer_item(message, False)
                if message.get_status() >= 2:
                    ft = self._file_transfers[(message.get_friend_number(), message.get_file_number())]
                    ft.set_state_changed_handler(item.update)

    def export_history(self, directory):
        self._history.export(directory)

    # -----------------------------------------------------------------------------------------------------------------
    # Factories for friend, message and file transfer items
    # -----------------------------------------------------------------------------------------------------------------

    def create_friend_item(self):
        """
        Method-factory
        :return: new widget for friend instance
        """
        item = ContactItem()
        elem = QtGui.QListWidgetItem(self._screen.friends_list)
        elem.setSizeHint(QtCore.QSize(250, 70))
        self._screen.friends_list.addItem(elem)
        self._screen.friends_list.setItemWidget(elem, item)
        return item

    def create_message_item(self, text, time, name, message_type, append=True):
        item = MessageItem(text, time, name, message_type, self._messages)
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

    def create_file_transfer_item(self, tm, append=True):
        data = list(tm.get_data())
        data[3] = self.get_friend_by_number(data[4]).name if data[3] else self._name
        data.append(self._messages.width())
        item = FileTransferItem(*data)
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width() - 30, 34))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)
        return item

    def create_inline_item(self, data, append=True):
        item = InlineImageItem(data, self._messages.width())
        elem = QtGui.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
        if append:
            self._messages.addItem(elem)
        else:
            self._messages.insertItem(0, elem)
        self._messages.setItemWidget(elem, item)

    # -----------------------------------------------------------------------------------------------------------------
    # Work with friends (remove, block, set alias, get public key)
    # -----------------------------------------------------------------------------------------------------------------

    def set_alias(self, num):
        """
        Set new alias for friend
        """
        friend = self._friends[num]
        name = friend.name.encode('utf-8')
        dialog = QtGui.QApplication.translate('MainWindow',
                                              "Enter new alias for friend {} or leave empty to use friend's name:",
                                              None, QtGui.QApplication.UnicodeUTF8)
        dialog = dialog.format(name.decode('utf-8'))
        title = QtGui.QApplication.translate('MainWindow',
                                             'Set alias',
                                             None, QtGui.QApplication.UnicodeUTF8)

        text, ok = QtGui.QInputDialog.getText(None,
                                              title,
                                              dialog,
                                              QtGui.QLineEdit.Normal,
                                              name.decode('utf-8'))
        if ok:
            settings = Settings.get_instance()
            aliases = settings['friends_aliases']
            if text:
                friend.name = text.encode('utf-8')
                try:
                    index = map(lambda x: x[0], aliases).index(friend.tox_id)
                    aliases[index] = (friend.tox_id, text)
                except:
                    aliases.append((friend.tox_id, text))
                friend.set_alias(text)
            else:  # use default name
                friend.name = self._tox.friend_get_name(friend.number).encode('utf-8')
                friend.set_alias('')
                try:
                    index = map(lambda x: x[0], aliases).index(friend.tox_id)
                    del aliases[index]
                except:
                    pass
            settings.save()
            self.set_active()

    def friend_public_key(self, num):
        return self._friends[num].tox_id

    def delete_friend(self, num):
        """
        Removes friend from contact list
        :param num: number of friend in list
        """
        friend = self._friends[num]
        try:
            settings = Settings.get_instance()
            index = map(lambda x: x[0], settings['friends_aliases']).index(friend.tox_id)
            del settings['friends_aliases'][index]
            settings.save()
        except:
            pass
        self.clear_history(num)
        if self._history.friend_exists_in_db(friend.tox_id):
            self._history.delete_friend_from_db(friend.tox_id)
        self._tox.friend_delete(friend.number)
        del self._friends[num]
        self._screen.friends_list.takeItem(num)
        if num == self._active_friend:  # active friend was deleted
            if not len(self._friends):  # last friend was deleted
                self.set_active(-1)
            else:
                self.set_active(0)
        data = self._tox.get_savedata()
        ProfileHelper.get_instance().save_profile(data)

    def add_friend(self, tox_id):
        """
        Adds friend to list
        """
        num = self._tox.friend_add_norequest(tox_id)  # num - friend number
        item = self.create_friend_item()
        try:
            if not self._history.friend_exists_in_db(tox_id):
                self._history.add_friend_to_db(tox_id)
            message_getter = self._history.messages_getter(tox_id)
        except Exception as ex:  # something is wrong
            log('Accept friend request failed! ' + str(ex))
            message_getter = None
        friend = Friend(message_getter, num, tox_id, '', item, tox_id)
        self._friends.append(friend)

    def block_user(self, tox_id):
        """
        Block user with specified tox id (or public key) - delete from friends list and ignore friend requests
        """
        tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
        if tox_id == self.tox_id[:TOX_PUBLIC_KEY_SIZE * 2]:
            return
        settings = Settings.get_instance()
        if tox_id not in settings['blocked']:
            settings['blocked'].append(tox_id)
            settings.save()
        try:
            num = self._tox.friend_by_public_key(tox_id)
            self.delete_friend(num)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)
        except:  # not in friend list
            pass

    def unblock_user(self, tox_id, add_to_friend_list):
        """
        Unblock user
        :param tox_id: tox id of contact
        :param add_to_friend_list: add this contact to friend list or not
        """
        s = Settings.get_instance()
        s['blocked'].remove(tox_id)
        s.save()
        if add_to_friend_list:
            self.add_friend(tox_id)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend requests
    # -----------------------------------------------------------------------------------------------------------------

    def send_friend_request(self, tox_id, message):
        """
        Function tries to send request to contact with specified id
        :param tox_id: id of new contact or tox dns 4 value
        :param message: additional message
        :return: True on success else error string
        """
        try:
            message = message or 'Hello! Add me to your contact list please'
            if '@' in tox_id:  # value like groupbot@toxme.io
                tox_id = tox_dns(tox_id)
                if tox_id is None:
                    raise Exception('TOX DNS lookup failed')
            if len(tox_id) == TOX_PUBLIC_KEY_SIZE * 2:  # public key
                self.add_friend(tox_id)
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Friend added", None, QtGui.QApplication.UnicodeUTF8))
                text = (QtGui.QApplication.translate("MainWindow", 'Friend added without sending friend request', None, QtGui.QApplication.UnicodeUTF8))
                msgBox.setText(text)
                msgBox.exec_()
            else:
                result = self._tox.friend_add(tox_id, message.encode('utf-8'))
                tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
                item = self.create_friend_item()
                if not self._history.friend_exists_in_db(tox_id):
                    self._history.add_friend_to_db(tox_id)
                message_getter = self._history.messages_getter(tox_id)
                friend = Friend(message_getter, result, tox_id, '', item, tox_id)
                self._friends.append(friend)
            data = self._tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)
            return True
        except Exception as ex:  # wrong data
            log('Friend request failed with ' + str(ex))
            return str(ex)

    def process_friend_request(self, tox_id, message):
        """
        Accept or ignore friend request
        :param tox_id: tox id of contact
        :param message: message
        """
        try:
            text = QtGui.QApplication.translate('MainWindow', 'User {} wants to add you to contact list. Message:\n{}', None, QtGui.QApplication.UnicodeUTF8)
            info = text.format(tox_id, message)
            fr_req = QtGui.QApplication.translate('MainWindow', 'Friend request', None, QtGui.QApplication.UnicodeUTF8)
            reply = QtGui.QMessageBox.question(None, fr_req, info, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:  # accepted
                self.add_friend(tox_id)
                data = self._tox.get_savedata()
                ProfileHelper.get_instance().save_profile(data)
        except Exception as ex:  # something is wrong
            log('Accept friend request failed! ' + str(ex))

    # -----------------------------------------------------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------------------------------------------------

    def reset(self, restart):
        """
        Recreate tox instance
        :param restart: method which calls restart and returns new tox instance
        """
        for key in self._file_transfers.keys():
            self._file_transfers[key].cancel()
            del self._file_transfers[key]
        self._call.stop()
        del self._tox
        self._tox = restart()
        self.status = None
        for friend in self._friends:
            friend.status = None

    def close(self):
        if hasattr(self, '_call'):
            self._call.stop()
            del self._call

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def incoming_file_transfer(self, friend_number, file_number, size, file_name):
        """
        New transfer
        :param friend_number: number of friend who sent file
        :param file_number: file number
        :param size: file size in bytes
        :param file_name: file name without path
        """
        settings = Settings.get_instance()
        friend = self.get_friend_by_number(friend_number)
        auto = settings['allow_auto_accept'] and friend.tox_id in settings['auto_accept_from_friends']
        inline = (file_name == 'toxygen_inline.png' or file_name == 'utox-inline.png') and settings['allow_inline']
        if inline and size < 1024 * 1024:
            self.accept_transfer(None, '', friend_number, file_number, size, True)
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 FILE_TRANSFER_MESSAGE_STATUS['INCOMING_STARTED'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)

        elif auto:
            path = settings['auto_accept_path'] or curr_directory()
            if not os.path.isdir(path):
                path = curr_directory()
            new_file_name, i = file_name, 1
            while os.path.isfile(path + '/' + new_file_name):  # file with same name already exists
                if '.' in file_name:  # has extension
                    d = file_name.rindex('.')
                else:  # no extension
                    d = len(file_name)
                new_file_name = file_name[:d] + ' ({})'.format(i) + file_name[d:]
                i += 1
            self.accept_transfer(None, path + '/' + new_file_name, friend_number, file_number, size)
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 FILE_TRANSFER_MESSAGE_STATUS['INCOMING_STARTED'],
                                 size,
                                 new_file_name,
                                 friend_number,
                                 file_number)
        else:
            tm = TransferMessage(MESSAGE_OWNER['FRIEND'],
                                 time.time(),
                                 FILE_TRANSFER_MESSAGE_STATUS['INCOMING_NOT_STARTED'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)
        if friend_number == self.get_active_number():
            item = self.create_file_transfer_item(tm)
            if (inline and size < 1024 * 1024) or auto:
                self._file_transfers[(friend_number, file_number)].set_state_changed_handler(item.update)
            self._messages.scrollToBottom()
        else:
            friend.set_messages(True)

        friend.append_message(tm)

    def cancel_transfer(self, friend_number, file_number, already_cancelled=False):
        """
        Stop transfer
        :param friend_number: number of friend
        :param file_number: file number
        :param already_cancelled: was cancelled by friend
        """
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      FILE_TRANSFER_MESSAGE_STATUS['CANCELLED'])
        if (friend_number, file_number) in self._file_transfers:
            tr = self._file_transfers[(friend_number, file_number)]
            if not already_cancelled:
                tr.cancel()
            else:
                tr.cancelled()
            if (friend_number, file_number) in self._file_transfers:
                del tr
                del self._file_transfers[(friend_number, file_number)]
        else:
            self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])

    def pause_transfer(self, friend_number, file_number, by_friend=False):
        """
        Pause transfer with specified data
        """
        tr = self._file_transfers[(friend_number, file_number)]
        tr.pause(by_friend)
        t = FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_FRIEND'] if by_friend else FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_USER']
        self.get_friend_by_number(friend_number).update_transfer_data(file_number, t)

    def resume_transfer(self, friend_number, file_number, by_friend=False):
        """
        Resume transfer with specified data
        """
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      FILE_TRANSFER_MESSAGE_STATUS['OUTGOING'])
        tr = self._file_transfers[(friend_number, file_number)]
        if by_friend:
            tr.state = TOX_FILE_TRANSFER_STATE['RUNNING']
            tr.signal()
        else:  # send seek control?
            tr.send_control(TOX_FILE_CONTROL['RESUME'])

    def accept_transfer(self, item, path, friend_number, file_number, size, inline=False):
        """
        :param item: transfer item.
        :param path: path for saving
        :param friend_number: friend number
        :param file_number: file number
        :param size: file size
        :param inline: is inline image
        """
        if not inline:
            rt = ReceiveTransfer(path, self._tox, friend_number, size, file_number)
        else:
            rt = ReceiveToBuffer(self._tox, friend_number, size, file_number)
        self._file_transfers[(friend_number, file_number)] = rt
        self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['RESUME'])
        if item is not None:
            rt.set_state_changed_handler(item.update)
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      FILE_TRANSFER_MESSAGE_STATUS['INCOMING_STARTED'])

    def send_screenshot(self, data):
        """
        Send screenshot to current active friend
        :param data: raw data - png
        """
        friend = self._friends[self._active_friend]
        st = SendFromBuffer(self._tox, friend.number, data, 'toxygen_inline.png')
        self._file_transfers[(friend.number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_OWNER['ME'],
                             time.time(),
                             FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_FRIEND'],  # OUTGOING NOT STARTED
                             len(data),
                             'toxygen_inline.png',
                             friend.number,
                             st.get_file_number())
        item = self.create_file_transfer_item(tm)
        friend.append_message(tm)
        st.set_state_changed_handler(item.update)
        self._messages.scrollToBottom()

    def send_file(self, path, number=None):
        """
        Send file to current active friend
        :param path: file path
        :param number: friend_number
        """
        friend_number = number or self.get_active_number()
        if self.get_friend_by_number(friend_number).status is None:
            return
        st = SendTransfer(path, self._tox, friend_number)
        self._file_transfers[(friend_number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_OWNER['ME'],
                             time.time(),
                             FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_FRIEND'],  # OUTGOING NOT STARTED
                             os.path.getsize(path),
                             os.path.basename(path),
                             friend_number,
                             st.get_file_number())
        item = self.create_file_transfer_item(tm)
        st.set_state_changed_handler(item.update)
        self._friends[self._active_friend].append_message(tm)
        self._messages.scrollToBottom()

    def incoming_chunk(self, friend_number, file_number, position, data):
        """
        Incoming chunk
        """
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.write_chunk(position, data)
            if transfer.state in (2, 3):  # finished or cancelled
                if type(transfer) is ReceiveAvatar:
                    self.get_friend_by_number(friend_number).load_avatar()
                    self.set_active(None)
                elif type(transfer) is ReceiveToBuffer:  # inline image
                    inline = InlineImage(transfer.get_data())
                    i = self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                      FILE_TRANSFER_MESSAGE_STATUS['FINISHED'],
                                                                                      inline)
                    if friend_number == self.get_active_number():
                        count = self._messages.count()
                        item = InlineImageItem(transfer.get_data(), self._messages.width())
                        elem = QtGui.QListWidgetItem()
                        elem.setSizeHint(QtCore.QSize(600, item.height()))
                        self._messages.insertItem(count + i + 1, elem)
                        self._messages.setItemWidget(elem, item)
                else:
                    self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                  FILE_TRANSFER_MESSAGE_STATUS['FINISHED'])
                del self._file_transfers[(friend_number, file_number)]

    def outgoing_chunk(self, friend_number, file_number, position, size):
        """
        Outgoing chunk
        """
        if (friend_number, file_number) in self._file_transfers:
            transfer = self._file_transfers[(friend_number, file_number)]
            transfer.send_chunk(position, size)
            if transfer.state in (2, 3):  # finished or cancelled
                del self._file_transfers[(friend_number, file_number)]
                if type(transfer) is not SendAvatar:
                    if type(transfer) is SendFromBuffer and Settings.get_instance()['allow_inline']:  # inline
                        inline = InlineImage(transfer.get_data())
                        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                      FILE_TRANSFER_MESSAGE_STATUS['FINISHED'],
                                                                                      inline)
                        self.update()
                    else:
                        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                                      FILE_TRANSFER_MESSAGE_STATUS['FINISHED'])

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars support
    # -----------------------------------------------------------------------------------------------------------------

    def send_avatar(self, friend_number):
        """
        :param friend_number: number of friend who should get new avatar
        """
        avatar_path = (ProfileHelper.get_path() + 'avatars/{}.png').format(self._tox_id[:TOX_PUBLIC_KEY_SIZE * 2])
        if not os.path.isfile(avatar_path):  # reset image
            avatar_path = None
        sa = SendAvatar(avatar_path, self._tox, friend_number)
        self._file_transfers[(friend_number, sa.get_file_number())] = sa

    def incoming_avatar(self, friend_number, file_number, size):
        """
        Friend changed avatar
        :param friend_number: friend number
        :param file_number: file number
        :param size: size of avatar or 0 (default avatar)
        """
        ra = ReceiveAvatar(self._tox, friend_number, size, file_number)
        if ra.state != TOX_FILE_TRANSFER_STATE['CANCELED']:
            self._file_transfers[(friend_number, file_number)] = ra
        else:
            self.get_friend_by_number(friend_number).load_avatar()
            if self.get_active_number() == friend_number:
                self.set_active(None)

    def reset_avatar(self):
        super(Profile, self).reset_avatar()
        for friend in filter(lambda x: x.status is not None, self._friends):
            self.send_avatar(friend.number)

    def set_avatar(self, data):
        super(Profile, self).set_avatar(data)
        for friend in filter(lambda x: x.status is not None, self._friends):
            self.send_avatar(friend.number)

    # -----------------------------------------------------------------------------------------------------------------
    # AV support
    # -----------------------------------------------------------------------------------------------------------------

    def get_call(self):
        return self._call

    call = property(get_call)

    def call_click(self, audio=True, video=False):
        """User clicked audio button in main window"""
        num = self.get_active_number()
        if num not in self._call and self.is_active_online():  # start call
            self._call(num, audio, video)
            self._screen.active_call()
        elif num in self._call:  # finish or cancel call if you call with active friend
            self.stop_call(num, False)

    def incoming_call(self, audio, video, friend_number):
        """
        Incoming call from friend. Only audio is supported now
        """
        friend = self.get_friend_by_number(friend_number)
        self._incoming_calls.add(friend_number)
        if friend_number == self.get_active_number():
            self._screen.incoming_call()
        else:
            friend.set_messages(True)
        if video:
            text = QtGui.QApplication.translate("incoming_call", "Incoming video call", None, QtGui.QApplication.UnicodeUTF8)
        else:
            text = QtGui.QApplication.translate("incoming_call", "Incoming audio call", None, QtGui.QApplication.UnicodeUTF8)
        self._call_widget = avwidgets.IncomingCallWidget(friend_number, text, friend.name)
        self._call_widget.set_pixmap(friend.get_pixmap())
        self._call_widget.show()

    def accept_call(self, friend_number, audio, video):
        """
        Accept incoming call with audio or video
        """
        self._call.accept_call(friend_number, audio, video)
        self._screen.active_call()
        self._incoming_calls.remove(friend_number)
        if hasattr(self, '_call_widget'):
            del self._call_widget

    def stop_call(self, friend_number, by_friend):
        """
        Stop call with friend
        """
        if friend_number in self._incoming_calls:
            self._incoming_calls.remove(friend_number)
        self._screen.call_finished()
        self._call.finish_call(friend_number, by_friend)  # finish or decline call
        if hasattr(self, '_call_widget'):
            del self._call_widget


def tox_factory(data=None, settings=None):
    """
    :param data: user data from .tox file. None = no saved data, create new profile
    :param settings: current profile settings. None = default settings will be used
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
