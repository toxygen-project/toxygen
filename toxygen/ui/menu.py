from PyQt5 import QtCore, QtGui, QtWidgets, uic
from user_data.settings import *
from utils.util import *
from ui.widgets import CenteredWidget, DataLabel, LineEdit, RubberBandWindow
import pyaudio
import updater.updater as updater
import utils.ui as util_ui
import cv2


class AddContact(CenteredWidget):
    """Add contact form"""

    def __init__(self, settings, contacts_manager, tox_id=''):
        super().__init__()
        self._settings = settings
        self._contacts_manager = contacts_manager
        self.initUI(tox_id)
        self._adding = False
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def initUI(self, tox_id):
        self.setObjectName('AddContact')
        self.resize(568, 306)
        self.sendRequestButton = QtWidgets.QPushButton(self)
        self.sendRequestButton.setGeometry(QtCore.QRect(50, 270, 471, 31))
        self.sendRequestButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setBaseSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setObjectName("sendRequestButton")
        self.sendRequestButton.clicked.connect(self.add_friend)
        self.tox_id = LineEdit(self)
        self.tox_id.setGeometry(QtCore.QRect(50, 40, 471, 27))
        self.tox_id.setObjectName("lineEdit")
        self.tox_id.setText(tox_id)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 10, 80, 20))
        self.error_label = DataLabel(self)
        self.error_label.setGeometry(QtCore.QRect(120, 10, 420, 20))
        font = QtGui.QFont()
        font.setFamily(self._settings['font'])
        font.setPointSize(10)
        font.setWeight(30)
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("QLabel { color: #BC1C1C; }")
        self.label.setObjectName("label")
        self.message_edit = QtWidgets.QTextEdit(self)
        self.message_edit.setGeometry(QtCore.QRect(50, 110, 471, 151))
        self.message_edit.setObjectName("textEdit")
        self.message = QtWidgets.QLabel(self)
        self.message.setGeometry(QtCore.QRect(50, 70, 101, 31))
        self.message.setFont(font)
        self.message.setObjectName("label_2")
        self.retranslateUi()
        self.message_edit.setText('Hello! Add me to your contact list please')
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.message.setFont(font)
        QtCore.QMetaObject.connectSlotsByName(self)

    def add_friend(self):
        if self._adding:
            return
        self._adding = True
        tox_id = self.tox_id.text().strip()
        if tox_id.startswith('tox:'):
            tox_id = tox_id[4:]
        send = self._contacts_manager.send_friend_request(tox_id, self.message_edit.toPlainText())
        self._adding = False
        if send is True:
            # request was successful
            self.close()
        else:  # print error data
            self.error_label.setText(send)

    def retranslateUi(self):
        self.setWindowTitle(util_ui.tr('Add contact'))
        self.sendRequestButton.setText(util_ui.tr('Send request'))
        self.label.setText(util_ui.tr('TOX ID:'))
        self.message.setText(util_ui.tr('Message:'))
        self.tox_id.setPlaceholderText(util_ui.tr('TOX ID or public key of contact'))


