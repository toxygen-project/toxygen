from PySide import QtCore, QtGui
from settings import *
from profile import Profile
from util import get_style, curr_directory
from widgets import CenteredWidget, DataLabel
import pyaudio


class AddContact(CenteredWidget):
    """Add contact form"""

    def __init__(self):
        super(AddContact, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName('AddContact')
        self.resize(568, 306)
        self.sendRequestButton = QtGui.QPushButton(self)
        self.sendRequestButton.setGeometry(QtCore.QRect(50, 270, 471, 31))
        self.sendRequestButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setBaseSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setObjectName("sendRequestButton")
        self.sendRequestButton.clicked.connect(self.add_friend)
        self.tox_id = QtGui.QLineEdit(self)
        self.tox_id.setGeometry(QtCore.QRect(50, 40, 471, 27))
        self.tox_id.setObjectName("lineEdit")
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(60, 10, 80, 20))
        self.error_label = DataLabel(self)
        self.error_label.setGeometry(QtCore.QRect(120, 10, 420, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(30)
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("QLabel { color: red; }")
        self.label.setObjectName("label")
        self.message_edit = QtGui.QTextEdit(self)
        self.message_edit.setGeometry(QtCore.QRect(50, 110, 471, 151))
        self.message_edit.setObjectName("textEdit")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(60, 70, 101, 31))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.retranslateUi()
        self.message_edit.setText('Hello! Add me to your contact list please')
        QtCore.QMetaObject.connectSlotsByName(self)

    def add_friend(self):
        profile = Profile.get_instance()
        send = profile.send_friend_request(self.tox_id.text(), self.message_edit.toPlainText())
        if send is True:
            # request was successful
            self.close()
        else:  # print error data
            self.error_label.setText(send)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate('AddContact', "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.sendRequestButton.setText(QtGui.QApplication.translate("Form", "Send request", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate('AddContact', "TOX ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate('AddContact', "Message:", None, QtGui.QApplication.UnicodeUTF8))


class ProfileSettings(CenteredWidget):
    """Form with profile settings such as name, status, TOX ID"""
    def __init__(self):
        super(ProfileSettings, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("ProfileSettingsForm")
        self.setMinimumSize(QtCore.QSize(650, 320))
        self.setMaximumSize(QtCore.QSize(650, 320))
        self.nick = QtGui.QLineEdit(self)
        self.nick.setGeometry(QtCore.QRect(30, 60, 350, 27))
        self.nick.setObjectName("nick")
        profile = Profile.get_instance()
        self.nick.setText(profile.name)
        self.status = QtGui.QLineEdit(self)
        self.status.setGeometry(QtCore.QRect(30, 130, 350, 27))
        self.status.setObjectName("status")
        self.status.setText(profile.status_message)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 30, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 100, 100, 21))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(40, 180, 100, 21))
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.tox_id = QtGui.QLabel(self)
        self.tox_id.setGeometry(QtCore.QRect(10, 210, self.width(), 21))
        font.setPointSize(10)
        self.tox_id.setFont(font)
        self.tox_id.setObjectName("tox_id")
        s = profile.tox_id
        self.tox_id.setText(s)
        self.copyId = QtGui.QPushButton(self)
        self.copyId.setGeometry(QtCore.QRect(40, 250, 160, 30))
        self.copyId.setObjectName("copyId")
        self.copyId.clicked.connect(self.copy)
        self.export = QtGui.QPushButton(self)
        self.export.setGeometry(QtCore.QRect(210, 250, 160, 30))
        self.export.setObjectName("export")
        self.export.clicked.connect(self.export_profile)
        self.new_nospam = QtGui.QPushButton(self)
        self.new_nospam.setGeometry(QtCore.QRect(380, 250, 160, 30))
        self.new_nospam.clicked.connect(self.new_no_spam)
        self.new_avatar = QtGui.QPushButton(self)
        self.new_avatar.setGeometry(QtCore.QRect(400, 50, 200, 50))
        self.delete_avatar = QtGui.QPushButton(self)
        self.delete_avatar.setGeometry(QtCore.QRect(400, 120, 200, 50))
        self.delete_avatar.clicked.connect(self.reset_avatar)
        self.new_avatar.clicked.connect(self.set_avatar)
        self.retranslateUi()
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

    def copy(self):
        clipboard = QtGui.QApplication.clipboard()
        profile = Profile.get_instance()
        clipboard.setText(profile.tox_id)

    def new_no_spam(self):
        self.tox_id.setText(Profile.get_instance().new_nospam())

    def reset_avatar(self):
        Profile.get_instance().reset_avatar()

    def set_avatar(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open file', None, 'Image Files (*.png)')
        print name
        if name[0]:
            with open(name[0], 'rb') as f:
                data = f.read()
            Profile.get_instance().set_avatar(data)

    def export_profile(self):
        directory = QtGui.QFileDialog.getExistingDirectory() + '/'
        if directory != '/':
            ProfileHelper.export_profile(directory)
            settings = Settings.get_instance()
            settings.export(directory)
            profile = Profile.get_instance()
            profile.export_history(directory)

    def closeEvent(self, event):
        profile = Profile.get_instance()
        profile.set_name(self.nick.text().encode('utf-8'))
        profile.set_status_message(self.status.text().encode('utf-8'))


class NetworkSettings(CenteredWidget):
    """Network settings form: UDP, Ipv6 and proxy"""
    def __init__(self, reset):
        super(NetworkSettings, self).__init__()
        self.reset = reset
        self.reconn = False
        self.initUI()

    def initUI(self):
        self.setObjectName("NetworkSettings")
        self.resize(300, 300)
        self.setMinimumSize(QtCore.QSize(300, 300))
        self.setMaximumSize(QtCore.QSize(300, 300))
        self.setBaseSize(QtCore.QSize(300, 300))
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
        self.proxyip = QtGui.QLineEdit(self)
        self.proxyip.setGeometry(QtCore.QRect(40, 130, 231, 27))
        self.proxyip.setObjectName("proxyip")
        self.proxyport = QtGui.QLineEdit(self)
        self.proxyport.setGeometry(QtCore.QRect(40, 190, 231, 27))
        self.proxyport.setObjectName("proxyport")
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 100, 66, 17))
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 165, 66, 17))
        self.reconnect = QtGui.QPushButton(self)
        self.reconnect.setGeometry(QtCore.QRect(40, 230, 200, 30))
        self.reconnect.clicked.connect(self.restart_core)
        settings = Settings.get_instance()
        self.ipv.setChecked(settings['ipv6_enabled'])
        self.udp.setChecked(settings['udp_enabled'])
        self.proxy.setChecked(settings['proxy_type'])
        self.proxyip.setText(settings['proxy_host'])
        self.proxyport.setText(unicode(settings['proxy_port']))
        self.http.setChecked(settings['proxy_type'] == 1)
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

    def activate(self):
        bl = self.proxy.isChecked()
        self.proxyip.setEnabled(bl)
        self.http.setEnabled(bl)
        self.proxyport.setEnabled(bl)

    def closeEvent(self, *args, **kwargs):
        settings = Settings.get_instance()
        old_data = str(settings['ipv6_enabled']) + str(settings['udp_enabled']) + str(bool(settings['proxy_type']))
        new_data = str(self.ipv.isChecked()) + str(self.udp.isChecked()) + str(self.proxy.isChecked())
        changed = old_data != new_data
        if self.proxy.isChecked() and (self.proxyip.text() != settings['proxy_host'] or self.proxyport.text() != unicode(settings['proxy_port'])):
            changed = True
        if changed:
            settings['ipv6_enabled'] = self.ipv.isChecked()
            settings['udp_enabled'] = self.udp.isChecked()
            settings['proxy_type'] = 2 - int(self.http.isChecked()) if self.proxy.isChecked() else 0
            settings['proxy_host'] = str(self.proxyip.text())
            settings['proxy_port'] = int(self.proxyport.text())
            settings.save()
        if changed or self.reconnect:
            # recreate tox instance
            Profile.get_instance().reset(self.reset)

    def restart_core(self):
        self.reconn = True
        self.close()


