from contacts.friend import *
from file_transfers.file_transfers import *
import time
from contacts import basecontact
from contacts.group_chat import *
import utils.ui as util_ui
import random


class Profile(basecontact.BaseContact):
    """
    Profile of current toxygen user. Contains friends list, tox instance
    """
    def __init__(self, profile_manager, tox, screen):
        """
        :param tox: tox instance
        :param screen: ref to main screen
        """
        basecontact.BaseContact.__init__(self,
                                         profile_manager,
                                         tox.self_get_name(),
                                         tox.self_get_status_message(),
                                         screen.user_info,
                                         tox.self_get_address())
        self._screen = screen
        self._messages = screen.messages
        self._tox = tox
        self._file_transfers = {}  # dict of file transfers. key - tuple (friend_number, file_number)
        self._load_history = True
        self._waiting_for_reconnection = False
        self._contacts_manager = None

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
        super().set_status(status)
        if status is not None:
            self._tox.self_set_status(status)
        elif not self._waiting_for_reconnection:
            self._waiting_for_reconnection = True
            QtCore.QTimer.singleShot(50000, self.reconnect)

    def set_name(self, value):
        if self.name == value:
            return
        tmp = self.name
        super().set_name(value.encode('utf-8'))
        self._tox.self_set_name(self._name.encode('utf-8'))
        message = util_ui.tr('User {} is now known as {}')
        message = message.format(tmp, value)
        for friend in self._contacts:
            friend.append_message(InfoMessage(message, time.time()))
        if self._active_friend + 1:
            self.create_message_item(message, time.time(), '', MESSAGE_TYPE['INFO_MESSAGE'])
            self._messages.scrollToBottom()

    def set_status_message(self, value):
        super().set_status_message(value)
        self._tox.self_set_status_message(self._status_message.encode('utf-8'))

    def new_nospam(self):
        """Sets new nospam part of tox id"""
        self._tox.self_set_nospam(random.randint(0, 4294967295))  # no spam - uint32
        self._tox_id = self._tox.self_get_address()

        return self._tox_id

    # -----------------------------------------------------------------------------------------------------------------
    # Friend connection status callbacks
    # -----------------------------------------------------------------------------------------------------------------

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
    # Private messages
    # -----------------------------------------------------------------------------------------------------------------

    def receipt(self):
        i = 0
        while i < self._messages.count() and not self._messages.itemWidget(self._messages.item(i)).mark_as_sent():
            i += 1

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
        del self._tox
        self._tox = restart()
        self.status = None
        self._contacts_manager.update_filtration()

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

    def reset_avatar(self):
        super().reset_avatar()
        for friend in filter(lambda x: x.status is not None, self._contacts):
            self.send_avatar(friend.number)

    def set_avatar(self, data):
        super().set_avatar(data)
        for friend in filter(lambda x: x.status is not None, self._contacts):
            self.send_avatar(friend.number)