class ProfileSettings(CenteredWidget):
    """Form with profile settings such as name, status, TOX ID"""
    def __init__(self, profile, profile_manager, settings, toxes):
        super().__init__()
        self._profile = profile
        self._profile_manager = profile_manager
        self._settings = settings
        self._toxes = toxes
        self._auto = False
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("ProfileSettingsForm")
        self.setMinimumSize(QtCore.QSize(700, 600))
        self.setMaximumSize(QtCore.QSize(700, 600))
        self.nick = LineEdit(self)
        self.nick.setGeometry(QtCore.QRect(30, 60, 350, 27))
        self.nick.setText(self._profile.name)
        self.status = QtWidgets.QComboBox(self)
        self.status.setGeometry(QtCore.QRect(400, 60, 200, 27))
        self.status_message = LineEdit(self)
        self.status_message.setGeometry(QtCore.QRect(30, 130, 350, 27))
        self.status_message.setText(self._profile.status_message)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 30, 91, 25))
        font = QtGui.QFont()
        font.setFamily(self._settings['font'])
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 100, 25))
        self.label_2.setFont(font)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(40, 180, 100, 25))
        self.label_3.setFont(font)
        self.tox_id = QtWidgets.QLabel(self)
        self.tox_id.setGeometry(QtCore.QRect(15, 210, 685, 21))
        font.setPointSize(10)
        self.tox_id.setFont(font)
        self.tox_id.setText(self._profile.tox_id)
        self.copyId = QtWidgets.QPushButton(self)
        self.copyId.setGeometry(QtCore.QRect(40, 250, 180, 30))
        self.copyId.clicked.connect(self.copy)
        self.export = QtWidgets.QPushButton(self)
        self.export.setGeometry(QtCore.QRect(230, 250, 180, 30))
        self.export.clicked.connect(self.export_profile)
        self.new_nospam = QtWidgets.QPushButton(self)
        self.new_nospam.setGeometry(QtCore.QRect(420, 250, 180, 30))
        self.new_nospam.clicked.connect(self.new_no_spam)
        self.copy_pk = QtWidgets.QPushButton(self)
        self.copy_pk.setGeometry(QtCore.QRect(40, 300, 180, 30))
        self.copy_pk.clicked.connect(self.copy_public_key)
        self.new_avatar = QtWidgets.QPushButton(self)
        self.new_avatar.setGeometry(QtCore.QRect(230, 300, 180, 30))
        self.delete_avatar = QtWidgets.QPushButton(self)
        self.delete_avatar.setGeometry(QtCore.QRect(420, 300, 180, 30))
        self.delete_avatar.clicked.connect(self.reset_avatar)
        self.new_avatar.clicked.connect(self.set_avatar)
        self.profilepass = QtWidgets.QLabel(self)
        self.profilepass.setGeometry(QtCore.QRect(40, 340, 300, 30))
        font.setPointSize(18)
        self.profilepass.setFont(font)
        self.password = LineEdit(self)
        self.password.setGeometry(QtCore.QRect(40, 380, 300, 30))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.leave_blank = QtWidgets.QLabel(self)
        self.leave_blank.setGeometry(QtCore.QRect(350, 380, 300, 30))
        self.confirm_password = LineEdit(self)
        self.confirm_password.setGeometry(QtCore.QRect(40, 420, 300, 30))
        self.confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.set_password = QtWidgets.QPushButton(self)
        self.set_password.setGeometry(QtCore.QRect(40, 470, 300, 30))
        self.set_password.clicked.connect(self.new_password)
        self.not_match = QtWidgets.QLabel(self)
        self.not_match.setGeometry(QtCore.QRect(350, 420, 300, 30))
        self.not_match.setVisible(False)
        self.not_match.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.warning = QtWidgets.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(40, 510, 500, 30))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.default = QtWidgets.QPushButton(self)
        self.default.setGeometry(QtCore.QRect(40, 550, 620, 30))
        self._auto = Settings.get_auto_profile() == self._profile_manager.get_path()
        self.default.clicked.connect(self.auto_profile)
        self.retranslateUi()
        if self._profile.status is not None:
            self.status.setCurrentIndex(self._profile.status)
        else:
            self.status.setVisible(False)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.export.setText(util_ui.tr("Export profile"))
        self.setWindowTitle(util_ui.tr("Profile settings"))
        self.label.setText(util_ui.tr("Name:"))
        self.label_2.setText(util_ui.tr("Status:"))
        self.label_3.setText(util_ui.tr("TOX ID:"))
        self.copyId.setText(util_ui.tr("Copy TOX ID"))
        self.new_avatar.setText(util_ui.tr("New avatar"))
        self.delete_avatar.setText(util_ui.tr("Reset avatar"))
        self.new_nospam.setText(util_ui.tr("New NoSpam"))
        self.profilepass.setText(util_ui.tr("Profile password"))
        self.password.setPlaceholderText(util_ui.tr("Password (at least 8 symbols)"))
        self.confirm_password.setPlaceholderText(util_ui.tr("Confirm password"))
        self.set_password.setText(util_ui.tr("Set password"))
        self.not_match.setText(util_ui.tr("Passwords do not match"))
        self.leave_blank.setText(util_ui.tr("Leaving blank will reset current password"))
        self.warning.setText(util_ui.tr("There is no way to recover lost passwords"))
        self.status.addItem(util_ui.tr("Online"))
        self.status.addItem(util_ui.tr("Away"))
        self.status.addItem(util_ui.tr("Busy"))
        self.copy_pk.setText(util_ui.tr("Copy public key"))

        self.set_default_profile_button_text()

    def auto_profile(self):
        if self._auto:
            Settings.reset_auto_profile()
        else:
            Settings.set_auto_profile(self._profile_manager.get_path())
        self._auto = not self._auto
        self.set_default_profile_button_text()

    def set_default_profile_button_text(self):
        if self._auto:
            self.default.setText(util_ui.tr("Mark as not default profile"))
        else:
            self.default.setText(util_ui.tr("Mark as default profile"))

    def new_password(self):
        if self.password.text() == self.confirm_password.text():
            if not len(self.password.text()) or len(self.password.text()) >= 8:
                self._toxes.set_password(self.password.text())
                self.close()
            else:
                self.not_match.setText(
                    util_ui.tr("Password must be at least 8 symbols"))
            self.not_match.setVisible(True)
        else:
            self.not_match.setText(util_ui.tr("Passwords do not match"))
            self.not_match.setVisible(True)

    def copy(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self._profile.tox_id)
        pixmap = QtGui.QPixmap(join_path(get_images_directory(), 'accept.png'))
        icon = QtGui.QIcon(pixmap)
        self.copyId.setIcon(icon)
        self.copyId.setIconSize(QtCore.QSize(10, 10))

    def copy_public_key(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self._profile.tox_id[:64])
        pixmap = QtGui.QPixmap(join_path(get_images_directory(), 'accept.png'))
        icon = QtGui.QIcon(pixmap)
        self.copy_pk.setIcon(icon)
        self.copy_pk.setIconSize(QtCore.QSize(10, 10))

    def new_no_spam(self):
        self.tox_id.setText(self._profile.set_new_nospam())

    def reset_avatar(self):
        self._profile.reset_avatar(self._settings['identicons'])

    def set_avatar(self):
        choose = util_ui.tr("Choose avatar")
        name = util_ui.file_dialog(choose, 'Images (*.png)')
        if name[0]:
            bitmap = QtGui.QPixmap(name[0])
            bitmap.scaled(QtCore.QSize(128, 128), aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                          transformMode=QtCore.Qt.SmoothTransformation)

            byte_array = QtCore.QByteArray()
            buffer = QtCore.QBuffer(byte_array)
            buffer.open(QtCore.QIODevice.WriteOnly)
            bitmap.save(buffer, 'PNG')
            self._profile.set_avatar(bytes(byte_array.data()))

    def export_profile(self):
        directory = util_ui.directory_dialog() + '/'
        if directory != '/':
            reply = util_ui.question(util_ui.tr('Do you want to move your profile to this location?'),
                                     util_ui.tr('Use new path'))
            self._settings.export(directory)
            self._profile.export_db(directory)
            self._profile_manager.export_profile(directory, reply)

    def closeEvent(self, event):
        self._profile.set_name(self.nick.text())
        self._profile.set_status_message(self.status_message.text())
        self._profile.set_status(self.status.currentIndex())


