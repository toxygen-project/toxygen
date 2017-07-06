from PyQt5 import QtCore, QtGui, QtWidgets
from settings import *
from profile import Profile
from util import curr_directory, copy
from widgets import CenteredWidget, DataLabel, LineEdit
import pyaudio
import toxes
import plugin_support
import updater


class AddContact(CenteredWidget):
    """Add contact form"""

    def __init__(self, tox_id=''):
        super(AddContact, self).__init__()
        self.initUI(tox_id)
        self._adding = False

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
        font.setFamily(Settings.get_instance()['font'])
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
        profile = Profile.get_instance()
        send = profile.send_friend_request(self.tox_id.text().strip(), self.message_edit.toPlainText())
        self._adding = False
        if send is True:
            # request was successful
            self.close()
        else:  # print error data
            self.error_label.setText(send)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate('AddContact', "Add contact"))
        self.sendRequestButton.setText(QtWidgets.QApplication.translate("Form", "Send request"))
        self.label.setText(QtWidgets.QApplication.translate('AddContact', "TOX ID:"))
        self.message.setText(QtWidgets.QApplication.translate('AddContact', "Message:"))
        self.tox_id.setPlaceholderText(QtWidgets.QApplication.translate('AddContact', "TOX ID or public key of contact"))


class ProfileSettings(CenteredWidget):
    """Form with profile settings such as name, status, TOX ID"""
    def __init__(self):
        super(ProfileSettings, self).__init__()
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("ProfileSettingsForm")
        self.setMinimumSize(QtCore.QSize(700, 600))
        self.setMaximumSize(QtCore.QSize(700, 600))
        self.nick = LineEdit(self)
        self.nick.setGeometry(QtCore.QRect(30, 60, 350, 27))
        profile = Profile.get_instance()
        self.nick.setText(profile.name)
        self.status = QtWidgets.QComboBox(self)
        self.status.setGeometry(QtCore.QRect(400, 60, 200, 27))
        self.status_message = LineEdit(self)
        self.status_message.setGeometry(QtCore.QRect(30, 130, 350, 27))
        self.status_message.setText(profile.status_message)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 30, 91, 25))
        font = QtGui.QFont()
        font.setFamily(Settings.get_instance()['font'])
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
        s = profile.tox_id
        self.tox_id.setText(s)
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
        path, name = Settings.get_auto_profile()
        self.auto = path + name == ProfileHelper.get_path() + Settings.get_instance().name
        self.default.clicked.connect(self.auto_profile)
        self.retranslateUi()
        if profile.status is not None:
            self.status.setCurrentIndex(profile.status)
        else:
            self.status.setVisible(False)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.export.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Export profile"))
        self.setWindowTitle(QtWidgets.QApplication.translate("ProfileSettingsForm", "Profile settings"))
        self.label.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Name:"))
        self.label_2.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Status:"))
        self.label_3.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "TOX ID:"))
        self.copyId.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Copy TOX ID"))
        self.new_avatar.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "New avatar"))
        self.delete_avatar.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Reset avatar"))
        self.new_nospam.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "New NoSpam"))
        self.profilepass.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Profile password"))
        self.password.setPlaceholderText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Password (at least 8 symbols)"))
        self.confirm_password.setPlaceholderText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Confirm password"))
        self.set_password.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Set password"))
        self.not_match.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Passwords do not match"))
        self.leave_blank.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Leaving blank will reset current password"))
        self.warning.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "There is no way to recover lost passwords"))
        self.status.addItem(QtWidgets.QApplication.translate("ProfileSettingsForm", "Online"))
        self.status.addItem(QtWidgets.QApplication.translate("ProfileSettingsForm", "Away"))
        self.status.addItem(QtWidgets.QApplication.translate("ProfileSettingsForm", "Busy"))
        self.copy_pk.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Copy public key"))
        if self.auto:
            self.default.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Mark as not default profile"))
        else:
            self.default.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Mark as default profile"))

    def auto_profile(self):
        if self.auto:
            Settings.reset_auto_profile()
        else:
            Settings.set_auto_profile(ProfileHelper.get_path(), Settings.get_instance().name)
        self.auto = not self.auto
        if self.auto:
            self.default.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Mark as not default profile"))
        else:
            self.default.setText(
                QtWidgets.QApplication.translate("ProfileSettingsForm", "Mark as default profile"))

    def new_password(self):
        if self.password.text() == self.confirm_password.text():
            if not len(self.password.text()) or len(self.password.text()) >= 8:
                e = toxes.ToxES.get_instance()
                e.set_password(self.password.text())
                self.close()
            else:
                self.not_match.setText(
                    QtWidgets.QApplication.translate("ProfileSettingsForm", "Password must be at least 8 symbols"))
            self.not_match.setVisible(True)
        else:
            self.not_match.setText(QtWidgets.QApplication.translate("ProfileSettingsForm", "Passwords do not match"))
            self.not_match.setVisible(True)

    def copy(self):
        clipboard = QtWidgets.QApplication.clipboard()
        profile = Profile.get_instance()
        clipboard.setText(profile.tox_id)
        pixmap = QtGui.QPixmap(curr_directory() + '/images/accept.png')
        icon = QtGui.QIcon(pixmap)
        self.copyId.setIcon(icon)
        self.copyId.setIconSize(QtCore.QSize(10, 10))

    def copy_public_key(self):
        clipboard = QtWidgets.QApplication.clipboard()
        profile = Profile.get_instance()
        clipboard.setText(profile.tox_id[:64])
        pixmap = QtGui.QPixmap(curr_directory() + '/images/accept.png')
        icon = QtGui.QIcon(pixmap)
        self.copy_pk.setIcon(icon)
        self.copy_pk.setIconSize(QtCore.QSize(10, 10))

    def new_no_spam(self):
        self.tox_id.setText(Profile.get_instance().new_nospam())

    def reset_avatar(self):
        Profile.get_instance().reset_avatar()

    def set_avatar(self):
        choose = QtWidgets.QApplication.translate("ProfileSettingsForm", "Choose avatar")
        name = QtWidgets.QFileDialog.getOpenFileName(self, choose, None, 'Images (*.png)',
                                                     QtGui.QComboBoxQtWidgets.QFileDialog.DontUseNativeDialog)
        if name[0]:
            bitmap = QtGui.QPixmap(name[0])
            bitmap.scaled(QtCore.QSize(128, 128), aspectMode=QtCore.Qt.KeepAspectRatio,
                          mode=QtCore.Qt.SmoothTransformation)

            byte_array = QtCore.QByteArray()
            buffer = QtCore.QBuffer(byte_array)
            buffer.open(QtCore.QIODevice.WriteOnly)
            bitmap.save(buffer, 'PNG')
            Profile.get_instance().set_avatar(bytes(byte_array.data()))

    def export_profile(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(options=QtWidgets.QFileDialog.DontUseNativeDialog,
                                                           dir=curr_directory()) + '/'
        if directory != '/':
            reply = QtWidgets.QMessageBox.question(None,
                                               QtWidgets.QApplication.translate("ProfileSettingsForm",
                                                                            'Use new path'),
                                               QtWidgets.QApplication.translate("ProfileSettingsForm",
                                                                            'Do you want to move your profile to this location?'),
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            settings = Settings.get_instance()
            settings.export(directory)
            profile = Profile.get_instance()
            profile.export_db(directory)
            ProfileHelper.get_instance().export_profile(directory, reply == QtWidgets.QMessageBox.Yes)

    def closeEvent(self, event):
        profile = Profile.get_instance()
        profile.set_name(self.nick.text())
        profile.set_status_message(self.status_message.text().encode('utf-8'))
        profile.set_status(self.status.currentIndex())


class NetworkSettings(CenteredWidget):
    """Network settings form: UDP, Ipv6 and proxy"""
    def __init__(self, reset):
        super(NetworkSettings, self).__init__()
        self.reset = reset
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("NetworkSettings")
        self.resize(300, 330)
        self.setMinimumSize(QtCore.QSize(300, 330))
        self.setMaximumSize(QtCore.QSize(300, 330))
        self.setBaseSize(QtCore.QSize(300, 330))
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
        settings = Settings.get_instance()
        self.ipv.setChecked(settings['ipv6_enabled'])
        self.udp.setChecked(settings['udp_enabled'])
        self.proxy.setChecked(settings['proxy_type'])
        self.proxyip.setText(settings['proxy_host'])
        self.proxyport.setText(str(settings['proxy_port']))
        self.http.setChecked(settings['proxy_type'] == 1)
        self.warning = QtWidgets.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(5, 270, 290, 60))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.retranslateUi()
        self.proxy.stateChanged.connect(lambda x: self.activate())
        self.activate()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("NetworkSettings", "Network settings"))
        self.ipv.setText(QtWidgets.QApplication.translate("Form", "IPv6"))
        self.udp.setText(QtWidgets.QApplication.translate("Form", "UDP"))
        self.proxy.setText(QtWidgets.QApplication.translate("Form", "Proxy"))
        self.label.setText(QtWidgets.QApplication.translate("Form", "IP:"))
        self.label_2.setText(QtWidgets.QApplication.translate("Form", "Port:"))
        self.reconnect.setText(QtWidgets.QApplication.translate("NetworkSettings", "Restart TOX core"))
        self.http.setText(QtWidgets.QApplication.translate("Form", "HTTP"))
        self.warning.setText(QtWidgets.QApplication.translate("Form", "WARNING:\nusing proxy with enabled UDP\ncan produce IP leak"))

    def activate(self):
        bl = self.proxy.isChecked()
        self.proxyip.setEnabled(bl)
        self.http.setEnabled(bl)
        self.proxyport.setEnabled(bl)

    def restart_core(self):
        try:
            settings = Settings.get_instance()
            settings['ipv6_enabled'] = self.ipv.isChecked()
            settings['udp_enabled'] = self.udp.isChecked()
            settings['proxy_type'] = 2 - int(self.http.isChecked()) if self.proxy.isChecked() else 0
            settings['proxy_host'] = str(self.proxyip.text())
            settings['proxy_port'] = int(self.proxyport.text())
            settings.save()
            # recreate tox instance
            Profile.get_instance().reset(self.reset)
            self.close()
        except Exception as ex:
            log('Exception in restart: ' + str(ex))


