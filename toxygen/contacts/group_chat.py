from contacts import contact
import util.util as util
from PyQt5 import QtGui, QtCore
from wrapper import toxcore_enums_and_consts as constants


# TODO: ngc

class GroupChat(contact.Contact):

    def __init__(self, profile_manager, name, status_message, widget, tox, group_number):
        super().__init__(None, group_number, profile_manager, name, status_message, widget, None)
        self._tox = tox
        self.set_status(constants.TOX_USER_STATUS['NONE'])

    def set_name(self, name):
        self._tox.group_set_title(self._number, name)
        super().set_name(name)

    def send_message(self, message):
        self._tox.group_message_send(self._number, message.encode('utf-8'))

    def new_title(self, title):
        super().set_name(title)

    @staticmethod
    def get_default_avatar_name():
        return 'group.png'

    def remove_invalid_unsent_files(self):
        pass

    def get_names(self):
        peers_count = self._tox.group_number_peers(self._number)
        names = []
        for i in range(peers_count):
            name = self._tox.group_peername(self._number, i)
            names.append(name)
        names = sorted(names, key=lambda n: n.lower())
        return names

    def get_full_status(self):
        names = self.get_names()
        return '\n'.join(names)

    def get_peer_name(self, peer_number):
        return self._tox.group_peername(self._number, peer_number)