class NetworkSettings(CenteredWidget):
    """Network settings form: UDP, Ipv6 and proxy"""
    def __init__(self, settings, reset):
        super().__init__()
        self._settings = settings
        self._reset = reset
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("NetworkSettings")
        self.resize(300, 400)
        self.setMinimumSize(QtCore.QSize(300, 400))
        self.setMaximumSize(QtCore.QSize(300, 400))
        self.setBaseSize(QtCore.QSize(300, 400))
        self.ipv = QtWidgets.QCheckBox(self)
        self.ipv.setGeometry(QtCore.QRect(20, 10, 97, 22))
        self.ipv.setObjectName("ipv")
        self.udp = QtWidgets.QCheckBox(self)
        self.udp.setGeometry(QtCore.QRect(150, 10, 97, 22))
        self.udp.setObjectName("udp")
        self.proxy = QtWidgets.QCheckBox(self)
        self.proxy.setGeometry(QtCore.QRect(20, 40, 97, 22))
        self.http = QtWidgets.QCheckBox(self)
        self.http.setGeometry(QtCore.QRect(20, 70, 97, 22))
        self.proxy.setObjectName("proxy")
        self.proxyip = LineEdit(self)
        self.proxyip.setGeometry(QtCore.QRect(40, 130, 231, 27))
        self.proxyip.setObjectName("proxyip")
        self.proxyport = LineEdit(self)
        self.proxyport.setGeometry(QtCore.QRect(40, 190, 231, 27))
        self.proxyport.setObjectName("proxyport")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 100, 66, 17))
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 165, 66, 17))
        self.reconnect = QtWidgets.QPushButton(self)
        self.reconnect.setGeometry(QtCore.QRect(40, 230, 231, 30))
        self.reconnect.clicked.connect(self.restart_core)
        self.ipv.setChecked(self._settings['ipv6_enabled'])
        self.udp.setChecked(self._settings['udp_enabled'])
        self.proxy.setChecked(self._settings['proxy_type'])
        self.proxyip.setText(self._settings['proxy_host'])
        self.proxyport.setText(str(self._settings['proxy_port']))
        self.http.setChecked(self._settings['proxy_type'] == 1)
        self.warning = QtWidgets.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(5, 270, 290, 60))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.nodes = QtWidgets.QCheckBox(self)
        self.nodes.setGeometry(QtCore.QRect(20, 350, 270, 22))
        self.nodes.setChecked(self._settings['download_nodes_list'])
        self.retranslateUi()
        self.proxy.stateChanged.connect(lambda x: self.activate())
        self.activate()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(util_ui.tr("Network settings"))
        self.ipv.setText(util_ui.tr("IPv6"))
        self.udp.setText(util_ui.tr("UDP"))
        self.proxy.setText(util_ui.tr("Proxy"))
        self.label.setText(util_ui.tr("IP:"))
        self.label_2.setText(util_ui.tr("Port:"))
        self.reconnect.setText(util_ui.tr("Restart TOX core"))
        self.http.setText(util_ui.tr("HTTP"))
        self.nodes.setText(util_ui.tr("Download nodes list from tox.chat"))
        self.warning.setText(util_ui.tr("WARNING:\nusing proxy with enabled UDP\ncan produce IP leak"))

    def activate(self):
        bl = self.proxy.isChecked()
        self.proxyip.setEnabled(bl)
        self.http.setEnabled(bl)
        self.proxyport.setEnabled(bl)

    def restart_core(self):
        try:
            self._settings['ipv6_enabled'] = self.ipv.isChecked()
            self._settings['udp_enabled'] = self.udp.isChecked()
            self._settings['proxy_type'] = 2 - int(self.http.isChecked()) if self.proxy.isChecked() else 0
            self._settings['proxy_host'] = str(self.proxyip.text())
            self._settings['proxy_port'] = int(self.proxyport.text())
            self._settings['download_nodes_list'] = self.nodes.isChecked()
            self._settings.save()
            # recreate tox instance
            self._reset()
            self.close()
        except Exception as ex:
            log('Exception in restart: ' + str(ex))