class PrivacySettings(CenteredWidget):
    """Privacy settings form: history, typing notifications"""

    def __init__(self):
        super(PrivacySettings, self).__init__()
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
        settings = Settings.get_instance()
        self.typingNotifications.setChecked(settings['typing_notifications'])
        self.fileautoaccept.setChecked(settings['allow_auto_accept'])
        self.saveHistory.setChecked(settings['save_history'])
        self.inlines.setChecked(settings['allow_inline'])
        self.saveUnsentOnly.setChecked(settings['save_unsent_only'])
        self.saveUnsentOnly.setEnabled(settings['save_history'])
        self.saveHistory.stateChanged.connect(self.update)
        self.path.setPlainText(settings['auto_accept_path'] or curr_directory())
        self.change_path.clicked.connect(self.new_path)
        self.block_user_label = QtWidgets.QLabel(self)
        self.block_user_label.setGeometry(QtCore.QRect(10, 360, 350, 30))
        self.block_id = QtWidgets.QPlainTextEdit(self)
        self.block_id.setGeometry(QtCore.QRect(10, 390, 350, 30))
        self.block = QtWidgets.QPushButton(self)
        self.block.setGeometry(QtCore.QRect(10, 430, 350, 30))
        self.block.clicked.connect(lambda: Profile.get_instance().block_user(self.block_id.toPlainText()) or self.close())
        self.blocked_users_label = QtWidgets.QLabel(self)
        self.blocked_users_label.setGeometry(QtCore.QRect(10, 470, 350, 30))
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(10, 500, 350, 30))
        self.comboBox.addItems(settings['blocked'])
        self.unblock = QtWidgets.QPushButton(self)
        self.unblock.setGeometry(QtCore.QRect(10, 540, 350, 30))
        self.unblock.clicked.connect(lambda: self.unblock_user())
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("privacySettings", "Privacy settings"))
        self.saveHistory.setText(QtWidgets.QApplication.translate("privacySettings", "Save chat history"))
        self.fileautoaccept.setText(QtWidgets.QApplication.translate("privacySettings", "Allow file auto accept"))
        self.typingNotifications.setText(QtWidgets.QApplication.translate("privacySettings", "Send typing notifications"))
        self.auto_path.setText(QtWidgets.QApplication.translate("privacySettings", "Auto accept default path:"))
        self.change_path.setText(QtWidgets.QApplication.translate("privacySettings", "Change"))
        self.inlines.setText(QtWidgets.QApplication.translate("privacySettings", "Allow inlines"))
        self.block_user_label.setText(QtWidgets.QApplication.translate("privacySettings", "Block by public key:"))
        self.blocked_users_label.setText(QtWidgets.QApplication.translate("privacySettings", "Blocked users:"))
        self.unblock.setText(QtWidgets.QApplication.translate("privacySettings", "Unblock"))
        self.block.setText(QtWidgets.QApplication.translate("privacySettings", "Block user"))
        self.saveUnsentOnly.setText(QtWidgets.QApplication.translate("privacySettings", "Save unsent messages only"))

    def update(self, new_state):
        self.saveUnsentOnly.setEnabled(new_state)
        if not new_state:
            self.saveUnsentOnly.setChecked(False)

    def unblock_user(self):
        if not self.comboBox.count():
            return
        title = QtWidgets.QApplication.translate("privacySettings", "Add to friend list")
        info = QtWidgets.QApplication.translate("privacySettings", "Do you want to add this user to friend list?")
        reply = QtWidgets.QMessageBox.question(None, title, info, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        Profile.get_instance().unblock_user(self.comboBox.currentText(), reply == QtWidgets.QMessageBox.Yes)
        self.close()

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['typing_notifications'] = self.typingNotifications.isChecked()
        settings['allow_auto_accept'] = self.fileautoaccept.isChecked()

        if settings['save_history'] and not self.saveHistory.isChecked():  # clear history
            reply = QtWidgets.QMessageBox.question(None,
                                               QtWidgets.QApplication.translate("privacySettings",
                                                                            'Chat history'),
                                               QtWidgets.QApplication.translate("privacySettings",
                                                                            'History will be cleaned! Continue?'),
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                Profile.get_instance().clear_history()
                settings['save_history'] = self.saveHistory.isChecked()
        else:
            settings['save_history'] = self.saveHistory.isChecked()
        if self.saveUnsentOnly.isChecked() and not settings['save_unsent_only']:
            reply = QtWidgets.QMessageBox.question(None,
                                               QtWidgets.QApplication.translate("privacySettings",
                                                                            'Chat history'),
                                               QtWidgets.QApplication.translate("privacySettings",
                                                                            'History will be cleaned! Continue?'),
                                               QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                Profile.get_instance().clear_history(None, True)
                settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        else:
            settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        settings['auto_accept_path'] = self.path.toPlainText()
        settings['allow_inline'] = self.inlines.isChecked()
        settings.save()

    def new_path(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(options=QtWidgets.QFileDialog.DontUseNativeDialog) + '/'
        if directory != '/':
            self.path.setPlainText(directory)


class NotificationsSettings(CenteredWidget):
    """Notifications settings form"""

    def __init__(self):
        super(NotificationsSettings, self).__init__()
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("notificationsForm")
        self.resize(350, 180)
        self.setMinimumSize(QtCore.QSize(350, 180))
        self.setMaximumSize(QtCore.QSize(350, 180))
        self.enableNotifications = QtWidgets.QCheckBox(self)
        self.enableNotifications.setGeometry(QtCore.QRect(10, 20, 340, 18))
        self.callsSound = QtWidgets.QCheckBox(self)
        self.callsSound.setGeometry(QtCore.QRect(10, 120, 340, 18))
        self.soundNotifications = QtWidgets.QCheckBox(self)
        self.soundNotifications.setGeometry(QtCore.QRect(10, 70, 340, 18))
        font = QtGui.QFont()
        s = Settings.get_instance()
        font.setFamily(s['font'])
        font.setPointSize(12)
        self.callsSound.setFont(font)
        self.soundNotifications.setFont(font)
        self.enableNotifications.setFont(font)
        self.enableNotifications.setChecked(s['notifications'])
        self.soundNotifications.setChecked(s['sound_notifications'])
        self.callsSound.setChecked(s['calls_sound'])
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("notificationsForm", "Notification settings"))
        self.enableNotifications.setText(QtWidgets.QApplication.translate("notificationsForm", "Enable notifications"))
        self.callsSound.setText(QtWidgets.QApplication.translate("notificationsForm", "Enable call\'s sound"))
        self.soundNotifications.setText(QtWidgets.QApplication.translate("notificationsForm", "Enable sound notifications"))

    def closeEvent(self, *args, **kwargs):
        settings = Settings.get_instance()
        settings['notifications'] = self.enableNotifications.isChecked()
        settings['sound_notifications'] = self.soundNotifications.isChecked()
        settings['calls_sound'] = self.callsSound.isChecked()
        settings.save()


class InterfaceSettings(CenteredWidget):
    """Interface settings form"""
    def __init__(self):
        super(InterfaceSettings, self).__init__()
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("interfaceForm")
        self.setMinimumSize(QtCore.QSize(400, 650))
        self.setMaximumSize(QtCore.QSize(400, 650))
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 10, 370, 20))
        settings = Settings.get_instance()
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setFamily(settings['font'])
        self.label.setFont(font)
        self.themeSelect = QtWidgets.QComboBox(self)
        self.themeSelect.setGeometry(QtCore.QRect(30, 40, 120, 30))
        self.themeSelect.addItems(list(settings.built_in_themes().keys()))
        theme = settings['theme']
        if theme in settings.built_in_themes().keys():
            index = list(settings.built_in_themes().keys()).index(theme)
        else:
            index = 0
        self.themeSelect.setCurrentIndex(index)
        self.lang_choose = QtWidgets.QComboBox(self)
        self.lang_choose.setGeometry(QtCore.QRect(30, 110, 120, 30))
        supported = sorted(Settings.supported_languages().keys(), reverse=True)
        for key in supported:
            self.lang_choose.insertItem(0, key)
            if settings['language'] == key:
                self.lang_choose.setCurrentIndex(0)
        self.lang = QtWidgets.QLabel(self)
        self.lang.setGeometry(QtCore.QRect(30, 80, 370, 20))
        self.lang.setFont(font)
        self.mirror_mode = QtWidgets.QCheckBox(self)
        self.mirror_mode.setGeometry(QtCore.QRect(30, 160, 370, 20))
        self.mirror_mode.setChecked(settings['mirror_mode'])
        self.smileys = QtWidgets.QCheckBox(self)
        self.smileys.setGeometry(QtCore.QRect(30, 190, 120, 20))
        self.smileys.setChecked(settings['smileys'])
        self.smiley_pack_label = QtWidgets.QLabel(self)
        self.smiley_pack_label.setGeometry(QtCore.QRect(30, 230, 370, 20))
        self.smiley_pack_label.setFont(font)
        self.smiley_pack = QtWidgets.QComboBox(self)
        self.smiley_pack.setGeometry(QtCore.QRect(30, 260, 160, 30))
        sm = smileys.SmileyLoader.get_instance()
        self.smiley_pack.addItems(sm.get_packs_list())
        try:
            ind = sm.get_packs_list().index(settings['smiley_pack'])
        except:
            ind = sm.get_packs_list().index('default')
        self.smiley_pack.setCurrentIndex(ind)
        self.messages_font_size_label = QtWidgets.QLabel(self)
        self.messages_font_size_label.setGeometry(QtCore.QRect(30, 300, 370, 20))
        self.messages_font_size_label.setFont(font)
        self.messages_font_size = QtWidgets.QComboBox(self)
        self.messages_font_size.setGeometry(QtCore.QRect(30, 330, 160, 30))
        self.messages_font_size.addItems([str(x) for x in range(10, 19)])
        self.messages_font_size.setCurrentIndex(settings['message_font_size'] - 10)

        self.unread = QtWidgets.QPushButton(self)
        self.unread.setGeometry(QtCore.QRect(30, 470, 340, 30))
        self.unread.clicked.connect(self.select_color)

        self.compact_mode = QtWidgets.QCheckBox(self)
        self.compact_mode.setGeometry(QtCore.QRect(30, 380, 370, 20))
        self.compact_mode.setChecked(settings['compact_mode'])

        self.close_to_tray = QtWidgets.QCheckBox(self)
        self.close_to_tray.setGeometry(QtCore.QRect(30, 410, 370, 20))
        self.close_to_tray.setChecked(settings['close_to_tray'])

        self.show_avatars = QtWidgets.QCheckBox(self)
        self.show_avatars.setGeometry(QtCore.QRect(30, 440, 370, 20))
        self.show_avatars.setChecked(settings['show_avatars'])

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
        self.show_avatars.setText(QtWidgets.QApplication.translate("interfaceForm", "Show avatars in chat"))
        self.setWindowTitle(QtWidgets.QApplication.translate("interfaceForm", "Interface settings"))
        self.label.setText(QtWidgets.QApplication.translate("interfaceForm", "Theme:"))
        self.lang.setText(QtWidgets.QApplication.translate("interfaceForm", "Language:"))
        self.smileys.setText(QtWidgets.QApplication.translate("interfaceForm", "Smileys"))
        self.smiley_pack_label.setText(QtWidgets.QApplication.translate("interfaceForm", "Smiley pack:"))
        self.mirror_mode.setText(QtWidgets.QApplication.translate("interfaceForm", "Mirror mode"))
        self.messages_font_size_label.setText(QtWidgets.QApplication.translate("interfaceForm", "Messages font size:"))
        self.unread.setText(QtWidgets.QApplication.translate("interfaceForm", "Select unread messages notification color"))
        self.compact_mode.setText(QtWidgets.QApplication.translate("interfaceForm", "Compact contact list"))
        self.import_smileys.setText(QtWidgets.QApplication.translate("interfaceForm", "Import smiley pack"))
        self.import_stickers.setText(QtWidgets.QApplication.translate("interfaceForm", "Import sticker pack"))
        self.close_to_tray.setText(QtWidgets.QApplication.translate("interfaceForm", "Close to tray"))
        self.choose_font.setText(QtWidgets.QApplication.translate("interfaceForm", "Select font"))

    def import_st(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                           QtWidgets.QApplication.translate("MainWindow",
                                                                                        'Choose folder with sticker pack'),
                                                           curr_directory(),
                                                           QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontUseNativeDialog)

        if directory:
            src = directory + '/'
            dest = curr_directory() + '/stickers/' + os.path.basename(directory) + '/'
            copy(src, dest)

    def import_sm(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                           QtWidgets.QApplication.translate("MainWindow",
                                                                                        'Choose folder with smiley pack'),
                                                           curr_directory(),
                                                           QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontUseNativeDialog)

        if directory:
            src = directory + '/'
            dest = curr_directory() + '/smileys/' + os.path.basename(directory) + '/'
            copy(src, dest)

    def new_font(self):
        settings = Settings.get_instance()
        font, ok = QtWidgets.QFontDialog.getFont(QtGui.QFont(settings['font'], 10), self)
        if ok:
            settings['font'] = font.family()
            settings.save()
            msgBox = QtWidgets.QMessageBox()
            text = QtWidgets.QApplication.translate("interfaceForm", 'Restart app to apply settings')
            msgBox.setWindowTitle(QtWidgets.QApplication.translate("interfaceForm", 'Restart required'))
            msgBox.setText(text)
            msgBox.exec_()

    def select_color(self):
        settings = Settings.get_instance()
        col = QtWidgets.QColorDialog.getColor(QtGui.QColor(settings['unread_color']))

        if col.isValid():
            name = col.name()
            settings['unread_color'] = name
            settings.save()

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['theme'] = str(self.themeSelect.currentText())
        try:
            theme = settings['theme']
            app = QtWidgets.QApplication.instance()
            with open(curr_directory() + settings.built_in_themes()[theme]) as fl:
                style = fl.read()
            app.setStyleSheet(style)
        except IsADirectoryError:
            app.setStyleSheet('') # for default style
        settings['smileys'] = self.smileys.isChecked()
        restart = False
        if settings['mirror_mode'] != self.mirror_mode.isChecked():
            settings['mirror_mode'] = self.mirror_mode.isChecked()
            restart = True
        if settings['compact_mode'] != self.compact_mode.isChecked():
            settings['compact_mode'] = self.compact_mode.isChecked()
            restart = True
        if settings['show_avatars'] != self.show_avatars.isChecked():
            settings['show_avatars'] = self.show_avatars.isChecked()
            restart = True
        settings['smiley_pack'] = self.smiley_pack.currentText()
        settings['close_to_tray'] = self.close_to_tray.isChecked()
        smileys.SmileyLoader.get_instance().load_pack()
        language = self.lang_choose.currentText()
        if settings['language'] != language:
            settings['language'] = language
            text = self.lang_choose.currentText()
            path = Settings.supported_languages()[text]
            app = QtWidgets.QApplication.instance()
            app.removeTranslator(app.translator)
            app.translator.load(curr_directory() + '/translations/' + path)
            app.installTranslator(app.translator)
        settings['message_font_size'] = self.messages_font_size.currentIndex() + 10
        Profile.get_instance().update()
        settings.save()
        if restart:
            msgBox = QtWidgets.QMessageBox()
            text = QtWidgets.QApplication.translate("interfaceForm", 'Restart app to apply settings')
            msgBox.setWindowTitle(QtWidgets.QApplication.translate("interfaceForm", 'Restart required'))
            msgBox.setText(text)
            msgBox.exec_()


class AudioSettings(CenteredWidget):
    """
    Audio calls settings form
    """

    def __init__(self):
        super(AudioSettings, self).__init__()
        self.initUI()
        self.retranslateUi()
        self.center()

    def initUI(self):
        self.setObjectName("audioSettingsForm")
        self.resize(400, 150)
        self.setMinimumSize(QtCore.QSize(400, 150))
        self.setMaximumSize(QtCore.QSize(400, 150))
        self.in_label = QtWidgets.QLabel(self)
        self.in_label.setGeometry(QtCore.QRect(25, 5, 350, 20))
        self.out_label = QtWidgets.QLabel(self)
        self.out_label.setGeometry(QtCore.QRect(25, 65, 350, 20))
        settings = Settings.get_instance()
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setFamily(settings['font'])
        self.in_label.setFont(font)
        self.out_label.setFont(font)
        self.input = QtWidgets.QComboBox(self)
        self.input.setGeometry(QtCore.QRect(25, 30, 350, 30))
        self.output = QtWidgets.QComboBox(self)
        self.output.setGeometry(QtCore.QRect(25, 90, 350, 30))
        p = pyaudio.PyAudio()
        self.in_indexes, self.out_indexes = [], []
        for i in range(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            if device["maxInputChannels"]:
                self.input.addItem(str(device["name"]))
                self.in_indexes.append(i)
            if device["maxOutputChannels"]:
                self.output.addItem(str(device["name"]))
                self.out_indexes.append(i)
        self.input.setCurrentIndex(self.in_indexes.index(settings.audio['input']))
        self.output.setCurrentIndex(self.out_indexes.index(settings.audio['output']))
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("audioSettingsForm", "Audio settings"))
        self.in_label.setText(QtWidgets.QApplication.translate("audioSettingsForm", "Input device:"))
        self.out_label.setText(QtWidgets.QApplication.translate("audioSettingsForm", "Output device:"))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings.audio['input'] = self.in_indexes[self.input.currentIndex()]
        settings.audio['output'] = self.out_indexes[self.output.currentIndex()]
        settings.save()


class VideoSettings(CenteredWidget):
    """
    Audio calls settings form
    """

    def __init__(self):
        super().__init__()
        self.initUI()
        self.retranslateUi()
        self.center()

    def initUI(self):
        self.setObjectName("videoSettingsForm")
        self.resize(400, 120)
        self.setMinimumSize(QtCore.QSize(400, 120))
        self.setMaximumSize(QtCore.QSize(400, 120))
        self.in_label = QtWidgets.QLabel(self)
        self.in_label.setGeometry(QtCore.QRect(25, 5, 350, 20))
        settings = Settings.get_instance()
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setFamily(settings['font'])
        self.in_label.setFont(font)
        self.video_size = QtWidgets.QComboBox(self)
        self.video_size.setGeometry(QtCore.QRect(25, 70, 350, 30))
        self.input = QtWidgets.QComboBox(self)
        self.input.setGeometry(QtCore.QRect(25, 30, 350, 30))
        self.input.currentIndexChanged.connect(self.selectionChanged)
        import cv2
        self.devices = []
        self.frame_max_sizes = []
        for i in range(10):
            v = cv2.VideoCapture(i)
            if v.isOpened():
                v.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
                v.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

                width = int(v.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(v.get(cv2.CAP_PROP_FRAME_HEIGHT))
                del v
                self.devices.append(i)
                self.frame_max_sizes.append((width, height))
                self.input.addItem('Device #' + str(i))
        try:
            index = self.devices.index(settings.video['device'])
            self.input.setCurrentIndex(index)
        except:
            print('Video devices error!')

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("videoSettingsForm", "Video settings"))
        self.in_label.setText(QtWidgets.QApplication.translate("videoSettingsForm", "Device:"))

    def closeEvent(self, event):
        try:
            settings = Settings.get_instance()
            settings.video['device'] = self.devices[self.input.currentIndex()]
            text = self.video_size.currentText()
            settings.video['width'] = int(text.split(' ')[0])
            settings.video['height'] = int(text.split(' ')[-1])
            settings.save()
        except Exception as ex:
            print('Saving video  settings error: ' + str(ex))

    def selectionChanged(self):
        width, height = self.frame_max_sizes[self.input.currentIndex()]
        self.video_size.clear()
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
                self.video_size.addItem(str(w) + ' * ' + str(h))


class PluginsSettings(CenteredWidget):
    """
    Plugins settings form
    """

    def __init__(self):
        super(PluginsSettings, self).__init__()
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
        self.pl_loader = plugin_support.PluginLoader.get_instance()
        self.update_list()
        self.comboBox.currentIndexChanged.connect(self.show_data)
        self.show_data()

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate('PluginsForm', "Plugins"))
        self.open.setText(QtWidgets.QApplication.translate('PluginsForm', "Open selected plugin"))

    def open_plugin(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        window = self.pl_loader.plugin_window(plugin[-1])
        if window is not None:
            self.window = window
            self.window.show()
        else:
            msgBox = QtWidgets.QMessageBox()
            text = QtWidgets.QApplication.translate("PluginsForm", 'No GUI found for this plugin')
            msgBox.setWindowTitle(QtWidgets.QApplication.translate("PluginsForm", 'Error'))
            msgBox.setText(text)
            msgBox.exec_()

    def update_list(self):
        self.comboBox.clear()
        data = self.pl_loader.get_plugins_list()
        self.comboBox.addItems(list(map(lambda x: x[0], data)))
        self.data = data

    def show_data(self):
        ind = self.comboBox.currentIndex()
        if len(self.data):
            plugin = self.data[ind]
            descr = plugin[2] or QtWidgets.QApplication.translate("PluginsForm", "No description available")
            self.label.setText(descr)
            if plugin[1]:
                self.button.setText(QtWidgets.QApplication.translate("PluginsForm", "Disable plugin"))
            else:
                self.button.setText(QtWidgets.QApplication.translate("PluginsForm", "Enable plugin"))
        else:
            self.open.setVisible(False)
            self.button.setVisible(False)
            self.label.setText(QtWidgets.QApplication.translate("PluginsForm", "No plugins found"))

    def button_click(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        self.pl_loader.toggle_plugin(plugin[-1])
        plugin[1] = not plugin[1]
        if plugin[1]:
            self.button.setText(QtWidgets.QApplication.translate("PluginsForm", "Disable plugin"))
        else:
            self.button.setText(QtWidgets.QApplication.translate("PluginsForm", "Enable plugin"))


class UpdateSettings(CenteredWidget):
    """
    Updates settings form
    """

    def __init__(self):
        super(UpdateSettings, self).__init__()
        self.initUI()
        self.center()

    def initUI(self):
        self.setObjectName("updateSettingsForm")
        self.resize(400, 150)
        self.setMinimumSize(QtCore.QSize(400, 120))
        self.setMaximumSize(QtCore.QSize(400, 120))
        self.in_label = QtWidgets.QLabel(self)
        self.in_label.setGeometry(QtCore.QRect(25, 5, 350, 20))
        settings = Settings.get_instance()
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setFamily(settings['font'])
        self.in_label.setFont(font)
        self.autoupdate = QtWidgets.QComboBox(self)
        self.autoupdate.setGeometry(QtCore.QRect(25, 30, 350, 30))
        self.button = QtWidgets.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(25, 70, 350, 30))
        self.button.setEnabled(settings['update'])
        self.button.clicked.connect(self.update_client)

        self.retranslateUi()
        self.autoupdate.setCurrentIndex(settings['update'])
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("updateSettingsForm", "Update settings"))
        self.in_label.setText(QtWidgets.QApplication.translate("updateSettingsForm", "Select update mode:"))
        self.button.setText(QtWidgets.QApplication.translate("updateSettingsForm", "Update Toxygen"))
        self.autoupdate.addItem(QtWidgets.QApplication.translate("updateSettingsForm", "Disabled"))
        self.autoupdate.addItem(QtWidgets.QApplication.translate("updateSettingsForm", "Manual"))
        self.autoupdate.addItem(QtWidgets.QApplication.translate("updateSettingsForm", "Auto"))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['update'] = self.autoupdate.currentIndex()
        settings.save()

    def update_client(self):
        if not updater.connection_available():
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle(
                QtWidgets.QApplication.translate("updateSettingsForm", "Error"))
            text = (QtWidgets.QApplication.translate("updateSettingsForm", 'Problems with internet connection'))
            msgBox.setText(text)
            msgBox.exec_()
            return
        if not updater.updater_available():
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle(
                QtWidgets.QApplication.translate("updateSettingsForm", "Error"))
            text = (QtWidgets.QApplication.translate("updateSettingsForm", 'Updater not found'))
            msgBox.setText(text)
            msgBox.exec_()
            return
        version = updater.check_for_updates()
        if version is not None:
            updater.download(version)
            QtWidgets.QApplication.closeAllWindows()
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setWindowTitle(
                QtWidgets.QApplication.translate("updateSettingsForm", "No updates found"))
            text = (QtWidgets.QApplication.translate("updateSettingsForm", 'Toxygen is up to date'))
            msgBox.setText(text)
            msgBox.exec_()
