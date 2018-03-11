from ui.list_items import *
from PyQt5 import QtWidgets
from contacts.friend import *
from user_data.settings import *
from wrapper.toxcore_enums_and_consts import *
from ctypes import *
from util import log, Singleton, curr_directory
from network.tox_dns import tox_dns
from db.database import *
from file_transfers.file_transfers import *
import time
from av import calls
import plugin_support
from contacts import basecontact
from ui import items_factory, avwidgets
import cv2
import threading
from contacts.group_chat import *
import re


class Profile(basecontact.BaseContact, Singleton):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    def __init__(self, tox, screen):
        """
        :param tox: tox instance
        :param screen: ref to main screen
        """
        basecontact.BaseContact.__init__(self,
                                         tox.self_get_name(),
                                         tox.self_get_status_message(),
                                         screen.user_info,
                                         tox.self_get_address())
        Singleton.__init__(self)
        self._screen = screen
        self._messages = screen.messages
        self._tox = tox
        self._file_transfers = {}  # dict of file transfers. key - tuple (friend_number, file_number)
        self._load_history = True
        self._waiting_for_reconnection = False
        self._factory = items_factory.ItemsFactory(self._screen.friends_list, self._messages)
        settings = Settings.get_instance()
        self._show_avatars = settings['show_avatars']
        self._paused_file_transfers = dict(settings['paused_file_transfers'])
        # key - file id, value: [path, friend number, is incoming, start position]


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
        elif not self._waiting_for_reconnection:
            self._waiting_for_reconnection = True
            QtCore.QTimer.singleShot(50000, self.reconnect)

    def set_name(self, value):
        if self.name == value:
            return
        tmp = self.name
        super(Profile, self).set_name(value.encode('utf-8'))
        self._tox.self_set_name(self._name.encode('utf-8'))
        message = QtWidgets.QApplication.translate("MainWindow", 'User {} is now known as {}')
        message = message.format(tmp, value)
        for friend in self._contacts:
            friend.append_message(InfoMessage(message, time.time()))
        if self._active_friend + 1:
            self.create_message_item(message, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()

    def set_status_message(self, value):
        super(Profile, self).set_status_message(value)
        self._tox.self_set_status_message(self._status_message.encode('utf-8'))

    def new_nospam(self):
        """Sets new nospam part of tox id"""
        import random
        self._tox.self_set_nospam(random.randint(0, 4294967295))  # no spam - uint32
        self._tox_id = self._tox.self_get_address()
        return self._tox_id

    # -----------------------------------------------------------------------------------------------------------------
    # Friend getters
    # -----------------------------------------------------------------------------------------------------------------

    def get_friend_by_number(self, num):
        return list(filter(lambda x: x.number == num and type(x) is Friend, self._contacts))[0]
    def get_last_message(self):
        if self._active_friend + 1:
            return self.get_curr_friend().get_last_message_text()
        else:
            return ''

    def get_active_number(self):
        return self.get_curr_friend().number if self._active_friend + 1 else -1

    def get_active_name(self):
        return self.get_curr_friend().name if self._active_friend + 1 else ''

    def is_active_online(self):
        return self._active_friend + 1 and self.get_curr_friend().status is not None

    def new_name(self, number, name):
        friend = self.get_friend_by_number(number)
        tmp = friend.name
        friend.set_name(name)
        name = str(name, 'utf-8')
        if friend.name == name and tmp != name:
            message = QtWidgets.QApplication.translate("MainWindow", 'User {} is now known as {}')
            message = message.format(tmp, name)
            friend.append_message(InfoMessage(message, time.time()))
            friend.actions = True
            if number == self.get_active_number():
                self.create_message_item(message, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
                self._messages.scrollToBottom()
            self.set_active(None)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend connection status callbacks
    # -----------------------------------------------------------------------------------------------------------------

    def send_files(self, friend_number):
        friend = self.get_friend_by_number(friend_number)
        friend.remove_invalid_unsent_files()
        files = friend.get_unsent_files()
        try:
            for fl in files:
                data = fl.get_data()
                if data[1] is not None:
                    self.send_inline(data[1], data[0], friend_number, True)
                else:
                    self.send_file(data[0], friend_number, True)
            friend.clear_unsent_files()
            for key in list(self._paused_file_transfers.keys()):
                data = self._paused_file_transfers[key]
                if not os.path.exists(data[0]):
                    del self._paused_file_transfers[key]
                elif data[1] == friend_number and not data[2]:
                    self.send_file(data[0], friend_number, True, key)
                    del self._paused_file_transfers[key]
            if friend_number == self.get_active_number() and self.is_active_a_friend():
                self.update()
        except Exception as ex:
            print('Exception in file sending: ' + str(ex))

    def friend_exit(self, friend_number):
        """
        Friend with specified number quit
        """
        self.get_friend_by_number(friend_number).status = None
        self.friend_typing(friend_number, False)
        if friend_number in self._call:
            self._call.finish_call(friend_number, True)
        for friend_num, file_num in list(self._file_transfers.keys()):
            if friend_num == friend_number:
                ft = self._file_transfers[(friend_num, file_num)]
                if type(ft) is SendTransfer:
                    self._paused_file_transfers[ft.get_id()] = [ft.get_path(), friend_num, False, -1]
                elif type(ft) is ReceiveTransfer and ft.state != TOX_FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
                    self._paused_file_transfers[ft.get_id()] = [ft.get_path(), friend_num, True, ft.total_size()]
                self.cancel_transfer(friend_num, file_num, True)

    # -----------------------------------------------------------------------------------------------------------------
    # Typing notifications
    # -----------------------------------------------------------------------------------------------------------------

    def send_typing(self, typing):
        """
        Send typing notification to a friend
        """
        if Settings.get_instance()['typing_notifications'] and self._active_friend + 1:
            try:
                friend = self.get_curr_friend()
                if friend.status is not None:
                    self._tox.self_set_typing(friend.number, typing)
            except:
                pass

    def friend_typing(self, friend_number, typing):
        """
        Display incoming typing notification
        """
        if friend_number == self.get_active_number() and self.is_active_a_friend():
            self._screen.typing.setVisible(typing)

    # -----------------------------------------------------------------------------------------------------------------
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def receipt(self):
        i = 0
        while i < self._messages.count() and not self._messages.itemWidget(self._messages.item(i)).mark_as_sent():
            i += 1

    def send_messages(self, friend_number):
        """
        Send 'offline' messages to friend
        """
        friend = self.get_friend_by_number(friend_number)
        friend.load_corr()
        messages = friend.get_unsent_messages()
        try:
            for message in messages:
                self.split_and_send(friend_number, message.get_data()[-1], message.get_data()[0].encode('utf-8'))
                friend.inc_receipts()
        except Exception as ex:
            log('Sending pending messages failed with ' + str(ex))

    def split_message(self, message):
        messages = []
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
            messages.append(message[:index])
            message = message[index:]

        return messages

    def new_message(self, friend_num, message_type, message):
        """
        Current user gets new message
        :param friend_num: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        if friend_num == self.get_active_number()and self.is_active_a_friend():  # add message to list
            t = time.time()
            self.create_message_item(message, t, MESSAGE_OWNER['FRIEND'], message_type)
            self._messages.scrollToBottom()
            self.get_curr_friend().append_message(
                TextMessage(message, MESSAGE_OWNER['FRIEND'], t, message_type))
        else:
            friend = self.get_friend_by_number(friend_num)
            friend.inc_messages()
            friend.append_message(
                TextMessage(message, MESSAGE_OWNER['FRIEND'], time.time(), message_type))
            if not friend.visibility:
                self.update_filtration()

    def send_message_to_friend(self, text, friend_number=None):
        """
        Send message
        :param text: message text
        :param friend_number: number of friend
        """
        if friend_number is None:
            friend_number = self.get_active_number()
        if text.startswith('/plugin '):
            self._plugin_loader.command(text[8:])
            self._screen.messageEdit.clear()
        elif text and friend_number >= 0:
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            friend = self.get_friend_by_number(friend_number)
            friend.inc_receipts()
            if friend.status is not None:
                messages = self.split_message(text.encode('utf-8'))
                for message in messages:
                    self._tox.friend_send_message(friend_number, message_type, message)
            t = time.time()
            if friend.number == self.get_active_number() and self.is_active_a_friend():
                self.create_message_item(text, t, MESSAGE_OWNER['NOT_SENT'], message_type)
                self._screen.messageEdit.clear()
                self._messages.scrollToBottom()
            friend.append_message(TextMessage(text, MESSAGE_OWNER['NOT_SENT'], t, message_type))

    def delete_message(self, message_id):
        friend = self.get_curr_friend()
        friend.delete_message(time)
        self._history.delete_message(friend.tox_id, message_id)
        self.update()

    # -----------------------------------------------------------------------------------------------------------------
    # Friend, message and file transfer items creation
    # -----------------------------------------------------------------------------------------------------------------


    def create_message_item(self, text, time, owner, message_type, append=True):
        if message_type == MESSAGE_TYPE['INFO_MESSAGE']:
            name = ''
        elif owner == MESSAGE_OWNER['FRIEND']:
            name = self.get_active_name()
        else:
            name = self._name
        pixmap = None
        if self._show_avatars:
            if owner == MESSAGE_OWNER['FRIEND']:
                pixmap = self.get_curr_friend().get_pixmap()
            else:
                pixmap = self.get_pixmap()
        return self._factory.message_item(text, time, name, owner != MESSAGE_OWNER['NOT_SENT'],
                                          message_type, append, pixmap)

    def create_gc_message_item(self, text, time, owner, name, message_type, append=True):
        pixmap = None
        if self._show_avatars:
            if owner == MESSAGE_OWNER['FRIEND']:
                pixmap = self.get_curr_friend().get_pixmap()
            else:
                pixmap = self.get_pixmap()
        return self._factory.message_item(text, time, name, True,
                                          message_type - 5, append, pixmap)

    def create_file_transfer_item(self, tm, append=True):
        data = list(tm.get_data())
        data[3] = self.get_friend_by_number(data[4]).name if data[3] else self._name
        return self._factory.file_transfer_item(data, append)

    def create_unsent_file_item(self, message, append=True):
        data = message.get_data()
        return self._factory.unsent_file_item(os.path.basename(data[0]),
                                              os.path.getsize(data[0]) if data[1] is None else len(data[1]),
                                              self.name,
                                              data[2],
                                              append)

    def create_inline_item(self, data, append=True):
        return self._factory.inline_item(data, append)

    # -----------------------------------------------------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------------------------------------------------

    def reset(self, restart):
        """
        Recreate tox instance
        :param restart: method which calls restart and returns new tox instance
        """
        for friend in self._contacts:
            self.friend_exit(friend.number)
        self._call.stop()
        del self._call
        del self._tox
        self._tox = restart()
        self._call = calls.AV(self._tox.AV)
        self.status = None
        for friend in self._contacts:
            friend.number = self._tox.friend_by_public_key(friend.tox_id)  # numbers update
        self.update_filtration()

    def reconnect(self):
        self._waiting_for_reconnection = False
        if self.status is None or all(list(map(lambda x: x.status is None, self._contacts))) and len(self._contacts):
            self._waiting_for_reconnection = True
            self.reset(self._screen.reset)
            QtCore.QTimer.singleShot(50000, self.reconnect)

    def close(self):
        for friend in filter(lambda x: type(x) is Friend, self._contacts):
            self.friend_exit(friend.number)
        for i in range(len(self._contacts)):
            del self._contacts[0]
        if hasattr(self, '_call'):
            self._call.stop()
            del self._call
        s = Settings.get_instance()
        s['paused_file_transfers'] = dict(self._paused_file_transfers) if s['resend_files'] else {}
        s.save()

    def reset_avatar(self):
        super(Profile, self).reset_avatar()
        for friend in filter(lambda x: x.status is not None, self._contacts):
            self.send_avatar(friend.number)

    def set_avatar(self, data):
        super(Profile, self).set_avatar(data)
        for friend in filter(lambda x: x.status is not None, self._contacts):
            self.send_avatar(friend.number)