class PrivacySettings(CenteredWidget):
    """Privacy settings form: history, typing notifications"""

    def __init__(self, contacts_manager, settings):
        """
        :type contacts_manager: ContactsManager
        """
        super().__init__()
        self._contacts_manager = contacts_manager
        self._settings = settings
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("privacySettings")
        self.resize(370, 600)
        self.setMinimumSize(QtCore.QSize(370, 600))
        self.setMaximumSize(QtCore.QSize(370, 600))
        self.saveHistory = QtWidgets.QCheckBox(self)
        self.saveHistory.setGeometry(QtCore.QRect(10, 20, 350, 22))
        self.saveUnsentOnly = QtWidgets.QCheckBox(self)
        self.saveUnsentOnly.setGeometry(QtCore.QRect(10, 60, 350, 22))

        self.fileautoaccept = QtWidgets.QCheckBox(self)
        self.fileautoaccept.setGeometry(QtCore.QRect(10, 100, 350, 22))

        self.typingNotifications = QtWidgets.QCheckBox(self)
        self.typingNotifications.setGeometry(QtCore.QRect(10, 140, 350, 30))
        self.inlines = QtWidgets.QCheckBox(self)
        self.inlines.setGeometry(QtCore.QRect(10, 180, 350, 30))
        self.auto_path = QtWidgets.QLabel(self)
        self.auto_path.setGeometry(QtCore.QRect(10, 230, 350, 30))
        self.path = QtWidgets.QPlainTextEdit(self)
        self.path.setGeometry(QtCore.QRect(10, 265, 350, 45))
        self.change_path = QtWidgets.QPushButton(self)
        self.change_path.setGeometry(QtCore.QRect(10, 320, 350, 30))
        self.typingNotifications.setChecked(self._settings['typing_notifications'])
        self.fileautoaccept.setChecked(self._settings['allow_auto_accept'])
        self.saveHistory.setChecked(self._settings['save_history'])
        self.inlines.setChecked(self._settings['allow_inline'])
        self.saveUnsentOnly.setChecked(self._settings['save_unsent_only'])
        self.saveUnsentOnly.setEnabled(self._settings['save_history'])
        self.saveHistory.stateChanged.connect(self.update)
        self.path.setPlainText(self._settings['auto_accept_path'] or curr_directory())
        self.change_path.clicked.connect(self.new_path)
        self.block_user_label = QtWidgets.QLabel(self)
        self.block_user_label.setGeometry(QtCore.QRect(10, 360, 350, 30))
        self.block_id = QtWidgets.QPlainTextEdit(self)
        self.block_id.setGeometry(QtCore.QRect(10, 390, 350, 30))
        self.block = QtWidgets.QPushButton(self)
        self.block.setGeometry(QtCore.QRect(10, 430, 350, 30))
        self.block.clicked.connect(lambda: self._contacts_manager.block_user(self.block_id.toPlainText()) or self.close())
        self.blocked_users_label = QtWidgets.QLabel(self)
        self.blocked_users_label.setGeometry(QtCore.QRect(10, 470, 350, 30))
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(10, 500, 350, 30))
        self.comboBox.addItems(self._settings['blocked'])
        self.unblock = QtWidgets.QPushButton(self)
        self.unblock.setGeometry(QtCore.QRect(10, 540, 350, 30))
        self.unblock.clicked.connect(lambda: self.unblock_user())
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(util_ui.tr("Privacy settings"))
        self.saveHistory.setText(util_ui.tr("Save chat history"))
        self.fileautoaccept.setText(util_ui.tr("Allow file auto accept"))
        self.typingNotifications.setText(util_ui.tr("Send typing notifications"))
        self.auto_path.setText(util_ui.tr("Auto accept default path:"))
        self.change_path.setText(util_ui.tr("Change"))
        self.inlines.setText(util_ui.tr("Allow inlines"))
        self.block_user_label.setText(util_ui.tr("Block by public key:"))
        self.blocked_users_label.setText(util_ui.tr("Blocked users:"))
        self.unblock.setText(util_ui.tr("Unblock"))
        self.block.setText(util_ui.tr("Block user"))
        self.saveUnsentOnly.setText(util_ui.tr("Save unsent messages only"))

    def update(self, new_state):
        self.saveUnsentOnly.setEnabled(new_state)
        if not new_state:
            self.saveUnsentOnly.setChecked(False)

    def unblock_user(self):
        if not self.comboBox.count():
            return
        title = util_ui.tr("Add to friend list")
        info = util_ui.tr("Do you want to add this user to friend list?")
        reply = util_ui.question(info, title)
        self._contacts_manager.unblock_user(self.comboBox.currentText(), reply)
        self.close()

    def closeEvent(self, event):
        self._settings['typing_notifications'] = self.typingNotifications.isChecked()
        self._settings['allow_auto_accept'] = self.fileautoaccept.isChecked()
        text = util_ui.tr('History will be cleaned! Continue?')
        title = util_ui.tr('Chat history')

        if self._settings['save_history'] and not self.saveHistory.isChecked():  # clear history
            reply = util_ui.question(text, title)
            if reply:
                self._history_loader.clear_history()
                self._settings['save_history'] = self.saveHistory.isChecked()
        else:
            self._settings['save_history'] = self.saveHistory.isChecked()
        if self.saveUnsentOnly.isChecked() and not self._settings['save_unsent_only']:
            reply = util_ui.question(text, title)
            if reply:
                self._history_loader.clear_history(None, True)
                self._settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        else:
            self._settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        self._settings['auto_accept_path'] = self.path.toPlainText()
        self._settings['allow_inline'] = self.inlines.isChecked()
        self._settings.save()

    def new_path(self):
        directory = util_ui.directory_dialog()
        if directory:
            self.path.setPlainText(directory)


