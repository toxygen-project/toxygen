import contact
import util
from PyQt5 import QtGui, QtCore
import toxcore_enums_and_consts as constants


class GroupChat(contact.Contact):

    def __init__(self, name, status_message, widget, tox, group_number):
        super().__init__(None, group_number, name, status_message, widget, None)
        self._tox = tox
        self.set_status(constants.TOX_USER_STATUS['NONE'])

    def set_name(self, name):
        self._tox.group_set_title(self._number, name)
        super().set_name(name)

    def send_message(self, message):
        self._tox.group_message_send(self._number, message.encode('utf-8'))

    def new_title(self, title):
        super().set_name(title)

    def load_avatar(self):
        path = util.curr_directory() + '/images/group.png'
        width = self._widget.avatar_label.width()
        pixmap = QtGui.QPixmap(path)
        self._widget.avatar_label.setPixmap(pixmap.scaled(width, width, QtCore.Qt.KeepAspectRatio,
                                                          QtCore.Qt.SmoothTransformation))
        self._widget.avatar_label.repaint()

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
