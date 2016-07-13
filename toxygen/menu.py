try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from settings import *
from profile import Profile
from util import curr_directory, copy
from widgets import CenteredWidget, DataLabel, LineEdit
import pyaudio
import toxencryptsave
import plugin_support


class AddContact(CenteredWidget):
    """Add contact form"""

    def __init__(self, tox_id=''):
        super(AddContact, self).__init__()
        self.initUI(tox_id)
        self._adding = False

    def initUI(self, tox_id):
        self.setObjectName('AddContact')
        self.resize(568, 306)
        self.sendRequestButton = QtGui.QPushButton(self)
        self.sendRequestButton.setGeometry(QtCore.QRect(50, 270, 471, 31))
        self.sendRequestButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setBaseSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setObjectName("sendRequestButton")
        self.sendRequestButton.clicked.connect(self.add_friend)
        self.tox_id = LineEdit(self)
        self.tox_id.setGeometry(QtCore.QRect(50, 40, 471, 27))
        self.tox_id.setObjectName("lineEdit")
        self.tox_id.setText(tox_id)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 10, 80, 20))
        self.error_label = DataLabel(self)
        self.error_label.setGeometry(QtCore.QRect(120, 10, 420, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(30)
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("QLabel { color: #BC1C1C; }")
        self.label.setObjectName("label")
        self.message_edit = QtGui.QTextEdit(self)
        self.message_edit.setGeometry(QtCore.QRect(50, 110, 471, 151))
        self.message_edit.setObjectName("textEdit")
        self.message = QtGui.QLabel(self)
        self.message.setGeometry(QtCore.QRect(50, 70, 101, 31))
        self.message.setFont(font)
        self.message.setObjectName("label_2")
        self.retranslateUi()
        self.message_edit.setText('Hello! Add me to your contact list please')
        font = QtGui.QFont()
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
        self.setWindowTitle(QtGui.QApplication.translate('AddContact', "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.sendRequestButton.setText(QtGui.QApplication.translate("Form", "Send request", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate('AddContact', "TOX ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.message.setText(QtGui.QApplication.translate('AddContact', "Message:", None, QtGui.QApplication.UnicodeUTF8))
        self.tox_id.setPlaceholderText(QtGui.QApplication.translate('AddContact', "TOX ID or public key of contact", None, QtGui.QApplication.UnicodeUTF8))


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
        self.status = QtGui.QComboBox(self)
        self.status.setGeometry(QtCore.QRect(400, 60, 200, 27))
        self.status_message = LineEdit(self)
        self.status_message.setGeometry(QtCore.QRect(30, 130, 350, 27))
        self.status_message.setText(profile.status_message)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 30, 91, 25))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 100, 25))
        self.label_2.setFont(font)
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(40, 180, 100, 25))
        self.label_3.setFont(font)
        self.tox_id = QtGui.QLabel(self)
        self.tox_id.setGeometry(QtCore.QRect(15, 210, 685, 21))
        font.setPointSize(10)
        self.tox_id.setFont(font)
        s = profile.tox_id
        self.tox_id.setText(s)
        self.copyId = QtGui.QPushButton(self)
        self.copyId.setGeometry(QtCore.QRect(40, 250, 180, 30))
        self.copyId.clicked.connect(self.copy)
        self.export = QtGui.QPushButton(self)
        self.export.setGeometry(QtCore.QRect(230, 250, 180, 30))
        self.export.clicked.connect(self.export_profile)
        self.new_nospam = QtGui.QPushButton(self)
        self.new_nospam.setGeometry(QtCore.QRect(420, 250, 180, 30))
        self.new_nospam.clicked.connect(self.new_no_spam)
        self.copy_pk = QtGui.QPushButton(self)
        self.copy_pk.setGeometry(QtCore.QRect(40, 300, 180, 30))
        self.copy_pk.clicked.connect(self.copy_public_key)
        self.new_avatar = QtGui.QPushButton(self)
        self.new_avatar.setGeometry(QtCore.QRect(230, 300, 180, 30))
        self.delete_avatar = QtGui.QPushButton(self)
        self.delete_avatar.setGeometry(QtCore.QRect(420, 300, 180, 30))
        self.delete_avatar.clicked.connect(self.reset_avatar)
        self.new_avatar.clicked.connect(self.set_avatar)
        self.profilepass = QtGui.QLabel(self)
        self.profilepass.setGeometry(QtCore.QRect(40, 340, 300, 30))
        font.setPointSize(18)
        self.profilepass.setFont(font)
        self.password = LineEdit(self)
        self.password.setGeometry(QtCore.QRect(40, 380, 300, 30))
        self.password.setEchoMode(QtGui.QLineEdit.EchoMode.Password)
        self.leave_blank = QtGui.QLabel(self)
        self.leave_blank.setGeometry(QtCore.QRect(350, 380, 300, 30))
        self.confirm_password = LineEdit(self)
        self.confirm_password.setGeometry(QtCore.QRect(40, 420, 300, 30))
        self.confirm_password.setEchoMode(QtGui.QLineEdit.EchoMode.Password)
        self.set_password = QtGui.QPushButton(self)
        self.set_password.setGeometry(QtCore.QRect(40, 470, 300, 30))
        self.set_password.clicked.connect(self.new_password)
        self.not_match = QtGui.QLabel(self)
        self.not_match.setGeometry(QtCore.QRect(350, 420, 300, 30))
        self.not_match.setVisible(False)
        self.not_match.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.warning = QtGui.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(40, 510, 500, 30))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.default = QtGui.QPushButton(self)
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
        self.export.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Export profile", None, QtGui.QApplication.UnicodeUTF8))
        self.setWindowTitle(QtGui.QApplication.translate("ProfileSettingsForm", "Profile settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ProfileSettingsForm", "TOX ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.copyId.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Copy TOX ID", None, QtGui.QApplication.UnicodeUTF8))
        self.new_avatar.setText(QtGui.QApplication.translate("ProfileSettingsForm", "New avatar", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_avatar.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Reset avatar", None, QtGui.QApplication.UnicodeUTF8))
        self.new_nospam.setText(QtGui.QApplication.translate("ProfileSettingsForm", "New NoSpam", None, QtGui.QApplication.UnicodeUTF8))
        self.profilepass.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Profile password", None, QtGui.QApplication.UnicodeUTF8))
        self.password.setPlaceholderText(QtGui.QApplication.translate("ProfileSettingsForm", "Password (at least 8 symbols)", None, QtGui.QApplication.UnicodeUTF8))
        self.confirm_password.setPlaceholderText(QtGui.QApplication.translate("ProfileSettingsForm", "Confirm password", None, QtGui.QApplication.UnicodeUTF8))
        self.set_password.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Set password", None, QtGui.QApplication.UnicodeUTF8))
        self.not_match.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Passwords do not match", None, QtGui.QApplication.UnicodeUTF8))
        self.leave_blank.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Leaving blank will reset current password", None, QtGui.QApplication.UnicodeUTF8))
        self.warning.setText(QtGui.QApplication.translate("ProfileSettingsForm", "There is no way to recover lost passwords", None, QtGui.QApplication.UnicodeUTF8))
        self.status.addItem(QtGui.QApplication.translate("ProfileSettingsForm", "Online", None, QtGui.QApplication.UnicodeUTF8))
        self.status.addItem(QtGui.QApplication.translate("ProfileSettingsForm", "Away", None, QtGui.QApplication.UnicodeUTF8))
        self.status.addItem(QtGui.QApplication.translate("ProfileSettingsForm", "Busy", None, QtGui.QApplication.UnicodeUTF8))
        self.copy_pk.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Copy public key", None, QtGui.QApplication.UnicodeUTF8))
        if self.auto:
            self.default.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Mark as not default profile", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.default.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Mark as default profile", None, QtGui.QApplication.UnicodeUTF8))

    def auto_profile(self):
        if self.auto:
            Settings.reset_auto_profile()
        else:
            Settings.set_auto_profile(ProfileHelper.get_path(), Settings.get_instance().name)
        self.auto = not self.auto
        if self.auto:
            self.default.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Mark as not default profile", None,
                                                              QtGui.QApplication.UnicodeUTF8))
        else:
            self.default.setText(
                QtGui.QApplication.translate("ProfileSettingsForm", "Mark as default profile", None,
                                             QtGui.QApplication.UnicodeUTF8))

    def new_password(self):
        if self.password.text() == self.confirm_password.text():
            if not len(self.password.text()) or len(self.password.text()) >= 8:
                e = toxencryptsave.ToxEncryptSave.get_instance()
                e.set_password(self.password.text())
                self.close()
            else:
                self.not_match.setText(
                    QtGui.QApplication.translate("ProfileSettingsForm", "Password must be at least 8 symbols", None,
                                                 QtGui.QApplication.UnicodeUTF8))
            self.not_match.setVisible(True)
        else:
            self.not_match.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Passwords do not match", None,
                                                                QtGui.QApplication.UnicodeUTF8))
            self.not_match.setVisible(True)

    def copy(self):
        clipboard = QtGui.QApplication.clipboard()
        profile = Profile.get_instance()
        clipboard.setText(profile.tox_id)
        pixmap = QtGui.QPixmap(curr_directory() + '/images/accept.png')
        icon = QtGui.QIcon(pixmap)
        self.copyId.setIcon(icon)
        self.copyId.setIconSize(QtCore.QSize(10, 10))

    def copy_public_key(self):
        clipboard = QtGui.QApplication.clipboard()
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
        choose = QtGui.QApplication.translate("ProfileSettingsForm", "Choose avatar", None, QtGui.QApplication.UnicodeUTF8)
        name = QtGui.QFileDialog.getOpenFileName(self, choose, None, 'Images (*.png)',
                                                 options=QtGui.QFileDialog.DontUseNativeDialog)
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
        directory = QtGui.QFileDialog.getExistingDirectory(options=QtGui.QFileDialog.DontUseNativeDialog) + '/'
        if directory != '/':
            ProfileHelper.get_instance().export_profile(directory)
            settings = Settings.get_instance()
            settings.export(directory)
            profile = Profile.get_instance()
            profile.export_history(directory)

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
        self.ipv = QtGui.QCheckBox(self)
        self.ipv.setGeometry(QtCore.QRect(20, 10, 97, 22))
        self.ipv.setObjectName("ipv")
        self.udp = QtGui.QCheckBox(self)
        self.udp.setGeometry(QtCore.QRect(150, 10, 97, 22))
        self.udp.setObjectName("udp")
        self.proxy = QtGui.QCheckBox(self)
        self.proxy.setGeometry(QtCore.QRect(20, 40, 97, 22))
        self.http = QtGui.QCheckBox(self)
        self.http.setGeometry(QtCore.QRect(20, 70, 97, 22))
        self.proxy.setObjectName("proxy")
        self.proxyip = LineEdit(self)
        self.proxyip.setGeometry(QtCore.QRect(40, 130, 231, 27))
        self.proxyip.setObjectName("proxyip")
        self.proxyport = LineEdit(self)
        self.proxyport.setGeometry(QtCore.QRect(40, 190, 231, 27))
        self.proxyport.setObjectName("proxyport")
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 100, 66, 17))
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 165, 66, 17))
        self.reconnect = QtGui.QPushButton(self)
        self.reconnect.setGeometry(QtCore.QRect(40, 230, 231, 30))
        self.reconnect.clicked.connect(self.restart_core)
        settings = Settings.get_instance()
        self.ipv.setChecked(settings['ipv6_enabled'])
        self.udp.setChecked(settings['udp_enabled'])
        self.proxy.setChecked(settings['proxy_type'])
        self.proxyip.setText(settings['proxy_host'])
        self.proxyport.setText(str(settings['proxy_port']))
        self.http.setChecked(settings['proxy_type'] == 1)
        self.warning = QtGui.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(5, 270, 290, 60))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.retranslateUi()
        self.proxy.stateChanged.connect(lambda x: self.activate())
        self.activate()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("NetworkSettings", "Network settings", None, QtGui.QApplication.UnicodeUTF8))
        self.ipv.setText(QtGui.QApplication.translate("Form", "IPv6", None, QtGui.QApplication.UnicodeUTF8))
        self.udp.setText(QtGui.QApplication.translate("Form", "UDP", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy.setText(QtGui.QApplication.translate("Form", "Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "IP:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Port:", None, QtGui.QApplication.UnicodeUTF8))
        self.reconnect.setText(QtGui.QApplication.translate("NetworkSettings", "Restart TOX core", None, QtGui.QApplication.UnicodeUTF8))
        self.http.setText(QtGui.QApplication.translate("Form", "HTTP", None, QtGui.QApplication.UnicodeUTF8))
        self.warning.setText(QtGui.QApplication.translate("Form", "WARNING:\nusing proxy with enabled UDP\ncan produce IP leak",
                                                          None, QtGui.QApplication.UnicodeUTF8))

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
        self.saveHistory = QtGui.QCheckBox(self)
        self.saveHistory.setGeometry(QtCore.QRect(10, 20, 350, 22))
        self.saveUnsentOnly = QtGui.QCheckBox(self)
        self.saveUnsentOnly.setGeometry(QtCore.QRect(10, 60, 350, 22))

        self.fileautoaccept = QtGui.QCheckBox(self)
        self.fileautoaccept.setGeometry(QtCore.QRect(10, 100, 350, 22))

        self.typingNotifications = QtGui.QCheckBox(self)
        self.typingNotifications.setGeometry(QtCore.QRect(10, 140, 350, 30))
        self.inlines = QtGui.QCheckBox(self)
        self.inlines.setGeometry(QtCore.QRect(10, 180, 350, 30))
        self.auto_path = QtGui.QLabel(self)
        self.auto_path.setGeometry(QtCore.QRect(10, 230, 350, 30))
        self.path = QtGui.QPlainTextEdit(self)
        self.path.setGeometry(QtCore.QRect(10, 265, 350, 45))
        self.change_path = QtGui.QPushButton(self)
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
        self.block_user_label = QtGui.QLabel(self)
        self.block_user_label.setGeometry(QtCore.QRect(10, 360, 350, 30))
        self.block_id = QtGui.QPlainTextEdit(self)
        self.block_id.setGeometry(QtCore.QRect(10, 390, 350, 30))
        self.block = QtGui.QPushButton(self)
        self.block.setGeometry(QtCore.QRect(10, 430, 350, 30))
        self.block.clicked.connect(lambda: Profile.get_instance().block_user(self.block_id.toPlainText()) or self.close())
        self.blocked_users_label = QtGui.QLabel(self)
        self.blocked_users_label.setGeometry(QtCore.QRect(10, 470, 350, 30))
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(10, 500, 350, 30))
        self.comboBox.addItems(settings['blocked'])
        self.unblock = QtGui.QPushButton(self)
        self.unblock.setGeometry(QtCore.QRect(10, 540, 350, 30))
        self.unblock.clicked.connect(lambda: self.unblock_user())
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("privacySettings", "Privacy settings", None, QtGui.QApplication.UnicodeUTF8))
        self.saveHistory.setText(QtGui.QApplication.translate("privacySettings", "Save chat history", None, QtGui.QApplication.UnicodeUTF8))
        self.fileautoaccept.setText(QtGui.QApplication.translate("privacySettings", "Allow file auto accept", None, QtGui.QApplication.UnicodeUTF8))
        self.typingNotifications.setText(QtGui.QApplication.translate("privacySettings", "Send typing notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.auto_path.setText(QtGui.QApplication.translate("privacySettings", "Auto accept default path:", None, QtGui.QApplication.UnicodeUTF8))
        self.change_path.setText(QtGui.QApplication.translate("privacySettings", "Change", None, QtGui.QApplication.UnicodeUTF8))
        self.inlines.setText(QtGui.QApplication.translate("privacySettings", "Allow inlines", None, QtGui.QApplication.UnicodeUTF8))
        self.block_user_label.setText(QtGui.QApplication.translate("privacySettings", "Block by public key:", None, QtGui.QApplication.UnicodeUTF8))
        self.blocked_users_label.setText(QtGui.QApplication.translate("privacySettings", "Blocked users:", None, QtGui.QApplication.UnicodeUTF8))
        self.unblock.setText(QtGui.QApplication.translate("privacySettings", "Unblock", None, QtGui.QApplication.UnicodeUTF8))
        self.block.setText(QtGui.QApplication.translate("privacySettings", "Block user", None, QtGui.QApplication.UnicodeUTF8))
        self.saveUnsentOnly.setText(QtGui.QApplication.translate("privacySettings", "Save unsent messages only", None, QtGui.QApplication.UnicodeUTF8))

    def update(self, new_state):
        self.saveUnsentOnly.setEnabled(new_state)
        if not new_state:
            self.saveUnsentOnly.setChecked(False)

    def unblock_user(self):
        if not self.comboBox.count():
            return
        title = QtGui.QApplication.translate("privacySettings", "Add to friend list", None, QtGui.QApplication.UnicodeUTF8)
        info = QtGui.QApplication.translate("privacySettings", "Do you want to add this user to friend list?", None, QtGui.QApplication.UnicodeUTF8)
        reply = QtGui.QMessageBox.question(None, title, info, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        Profile.get_instance().unblock_user(self.comboBox.currentText(), reply == QtGui.QMessageBox.Yes)
        self.close()

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['typing_notifications'] = self.typingNotifications.isChecked()
        settings['allow_auto_accept'] = self.fileautoaccept.isChecked()

        if settings['save_history'] and not self.saveHistory.isChecked():  # clear history
            reply = QtGui.QMessageBox.question(None,
                                               QtGui.QApplication.translate("privacySettings",
                                                                            'Chat history',
                                                                            None, QtGui.QApplication.UnicodeUTF8),
                                               QtGui.QApplication.translate("privacySettings",
                                                                            'History will be cleaned! Continue?',
                                                                            None, QtGui.QApplication.UnicodeUTF8),
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                Profile.get_instance().clear_history()
                settings['save_history'] = self.saveHistory.isChecked()
        else:
            settings['save_history'] = self.saveHistory.isChecked()
        if self.saveUnsentOnly.isChecked() and not settings['save_unsent_only']:
            reply = QtGui.QMessageBox.question(None,
                                               QtGui.QApplication.translate("privacySettings",
                                                                            'Chat history',
                                                                            None, QtGui.QApplication.UnicodeUTF8),
                                               QtGui.QApplication.translate("privacySettings",
                                                                            'History will be cleaned! Continue?',
                                                                            None, QtGui.QApplication.UnicodeUTF8),
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                Profile.get_instance().clear_history(None, True)
                settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        else:
            settings['save_unsent_only'] = self.saveUnsentOnly.isChecked()
        settings['auto_accept_path'] = self.path.toPlainText()
        settings['allow_inline'] = self.inlines.isChecked()
        settings.save()

    def new_path(self):
        directory = QtGui.QFileDialog.getExistingDirectory(options=QtGui.QFileDialog.DontUseNativeDialog) + '/'
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
        self.enableNotifications = QtGui.QCheckBox(self)
        self.enableNotifications.setGeometry(QtCore.QRect(10, 20, 340, 18))
        self.callsSound = QtGui.QCheckBox(self)
        self.callsSound.setGeometry(QtCore.QRect(10, 120, 340, 18))
        self.soundNotifications = QtGui.QCheckBox(self)
        self.soundNotifications.setGeometry(QtCore.QRect(10, 70, 340, 18))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.callsSound.setFont(font)
        self.soundNotifications.setFont(font)
        self.enableNotifications.setFont(font)
        s = Settings.get_instance()
        self.enableNotifications.setChecked(s['notifications'])
        self.soundNotifications.setChecked(s['sound_notifications'])
        self.callsSound.setChecked(s['calls_sound'])
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("notificationsForm", "Notification settings", None, QtGui.QApplication.UnicodeUTF8))
        self.enableNotifications.setText(QtGui.QApplication.translate("notificationsForm", "Enable notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.callsSound.setText(QtGui.QApplication.translate("notificationsForm", "Enable call\'s sound", None, QtGui.QApplication.UnicodeUTF8))
        self.soundNotifications.setText(QtGui.QApplication.translate("notificationsForm", "Enable sound notifications", None, QtGui.QApplication.UnicodeUTF8))

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
        self.setMinimumSize(QtCore.QSize(400, 580))
        self.setMaximumSize(QtCore.QSize(400, 580))
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 10, 370, 20))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.themeSelect = QtGui.QComboBox(self)
        self.themeSelect.setGeometry(QtCore.QRect(30, 40, 120, 30))
        list_of_themes = ['dark']
        self.themeSelect.addItems(list_of_themes)
        settings = Settings.get_instance()
        theme = settings['theme']
        if theme in list_of_themes:
            index = list_of_themes.index(theme)
        else:
            index = 0
        self.themeSelect.setCurrentIndex(index)
        self.lang_choose = QtGui.QComboBox(self)
        self.lang_choose.setGeometry(QtCore.QRect(30, 110, 120, 30))
        supported = sorted(Settings.supported_languages().keys(), reverse=True)
        for key in supported:
            self.lang_choose.insertItem(0, key)
            if settings['language'] == key:
                self.lang_choose.setCurrentIndex(0)
        self.lang = QtGui.QLabel(self)
        self.lang.setGeometry(QtCore.QRect(30, 80, 370, 20))
        self.lang.setFont(font)
        self.mirror_mode = QtGui.QCheckBox(self)
        self.mirror_mode.setGeometry(QtCore.QRect(30, 160, 370, 20))
        self.mirror_mode.setChecked(settings['mirror_mode'])
        self.smileys = QtGui.QCheckBox(self)
        self.smileys.setGeometry(QtCore.QRect(30, 190, 120, 20))
        self.smileys.setChecked(settings['smileys'])
        self.smiley_pack_label = QtGui.QLabel(self)
        self.smiley_pack_label.setGeometry(QtCore.QRect(30, 230, 370, 20))
        self.smiley_pack_label.setFont(font)
        self.smiley_pack = QtGui.QComboBox(self)
        self.smiley_pack.setGeometry(QtCore.QRect(30, 260, 160, 30))
        sm = smileys.SmileyLoader.get_instance()
        self.smiley_pack.addItems(sm.get_packs_list())
        try:
            ind = sm.get_packs_list().index(settings['smiley_pack'])
        except:
            ind = sm.get_packs_list().index('default')
        self.smiley_pack.setCurrentIndex(ind)
        self.messages_font_size_label = QtGui.QLabel(self)
        self.messages_font_size_label.setGeometry(QtCore.QRect(30, 300, 370, 20))
        self.messages_font_size_label.setFont(font)
        self.messages_font_size = QtGui.QComboBox(self)
        self.messages_font_size.setGeometry(QtCore.QRect(30, 330, 160, 30))
        self.messages_font_size.addItems([str(x) for x in range(10, 19)])
        self.messages_font_size.setCurrentIndex(settings['message_font_size'] - 10)

        self.unread = QtGui.QPushButton(self)
        self.unread.setGeometry(QtCore.QRect(30, 465, 340, 30))
        self.unread.clicked.connect(self.select_color)

        self.compact_mode = QtGui.QCheckBox(self)
        self.compact_mode.setGeometry(QtCore.QRect(30, 380, 370, 20))
        self.compact_mode.setChecked(settings['compact_mode'])

        self.show_avatars = QtGui.QCheckBox(self)
        self.show_avatars.setGeometry(QtCore.QRect(30, 410, 370, 20))
        self.show_avatars.setChecked(settings['show_avatars'])

        self.import_smileys = QtGui.QPushButton(self)
        self.import_smileys.setGeometry(QtCore.QRect(30, 505, 340, 30))
        self.import_smileys.clicked.connect(self.import_sm)

        self.import_stickers = QtGui.QPushButton(self)
        self.import_stickers.setGeometry(QtCore.QRect(30, 545, 340, 30))
        self.import_stickers.clicked.connect(self.import_st)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.show_avatars.setText(QtGui.QApplication.translate("interfaceForm", "Show avatars in chat", None, QtGui.QApplication.UnicodeUTF8))
        self.setWindowTitle(QtGui.QApplication.translate("interfaceForm", "Interface settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("interfaceForm", "Theme:", None, QtGui.QApplication.UnicodeUTF8))
        self.lang.setText(QtGui.QApplication.translate("interfaceForm", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.smileys.setText(QtGui.QApplication.translate("interfaceForm", "Smileys", None, QtGui.QApplication.UnicodeUTF8))
        self.smiley_pack_label.setText(QtGui.QApplication.translate("interfaceForm", "Smiley pack:", None, QtGui.QApplication.UnicodeUTF8))
        self.mirror_mode.setText(QtGui.QApplication.translate("interfaceForm", "Mirror mode", None, QtGui.QApplication.UnicodeUTF8))
        self.messages_font_size_label.setText(QtGui.QApplication.translate("interfaceForm", "Messages font size:", None, QtGui.QApplication.UnicodeUTF8))
        self.unread.setText(QtGui.QApplication.translate("interfaceForm", "Select unread messages notification color", None, QtGui.QApplication.UnicodeUTF8))
        self.compact_mode.setText(QtGui.QApplication.translate("interfaceForm", "Compact contact list", None, QtGui.QApplication.UnicodeUTF8))
        self.import_smileys.setText(QtGui.QApplication.translate("interfaceForm", "Import smiley pack", None, QtGui.QApplication.UnicodeUTF8))
        self.import_stickers.setText(QtGui.QApplication.translate("interfaceForm", "Import sticker pack", None, QtGui.QApplication.UnicodeUTF8))

    def import_st(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           QtGui.QApplication.translate("MainWindow",
                                                                                        'Choose folder with sticker pack',
                                                                                        None,
                                                                                        QtGui.QApplication.UnicodeUTF8),
                                                           curr_directory(),
                                                           QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)

        if directory:
            src = directory + '/'
            dest = curr_directory() + '/stickers/' + os.path.basename(directory) + '/'
            copy(src, dest)

    def import_sm(self):
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           QtGui.QApplication.translate("MainWindow",
                                                                                        'Choose folder with smiley pack',
                                                                                        None,
                                                                                        QtGui.QApplication.UnicodeUTF8),
                                                           curr_directory(),
                                                           QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)

        if directory:
            src = directory + '/'
            dest = curr_directory() + '/smileys/' + os.path.basename(directory) + '/'
            copy(src, dest)

    def select_color(self):
        col = QtGui.QColorDialog.getColor()

        if col.isValid():
            settings = Settings.get_instance()
            name = col.name()
            settings['unread_color'] = name
            settings.save()

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['theme'] = str(self.themeSelect.currentText())
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
        smileys.SmileyLoader.get_instance().load_pack()
        language = self.lang_choose.currentText()
        if settings['language'] != language:
            settings['language'] = language
            text = self.lang_choose.currentText()
            path = Settings.supported_languages()[text]
            app = QtGui.QApplication.instance()
            app.removeTranslator(app.translator)
            app.translator.load(curr_directory() + '/translations/' + path)
            app.installTranslator(app.translator)
        settings['message_font_size'] = self.messages_font_size.currentIndex() + 10
        Profile.get_instance().update()
        settings.save()
        if restart:
            msgBox = QtGui.QMessageBox()
            text = QtGui.QApplication.translate("interfaceForm", 'Restart app to apply settings', None,
                                                QtGui.QApplication.UnicodeUTF8)
            msgBox.setWindowTitle(QtGui.QApplication.translate("interfaceForm", 'Restart required', None,
                                                               QtGui.QApplication.UnicodeUTF8))
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
        self.in_label = QtGui.QLabel(self)
        self.in_label.setGeometry(QtCore.QRect(25, 5, 350, 20))
        self.out_label = QtGui.QLabel(self)
        self.out_label.setGeometry(QtCore.QRect(25, 65, 350, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.in_label.setFont(font)
        self.out_label.setFont(font)
        self.input = QtGui.QComboBox(self)
        self.input.setGeometry(QtCore.QRect(25, 30, 350, 30))
        self.output = QtGui.QComboBox(self)
        self.output.setGeometry(QtCore.QRect(25, 90, 350, 30))
        p = pyaudio.PyAudio()
        settings = Settings.get_instance()
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
        self.setWindowTitle(QtGui.QApplication.translate("audioSettingsForm", "Audio settings", None, QtGui.QApplication.UnicodeUTF8))
        self.in_label.setText(QtGui.QApplication.translate("audioSettingsForm", "Input device:", None, QtGui.QApplication.UnicodeUTF8))
        self.out_label.setText(QtGui.QApplication.translate("audioSettingsForm", "Output device:", None, QtGui.QApplication.UnicodeUTF8))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings.audio['input'] = self.in_indexes[self.input.currentIndex()]
        settings.audio['output'] = self.out_indexes[self.output.currentIndex()]
        settings.save()


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
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(30, 10, 340, 30))
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 40, 340, 90))
        self.label.setWordWrap(True)
        self.button = QtGui.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(30, 130, 340, 30))
        self.button.clicked.connect(self.button_click)
        self.open = QtGui.QPushButton(self)
        self.open.setGeometry(QtCore.QRect(30, 170, 340, 30))
        self.open.clicked.connect(self.open_plugin)
        self.pl_loader = plugin_support.PluginLoader.get_instance()
        self.update_list()
        self.comboBox.currentIndexChanged.connect(self.show_data)
        self.show_data()

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate('PluginsForm', "Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.open.setText(QtGui.QApplication.translate('PluginsForm', "Open selected plugin", None, QtGui.QApplication.UnicodeUTF8))

    def open_plugin(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        window = self.pl_loader.plugin_window(plugin[-1])
        if window is not None:
            self.window = window
            self.window.show()
        else:
            msgBox = QtGui.QMessageBox()
            text = QtGui.QApplication.translate("PluginsForm", 'No GUI found for this plugin', None,
                                                QtGui.QApplication.UnicodeUTF8)
            msgBox.setWindowTitle(QtGui.QApplication.translate("PluginsForm", 'Error', None,
                                                               QtGui.QApplication.UnicodeUTF8))
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
            descr = plugin[2] or QtGui.QApplication.translate("PluginsForm", "No description available", None, QtGui.QApplication.UnicodeUTF8)
            self.label.setText(descr)
            if plugin[1]:
                self.button.setText(QtGui.QApplication.translate("PluginsForm", "Disable plugin", None, QtGui.QApplication.UnicodeUTF8))
            else:
                self.button.setText(QtGui.QApplication.translate("PluginsForm", "Enable plugin", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.open.setVisible(False)
            self.button.setVisible(False)
            self.label.setText(QtGui.QApplication.translate("PluginsForm", "No plugins found", None, QtGui.QApplication.UnicodeUTF8))

    def button_click(self):
        ind = self.comboBox.currentIndex()
        plugin = self.data[ind]
        self.pl_loader.toggle_plugin(plugin[-1])
        plugin[1] = not plugin[1]
        if plugin[1]:
            self.button.setText(QtGui.QApplication.translate("PluginsForm", "Disable plugin", None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.button.setText(QtGui.QApplication.translate("PluginsForm", "Enable plugin", None, QtGui.QApplication.UnicodeUTF8))