class NotificationsSettings(CenteredWidget):
    """Notifications settings form"""

    def __init__(self, setttings):
        super().__init__()
        self._settings = setttings
        uic.loadUi(get_views_path('notifications_settings_screen'), self)
        self._update_ui()
        self.center()

    def closeEvent(self, *args, **kwargs):
        self._settings['notifications'] = self.notificationsCheckBox.isChecked()
        self._settings['sound_notifications'] = self.soundNotificationsCheckBox.isChecked()
        self._settings['group_notifications'] = self.groupNotificationsCheckBox.isChecked()
        self._settings['calls_sound'] = self.callsSoundCheckBox.isChecked()
        self._settings.save()

    def _update_ui(self):
        self.notificationsCheckBox.setChecked(self._settings['notifications'])
        self.soundNotificationsCheckBox.setChecked(self._settings['sound_notifications'])
        self.groupNotificationsCheckBox.setChecked(self._settings['group_notifications'])
        self.callsSoundCheckBox.setChecked(self._settings['calls_sound'])
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Notifications settings"))
        self.notificationsCheckBox.setText(util_ui.tr("Enable notifications"))
        self.groupNotificationsCheckBox.setText(util_ui.tr("Notify about all messages in groups"))
        self.callsSoundCheckBox.setText(util_ui.tr("Enable call\'s sound"))
        self.soundNotificationsCheckBox.setText(util_ui.tr("Enable sound notifications"))