class PrivacySettings(CenteredWidget):
    """Privacy settings form: history, typing notifications"""

    def __init__(self):
        super(PrivacySettings, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("privacySettings")
        self.resize(350, 550)
        self.setMinimumSize(QtCore.QSize(350, 550))
        self.setMaximumSize(QtCore.QSize(350, 550))
        self.saveHistory = QtGui.QCheckBox(self)
        self.saveHistory.setGeometry(QtCore.QRect(40, 20, 291, 22))
        self.saveHistory.setObjectName("saveHistory")
        self.fileautoaccept = QtGui.QCheckBox(self)
        self.fileautoaccept.setGeometry(QtCore.QRect(40, 60, 271, 22))
        self.fileautoaccept.setObjectName("fileautoaccept")
        self.typingNotifications = QtGui.QCheckBox(self)
        self.typingNotifications.setGeometry(QtCore.QRect(40, 100, 350, 30))
        self.typingNotifications.setObjectName("typingNotifications")
        self.inlines = QtGui.QCheckBox(self)
        self.inlines.setGeometry(QtCore.QRect(40, 140, 350, 30))
        self.inlines.setObjectName("inlines")


        self.auto_path = QtGui.QLabel(self)
        self.auto_path.setGeometry(QtCore.QRect(40, 190, 350, 30))
        self.path = QtGui.QPlainTextEdit(self)
        self.path.setGeometry(QtCore.QRect(10, 225, 330, 45))
        self.change_path = QtGui.QPushButton(self)
        self.change_path.setGeometry(QtCore.QRect(10, 280, 330, 30))
        settings = Settings.get_instance()
        self.typingNotifications.setChecked(settings['typing_notifications'])
        self.fileautoaccept.setChecked(settings['allow_auto_accept'])
        self.saveHistory.setChecked(settings['save_history'])
        self.inlines.setChecked(settings['allow_inline'])
        self.path.setPlainText(settings['auto_accept_path'] or curr_directory())
        self.change_path.clicked.connect(self.new_path)
        self.block_user_label = QtGui.QLabel(self)
        self.block_user_label.setGeometry(QtCore.QRect(10, 320, 330, 30))
        self.block_id = QtGui.QPlainTextEdit(self)
        self.block_id.setGeometry(QtCore.QRect(10, 350, 330, 30))
        self.block = QtGui.QPushButton(self)
        self.block.setGeometry(QtCore.QRect(10, 390, 330, 30))
        self.block.clicked.connect(lambda: Profile.get_instance().block_user(self.block_id.toPlainText()) or self.close())
        self.blocked_users_label = QtGui.QLabel(self)
        self.blocked_users_label.setGeometry(QtCore.QRect(10, 430, 330, 30))
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(10, 460, 330, 30))
        self.comboBox.addItems(settings['blocked'])
        self.unblock = QtGui.QPushButton(self)
        self.unblock.setGeometry(QtCore.QRect(10, 500, 330, 30))
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
        self.block_user_label.setText(QtGui.QApplication.translate("privacySettings", "Block by TOX ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.blocked_users_label.setText(QtGui.QApplication.translate("privacySettings", "Blocked users:", None, QtGui.QApplication.UnicodeUTF8))
        self.unblock.setText(QtGui.QApplication.translate("privacySettings", "Unblock", None, QtGui.QApplication.UnicodeUTF8))
        self.block.setText(QtGui.QApplication.translate("privacySettings", "Block user", None, QtGui.QApplication.UnicodeUTF8))

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
        settings['auto_accept_path'] = self.path.toPlainText()
        settings['allow_inline'] = self.inlines.isChecked()
        settings.save()

    def new_path(self):
        directory = QtGui.QFileDialog.getExistingDirectory() + '/'
        if directory != '/':
            self.path.setPlainText(directory)


class NotificationsSettings(CenteredWidget):
    """Notifications settings form"""

    def __init__(self):
        super(NotificationsSettings, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("notificationsForm")
        self.resize(350, 200)
        self.setMinimumSize(QtCore.QSize(350, 200))
        self.setMaximumSize(QtCore.QSize(350, 200))
        self.enableNotifications = QtGui.QCheckBox(self)
        self.enableNotifications.setGeometry(QtCore.QRect(10, 20, 340, 18))
        self.callsSound = QtGui.QCheckBox(self)
        self.callsSound.setGeometry(QtCore.QRect(10, 120, 340, 18))
        self.soundNotifications = QtGui.QCheckBox(self)
        self.soundNotifications.setGeometry(QtCore.QRect(10, 70, 340, 18))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
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

    def initUI(self):
        self.setObjectName("interfaceForm")
        self.resize(300, 300)
        self.setMinimumSize(QtCore.QSize(300, 300))
        self.setMaximumSize(QtCore.QSize(300, 300))
        self.setBaseSize(QtCore.QSize(300, 300))
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(30, 20, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.themeSelect = QtGui.QComboBox(self)
        self.themeSelect.setGeometry(QtCore.QRect(30, 60, 160, 30))
        self.themeSelect.setObjectName("themeSelect")
        list_of_themes = ['default', 'windows', 'gtk', 'cde', 'plastique', 'motif']
        self.themeSelect.addItems(list_of_themes)
        settings = Settings.get_instance()
        theme = settings['theme']
        index = list_of_themes.index(theme)
        self.themeSelect.setCurrentIndex(index)
        self.lang_choose = QtGui.QComboBox(self)
        self.lang_choose.setGeometry(QtCore.QRect(30, 150, 160, 30))
        self.lang_choose.setObjectName("comboBox")
        supported = Settings.supported_languages()
        for elem in supported:
            self.lang_choose.addItem(elem[0])
        lang = settings['language']
        index = map(lambda x: x[0], supported).index(lang)
        self.lang_choose.setCurrentIndex(index)
        self.lang = QtGui.QLabel(self)
        self.lang.setGeometry(QtCore.QRect(30, 110, 121, 31))
        self.lang.setFont(font)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("interfaceForm", "Interface settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("interfaceForm", "Theme:", None, QtGui.QApplication.UnicodeUTF8))
        self.lang.setText(QtGui.QApplication.translate("interfaceForm", "Language:", None, QtGui.QApplication.UnicodeUTF8))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        style = str(self.themeSelect.currentText())
        settings['theme'] = style
        QtGui.QApplication.setStyle(get_style(style))
        language = self.lang_choose.currentText()
        if settings['language'] != language:
            settings['language'] = language
            index = self.lang_choose.currentIndex()
            path = Settings.supported_languages()[index][1]
            app = QtGui.QApplication.instance()
            app.removeTranslator(app.translator)
            app.translator.load(curr_directory() + '/translations/' + path)
            app.installTranslator(app.translator)
        settings.save()


class AudioSettings(CenteredWidget):

    def __init__(self):
        super(AudioSettings, self).__init__()
        self.initUI()
        self.retranslateUi()

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
        for i in xrange(p.get_device_count()):
            device = p.get_device_info_by_index(i)
            if device["maxInputChannels"]:
                self.input.addItem(unicode(device["name"]))
                self.in_indexes.append(i)
            if device["maxOutputChannels"]:
                self.output.addItem(unicode(device["name"]))
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
