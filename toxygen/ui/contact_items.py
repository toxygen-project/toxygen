from wrapper.toxcore_enums_and_consts import *
from PyQt5 import QtCore, QtGui, QtWidgets
from contacts import profile
from file_transfers.file_transfers import TOX_FILE_TRANSFER_STATE, PAUSED_FILE_TRANSFERS, DO_NOT_SHOW_ACCEPT_BUTTON, ACTIVE_FILE_TRANSFERS, SHOW_PROGRESS_BAR
from utils.util import *
from ui.widgets import DataLabel, create_menu
from user_data import settings


class ContactItem(QtWidgets.QWidget):
    """
    Contact in friends list
    """

    def __init__(self, settings, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        mode = settings['compact_mode']
        self.setBaseSize(QtCore.QSize(250, 40 if mode else 70))
        self.avatar_label = QtWidgets.QLabel(self)
        size = 32 if mode else 64
        self.avatar_label.setGeometry(QtCore.QRect(3, 4, size, size))
        self.avatar_label.setScaledContents(False)
        self.avatar_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(50 if mode else 75, 3 if mode else 10, 150, 15 if mode else 25))
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPointSize(10 if mode else 12)
        font.setBold(True)
        self.name.setFont(font)
        self.status_message = DataLabel(self)
        self.status_message.setGeometry(QtCore.QRect(50 if mode else 75, 20 if mode else 30, 170, 15 if mode else 20))
        font.setPointSize(10)
        font.setBold(False)
        self.status_message.setFont(font)
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(230, -2 if mode else 5, 32, 32))
        self.messages = UnreadMessagesCount(settings, self)
        self.messages.setGeometry(QtCore.QRect(20 if mode else 52, 20 if mode else 50, 30, 20))


class StatusCircle(QtWidgets.QWidget):
    """
    Connection status
    """
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setGeometry(0, 0, 32, 32)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 32, 32))
        self.unread = False

    def update(self, status, unread_messages=None):
        if unread_messages is None:
            unread_messages = self.unread
        else:
            self.unread = unread_messages
        if status == TOX_USER_STATUS['NONE']:
            name = 'online'
        elif status == TOX_USER_STATUS['AWAY']:
            name = 'idle'
        elif status == TOX_USER_STATUS['BUSY']:
            name = 'busy'
        else:
            name = 'offline'
        if unread_messages:
            name += '_notification'
            self.label.setGeometry(QtCore.QRect(0, 0, 32, 32))
        else:
            self.label.setGeometry(QtCore.QRect(2, 0, 32, 32))
        pixmap = QtGui.QPixmap(join_path(get_images_directory(), '{}.png'.format(name)))
        self.label.setPixmap(pixmap)


class UnreadMessagesCount(QtWidgets.QWidget):

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.resize(30, 20)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 30, 20))
        self.label.setVisible(False)
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        color = settings['unread_color']
        self.label.setStyleSheet('QLabel { color: white; background-color: ' + color + '; border-radius: 10; }')

    def update(self, messages_count):
        color = self._settings['unread_color']
        self.label.setStyleSheet('QLabel { color: white; background-color: ' + color + '; border-radius: 10; }')
        if messages_count:
            self.label.setVisible(True)
            self.label.setText(str(messages_count))
        else:
            self.label.setVisible(False)