class InterfaceSettings(CenteredWidget):
    """Interface settings form"""
    def __init__(self, settings, smiley_loader):
        super().__init__()
        self._settings = settings
        self._smiley_loader = smiley_loader
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("interfaceForm")
        self.setMinimumSize(QtCore.QSize(400, 650))
        self.setMaximumSize(QtCore.QSize(400, 650))
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 10, 370, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setFamily(self._settings['font'])
        self.label.setFont(font)
        self.themeSelect = QtWidgets.QComboBox(self)
        self.themeSelect.setGeometry(QtCore.QRect(30, 40, 120, 30))
        self.themeSelect.addItems(list(self._settings.built_in_themes().keys()))
        theme = self._settings['theme']
        if theme in self._settings.built_in_themes().keys():
            index = list(self._settings.built_in_themes().keys()).index(theme)
        else:
            index = 0
        self.themeSelect.setCurrentIndex(index)
        self.lang_choose = QtWidgets.QComboBox(self)
        self.lang_choose.setGeometry(QtCore.QRect(30, 110, 120, 30))
        supported = sorted(Settings.supported_languages().keys(), reverse=True)
        for key in supported:
            self.lang_choose.insertItem(0, key)
            if self._settings['language'] == key:
                self.lang_choose.setCurrentIndex(0)
        self.lang = QtWidgets.QLabel(self)
        self.lang.setGeometry(QtCore.QRect(30, 80, 370, 20))
        self.lang.setFont(font)
        self.mirror_mode = QtWidgets.QCheckBox(self)
        self.mirror_mode.setGeometry(QtCore.QRect(30, 160, 370, 20))
        self.mirror_mode.setChecked(self._settings['mirror_mode'])
        self.smileys = QtWidgets.QCheckBox(self)
        self.smileys.setGeometry(QtCore.QRect(30, 190, 120, 20))
        self.smileys.setChecked(self._settings['smileys'])
        self.smiley_pack_label = QtWidgets.QLabel(self)
        self.smiley_pack_label.setGeometry(QtCore.QRect(30, 230, 370, 20))
        self.smiley_pack_label.setFont(font)
        self.smiley_pack = QtWidgets.QComboBox(self)
        self.smiley_pack.setGeometry(QtCore.QRect(30, 260, 160, 30))
        self.smiley_pack.addItems(self._smiley_loader.get_packs_list())
        try:
            ind = self._smiley_loader.get_packs_list().index(self._settings['smiley_pack'])
        except:
            ind = self._smiley_loader.get_packs_list().index('default')
        self.smiley_pack.setCurrentIndex(ind)
        self.messages_font_size_label = QtWidgets.QLabel(self)
        self.messages_font_size_label.setGeometry(QtCore.QRect(30, 300, 370, 20))
        self.messages_font_size_label.setFont(font)
        self.messages_font_size = QtWidgets.QComboBox(self)
        self.messages_font_size.setGeometry(QtCore.QRect(30, 330, 160, 30))
        self.messages_font_size.addItems([str(x) for x in range(10, 25)])
        self.messages_font_size.setCurrentIndex(self._settings['message_font_size'] - 10)

        self.unread = QtWidgets.QPushButton(self)
        self.unread.setGeometry(QtCore.QRect(30, 470, 340, 30))
        self.unread.clicked.connect(self.select_color)

        self.compact_mode = QtWidgets.QCheckBox(self)
        self.compact_mode.setGeometry(QtCore.QRect(30, 380, 370, 20))
        self.compact_mode.setChecked(self._settings['compact_mode'])

        self.close_to_tray = QtWidgets.QCheckBox(self)
        self.close_to_tray.setGeometry(QtCore.QRect(30, 410, 370, 20))
        self.close_to_tray.setChecked(self._settings['close_to_tray'])

        self.show_avatars = QtWidgets.QCheckBox(self)
        self.show_avatars.setGeometry(QtCore.QRect(30, 440, 370, 20))
        self.show_avatars.setChecked(self._settings['show_avatars'])

        self.choose_font = QtWidgets.QPushButton(self)
        self.choose_font.setGeometry(QtCore.QRect(30, 510, 340, 30))
        self.choose_font.clicked.connect(self.new_font)

        self.import_smileys = QtWidgets.QPushButton(self)
        self.import_smileys.setGeometry(QtCore.QRect(30, 550, 340, 30))
        self.import_smileys.clicked.connect(self.import_sm)

        self.import_stickers = QtWidgets.QPushButton(self)
        self.import_stickers.setGeometry(QtCore.QRect(30, 590, 340, 30))
        self.import_stickers.clicked.connect(self.import_st)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.show_avatars.setText(util_ui.tr("Show avatars in chat"))
        self.setWindowTitle(util_ui.tr("Interface settings"))
        self.label.setText(util_ui.tr("Theme:"))
        self.lang.setText(util_ui.tr("Language:"))
        self.smileys.setText(util_ui.tr("Smileys"))
        self.smiley_pack_label.setText(util_ui.tr("Smiley pack:"))
        self.mirror_mode.setText(util_ui.tr("Mirror mode"))
        self.messages_font_size_label.setText(util_ui.tr("Messages font size:"))
        self.unread.setText(util_ui.tr("Select unread messages notification color"))
        self.compact_mode.setText(util_ui.tr("Compact contact list"))
        self.import_smileys.setText(util_ui.tr("Import smiley pack"))
        self.import_stickers.setText(util_ui.tr("Import sticker pack"))
        self.close_to_tray.setText(util_ui.tr("Close to tray"))
        self.choose_font.setText(util_ui.tr("Select font"))

    def import_st(self):
        directory = util_ui.directory_dialog(util_ui.tr('Choose folder with sticker pack'))
        if directory:
            dest = join_path(get_stickers_directory(), os.path.basename(directory))
            copy(directory, dest)

    def import_sm(self):
        directory = util_ui.directory_dialog(util_ui.tr('Choose folder with smiley pack'))
        if directory:
            src = directory + '/'
            dest = curr_directory() + '/smileys/' + os.path.basename(directory) + '/'
            copy(src, dest)

    def new_font(self):
        font, ok = QtWidgets.QFontDialog.getFont(QtGui.QFont(self._settings['font'], 10), self)
        if ok:
            self._settings['font'] = font.family()
            self._settings.save()
            util_ui.question()
            msgBox = QtWidgets.QMessageBox()
            text = util_ui.tr('Restart app to apply settings')
            msgBox.setWindowTitle(util_ui.tr('Restart required'))
            msgBox.setText(text)
            msgBox.exec_()

    def select_color(self):
        col = QtWidgets.QColorDialog.getColor(QtGui.QColor(self._settings['unread_color']))

        if col.isValid():
            name = col.name()
            self._settings['unread_color'] = name
            self._settings.save()

    def closeEvent(self, event):
        self._settings['theme'] = str(self.themeSelect.currentText())
        try:
            theme = self._settings['theme']
            app = QtWidgets.QApplication.instance()
            with open(curr_directory() + self._settings.built_in_themes()[theme]) as fl:
                style = fl.read()
            app.setStyleSheet(style)
        except IsADirectoryError:
            app.setStyleSheet('') # for default style
            self._settings['smileys'] = self.smileys.isChecked()
        restart = False
        if self._settings['mirror_mode'] != self.mirror_mode.isChecked():
            self._settings['mirror_mode'] = self.mirror_mode.isChecked()
            restart = True
        if self._settings['compact_mode'] != self.compact_mode.isChecked():
            self._settings['compact_mode'] = self.compact_mode.isChecked()
            restart = True
        if self._settings['show_avatars'] != self.show_avatars.isChecked():
            self._settings['show_avatars'] = self.show_avatars.isChecked()
            restart = True
        self._settings['smiley_pack'] = self.smiley_pack.currentText()
        self._settings['close_to_tray'] = self.close_to_tray.isChecked()
        smileys.SmileyLoader.get_instance().load_pack()
        language = self.lang_choose.currentText()
        if self._settings['language'] != language:
            self._settings['language'] = language
            text = self.lang_choose.currentText()
            path = Settings.supported_languages()[text]
            app = QtWidgets.QApplication.instance()
            app.removeTranslator(app.translator)
            app.translator.load(curr_directory() + '/translations/' + path)
            app.installTranslator(app.translator)
        self._settings['message_font_size'] = self.messages_font_size.currentIndex() + 10
        self._settings.save()
        if restart:
            util_ui.message_box(util_ui.tr('Restart app to apply settings'), util_ui.tr('Restart required'))


class AudioSettings(CenteredWidget):
    """
    Audio calls settings form
    """

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self._in_indexes = self._out_indexes = None
        uic.loadUi(get_views_path('audio_settings_screen'), self)
        self._update_ui()
        self.center()

    def closeEvent(self, event):
        self._settings.audio['input'] = self._in_indexes[self.inputDeviceComboBox.currentIndex()]
        self._settings.audio['output'] = self._out_indexes[self.outputDeviceComboBox.currentIndex()]
        self._settings.save()

    def _update_ui(self):
        p = pyaudio.PyAudio()
        self._in_indexes, self._out_indexes = [], []
        for i in range(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            if device["maxInputChannels"]:
                self.inputDeviceComboBox.addItem(str(device["name"]))
                self._in_indexes.append(i)
            if device["maxOutputChannels"]:
                self.outputDeviceComboBox.addItem(str(device["name"]))
                self._out_indexes.append(i)
        self.inputDeviceComboBox.setCurrentIndex(self._in_indexes.index(self._settings.audio['input']))
        self.outputDeviceComboBox.setCurrentIndex(self._out_indexes.index(self._settings.audio['output']))
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Audio settings"))
        self.inputDeviceLabel.setText(util_ui.tr("Input device:"))
        self.outputDeviceLabel.setText(util_ui.tr("Output device:"))


class DesktopAreaSelectionWindow(RubberBandWindow):

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            width, height = rect.width(), rect.height()
            if width >= 8 and height >= 8:
                self.parent.save(rect.x(), rect.y(), width - (width % 4), height - (height % 4))
            self.close()


class VideoSettings(CenteredWidget):
    """
    Audio calls settings form
    """

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        uic.loadUi(get_views_path('video_settings_screen'), self)
        self._devices = self._frame_max_sizes = None
        self._update_ui()
        self.center()
        self.desktopAreaSelection = None

    def closeEvent(self, event):
        if self.deviceComboBox.currentIndex() == 0:
            return
        try:
            self._settings.video['device'] = self.devices[self.input.currentIndex()]
            text = self.resolutionComboBox.currentText()
            self._settings.video['width'] = int(text.split(' ')[0])
            self._settings.video['height'] = int(text.split(' ')[-1])
            self._settings.save()
        except Exception as ex:
            print('Saving video  settings error: ' + str(ex))

    def save(self, x, y, width, height):
        self.desktopAreaSelection = None
        self._settings.video['device'] = -1
        self._settings.video['width'] = width
        self._settings.video['height'] = height
        self._settings.video['x'] = x
        self._settings.video['y'] = y
        self._settings.save()

    def _update_ui(self):
        self.deviceComboBox.currentIndexChanged.connect(self._device_changed)
        self.selectRegionPushButton.clicked.connect(self._button_clicked)
        self._devices = [-1]
        screen = QtWidgets.QApplication.primaryScreen()
        size = screen.size()
        self._frame_max_sizes = [(size.width(), size.height())]
        desktop = util_ui.tr("Desktop")
        self.deviceComboBox.addItem(desktop)
        for i in range(10):
            v = cv2.VideoCapture(i)
            if v.isOpened():
                v.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
                v.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

                width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
                del v
                self._devices.append(i)
                self._frame_max_sizes.append((width, height))
                self.deviceComboBox.addItem(util_ui.tr('Device #') + str(i))
        try:
            index = self._devices.index(self._settings.video['device'])
            self.deviceComboBox.setCurrentIndex(index)
        except:
            print('Video devices error!')
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Video settings"))
        self.deviceLabel.setText(util_ui.tr("Device:"))
        self.selectRegionPushButton.setText(util_ui.tr("Select region"))

    def _button_clicked(self):
        self.desktopAreaSelection = DesktopAreaSelectionWindow(self)

    def _device_changed(self):
        index = self.deviceComboBox.currentIndex()
        self.selectRegionPushButton.setVisible(index == 0)
        self.resolutionComboBox.setVisible(index != 0)
        width, height = self._frame_max_sizes[index]
        self.resolutionComboBox.clear()
        dims = [
            (320, 240),
            (640, 360),
            (640, 480),
            (720, 480),
            (1280, 720),
            (1920, 1080),
            (2560, 1440)
        ]
        for w, h in dims:
            if w <= width and h <= height:
                self.resolutionComboBox.addItem(str(w) + ' * ' + str(h))


class PluginsSettings(CenteredWidget):
    """
    Plugins settings form
    """

    def __init__(self, plugin_loader):
        super().__init__()
        self._plugin_loader = plugin_loader
        self._window = None
        self.initUI()
        self.center()
        self.retranslateUi()

    def initUI(self):
        self.resize(400, 210)
        self.setMinimumSize(QtCore.QSize(400, 210))
        self.setMaximumSize(QtCore.QSize(400, 210))
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(30, 10, 340, 30))
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 40, 340, 90))
        self.label.setWordWrap(True)
        self.button = QtWidgets.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(30, 130, 340, 30))
        self.button.clicked.connect(self.button_click)
        self.open = QtWidgets.QPushButton(self)
        self.open.setGeometry(QtCore.QRect(30, 170, 340, 30))
        self.open.clicked.connect(self.open_plugin)
        self.update_list()
        self.comboBox.currentIndexChanged.connect(self.show_data)
        self.show_data()

    def retranslateUi(self):
        self.setWindowTitle(util_ui.tr("Plugins"))
        self.open.setText(util_ui.tr("Open selected plugin"))

    def open_plugin(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        window = self.pl_loader.plugin_window(plugin[-1])
        if window is not None:
            self._window = window
            self._window.show()
        else:
            util_ui.message_box(util_ui.tr('No GUI found for this plugin'), util_ui.tr('Error'))

    def update_list(self):
        self.comboBox.clear()
        data = self._plugin_loader.get_plugins_list()
        self.comboBox.addItems(list(map(lambda x: x[0], data)))
        self.data = data

    def show_data(self):
        ind = self.comboBox.currentIndex()
        if len(self.data):
            plugin = self.data[ind]
            descr = plugin[2] or util_ui.tr("No description available")
            self.label.setText(descr)
            if plugin[1]:
                self.button.setText(util_ui.tr("Disable plugin"))
            else:
                self.button.setText(util_ui.tr("Enable plugin"))
        else:
            self.open.setVisible(False)
            self.button.setVisible(False)
            self.label.setText(util_ui.tr("No plugins found"))

    def button_click(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        self._plugin_loader.toggle_plugin(plugin[-1])
        plugin[1] = not plugin[1]
        if plugin[1]:
            self.button.setText(util_ui.tr("Disable plugin"))
        else:
            self.button.setText(util_ui.tr("Enable plugin"))


class UpdateSettings(CenteredWidget):
    """
    Updates settings form
    """

    def __init__(self, settings, version):
        super().__init__()
        self._settings = settings
        self._version = version
        uic.loadUi(get_views_path('update_settings_screen'), self)
        self._update_ui()
        self.center()

    def closeEvent(self, event):
        self._settings['update'] = self.updateModeComboBox.currentIndex()
        self._settings.save()

    def _update_ui(self):
        self.updatePushButton.clicked.connect(self._update_client)
        self.updateModeComboBox.currentIndexChanged.connect(self._update_mode_changed)
        self._retranslate_ui()
        self.updateModeComboBox.setCurrentIndex(self._settings['update'])

    def _update_mode_changed(self):
        index = self.updateModeComboBox.currentIndex()
        self.updatePushButton.setEnabled(index > 0)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Update settings"))
        self.updateModeLabel.setText(util_ui.tr("Select update mode:"))
        self.updatePushButton.setText(util_ui.tr("Update Toxygen"))
        self.updateModeComboBox.addItem(util_ui.tr("Disabled"))
        self.updateModeComboBox.addItem(util_ui.tr("Manual"))
        self.updateModeComboBox.addItem(util_ui.tr("Auto"))

    def _update_client(self):
        if not updater.connection_available():
            util_ui.message_box(util_ui.tr('Problems with internet connection'), util_ui.tr("Error"))
            return
        if not updater.updater_available():
            util_ui.message_box(util_ui.tr('Updater not found'), util_ui.tr("Error"))
            return
        version = updater.check_for_updates(self._version, self._settings)
        if version is not None:
            updater.download(version)
            util_ui.close_all_windows()
        else:
            util_ui.message_box(util_ui.tr('Toxygen is up to date'), util_ui.tr("No updates found"))
