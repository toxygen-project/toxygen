from PySide import QtCore, QtGui
from settings import Settings
from profile import Profile, ProfileHelper
from util import get_style


class CenteredWidget(QtGui.QWidget):
    def __init__(self):
        super(CenteredWidget, self).__init__()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


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
        self.label.setGeometry(QtCore.QRect(30, 10, 80, 20))
        self.error_label = QtGui.QLabel(self)
        self.error_label.setGeometry(QtCore.QRect(120, 10, 400, 20))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(40)
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
        QtCore.QMetaObject.connectSlotsByName(self)

    def add_friend(self):
        profile = Profile.get_instance()
        send = profile.send_friend_request(self.tox_id.text(), self.message_edit.toPlainText())
        if send is True:
            # request was successful
            self.close()
        else:  # print error data
            if len(send) > 40:
                send = send[:40] + '...'
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
        self.setMinimumSize(QtCore.QSize(650, 400))
        self.setMaximumSize(QtCore.QSize(650, 400))
        self.nick = QtGui.QLineEdit(self)
        self.nick.setGeometry(QtCore.QRect(30, 60, 351, 27))
        self.nick.setObjectName("nick")
        profile = Profile.get_instance()
        self.nick.setText(profile.name)
        self.status = QtGui.QLineEdit(self)
        self.status.setGeometry(QtCore.QRect(30, 130, 351, 27))
        self.status.setObjectName("status")
        self.status.setText(profile.status_message)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 30, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(50, 100, 91, 21))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(50, 170, 91, 21))
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
        self.copyId.setGeometry(QtCore.QRect(40, 250, 100, 30))
        self.copyId.setObjectName("copyId")
        self.copyId.clicked.connect(self.copy)
        self.export = QtGui.QPushButton(self)
        self.export.setGeometry(QtCore.QRect(150, 250, 100, 30))
        self.export.setObjectName("export")
        self.export.clicked.connect(self.export_profile)
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.setGeometry(QtCore.QRect(30, 350, 211, 27))
        self.comboBox.setObjectName("comboBox")
        self.tox_id_2 = QtGui.QLabel(self)
        self.tox_id_2.setGeometry(QtCore.QRect(40, 310, 121, 31))
        font.setPointSize(18)
        self.tox_id_2.setFont(font)
        self.tox_id_2.setObjectName("tox_id_2")
        self.new_avatar = QtGui.QPushButton(self)
        self.new_avatar.setGeometry(QtCore.QRect(400, 50, 200, 50))
        self.delete_avatar = QtGui.QPushButton(self)
        self.delete_avatar.setGeometry(QtCore.QRect(400, 100, 200, 50))
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
        self.tox_id_2.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Language:", None, QtGui.QApplication.UnicodeUTF8))
        self.new_avatar.setText(QtGui.QApplication.translate("ProfileSettingsForm", "New avatar", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_avatar.setText(QtGui.QApplication.translate("ProfileSettingsForm", "Reset avatar", None, QtGui.QApplication.UnicodeUTF8))

    def copy(self):
        clipboard = QtGui.QApplication.clipboard()
        profile = Profile.get_instance()
        clipboard.setText(profile.tox_id)

    def reset_avatar(self):
        Profile.get_instance().reset_avatar()

    def set_avatar(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
        print name
        if name[0]:
            with open(name[0], 'rb') as f:
                data = f.read()
            Profile.get_instance().set_avatar(data)

    def export_profile(self):
        # TODO: export history
        directory = QtGui.QFileDialog.getExistingDirectory() + '/'
        ProfileHelper.export_profile(directory)
        settings = Settings.get_instance()
        settings.export(directory)

    def closeEvent(self, event):
        profile = Profile.get_instance()
        profile.set_name(self.nick.text().encode('utf-8'))
        profile.set_status_message(self.status.text().encode('utf-8'))


class NetworkSettings(CenteredWidget):
    """Network settings form: UDP, Ipv6 and proxy"""
    # TODO: add possibility to change network settings
    def __init__(self, reset):
        super(NetworkSettings, self).__init__()
        self.reset = reset
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
        self.udp.setGeometry(QtCore.QRect(20, 50, 97, 22))
        self.udp.setObjectName("udp")
        self.proxy = QtGui.QCheckBox(self)
        self.proxy.setGeometry(QtCore.QRect(20, 90, 97, 22))
        self.proxy.setObjectName("proxy")
        self.proxyip = QtGui.QLineEdit(self)
        self.proxyip.setGeometry(QtCore.QRect(40, 160, 231, 27))
        self.proxyip.setObjectName("proxyip")
        self.proxyport = QtGui.QLineEdit(self)
        self.proxyport.setGeometry(QtCore.QRect(40, 220, 231, 27))
        self.proxyport.setObjectName("proxyport")
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(40, 130, 66, 17))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(40, 190, 66, 17))
        self.label_2.setObjectName("label_2")
        settings = Settings.get_instance()
        self.ipv.setChecked(settings['ipv6_enabled'])
        self.udp.setChecked(settings['udp_enabled'])
        self.proxy.setChecked(settings['proxy_type'] != 0)
        self.proxyip.setText(settings['proxy_host'])
        self.proxyport.setText(unicode(settings['proxy_port']))
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("NetworkSettings", "Network settings", None, QtGui.QApplication.UnicodeUTF8))
        self.ipv.setText(QtGui.QApplication.translate("Form", "IPv6", None, QtGui.QApplication.UnicodeUTF8))
        self.udp.setText(QtGui.QApplication.translate("Form", "UDP", None, QtGui.QApplication.UnicodeUTF8))
        self.proxy.setText(QtGui.QApplication.translate("Form", "Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "IP:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Port:", None, QtGui.QApplication.UnicodeUTF8))

    def closeEvent(self, *args, **kwargs):
        settings = Settings.get_instance()
        old_data = str(settings['ipv6_enabled']) + str(settings['udp_enabled']) + str(bool(settings['proxy_type']))
        new_data = str(self.ipv.isChecked()) + str(self.udp.isChecked()) + str(self.proxy.isChecked())
        changed = old_data != new_data
        if self.proxy.isChecked() and (self.proxyip.text() != settings['proxy_host'] or self.proxyport.text() != settings['proxy_port']):
            changed = True
        if changed:
            settings['ipv6_enabled'] = self.ipv.isChecked()
            settings['udp_enabled'] = self.udp.isChecked()
            settings['proxy_type'] = int(self.proxy.isChecked())
            settings['proxy_host'] = self.proxyip.text()
            settings['proxy_port'] = int(self.proxyport.text())
            settings.save()
            # recreate tox instance
            Profile.get_instance().reset(self.reset)


class PrivacySettings(CenteredWidget):
    """Privacy settings form: history, typing notifications"""

    def __init__(self):
        super(PrivacySettings, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("privacySettings")
        self.resize(350, 200)
        self.setMinimumSize(QtCore.QSize(350, 200))
        self.setMaximumSize(QtCore.QSize(350, 200))
        self.setBaseSize(QtCore.QSize(350, 200))
        self.saveHistory = QtGui.QCheckBox(self)
        self.saveHistory.setGeometry(QtCore.QRect(40, 20, 291, 22))
        self.saveHistory.setObjectName("saveHistory")
        self.fileautoaccept = QtGui.QCheckBox(self)
        self.fileautoaccept.setGeometry(QtCore.QRect(40, 60, 271, 22))
        self.fileautoaccept.setObjectName("fileautoaccept")
        self.typingNotifications = QtGui.QCheckBox(self)
        self.typingNotifications.setGeometry(QtCore.QRect(40, 90, 350, 31))
        self.typingNotifications.setBaseSize(QtCore.QSize(350, 200))
        self.typingNotifications.setObjectName("typingNotifications")

        self.retranslateUi()
        settings = Settings.get_instance()
        self.typingNotifications.setChecked(settings['typing_notifications'])
        self.fileautoaccept.setChecked(settings['allow_auto_accept'])
        self.saveHistory.setChecked(settings['save_history'])
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("privacySettings", "Privacy settings", None, QtGui.QApplication.UnicodeUTF8))
        self.saveHistory.setText(QtGui.QApplication.translate("privacySettings", "Save chat history", None, QtGui.QApplication.UnicodeUTF8))
        self.fileautoaccept.setText(QtGui.QApplication.translate("privacySettings", "Allow file autoaccept", None, QtGui.QApplication.UnicodeUTF8))
        self.typingNotifications.setText(QtGui.QApplication.translate("privacySettings", "Send typing notifications", None, QtGui.QApplication.UnicodeUTF8))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        settings['typing_notifications'] = self.typingNotifications.isChecked()
        settings['allow_auto_accept'] = self.fileautoaccept.isChecked()
        if settings['save_history'] and not self.saveHistory.isChecked():  # clear history
            Profile.get_instance().clear_history()
        settings['save_history'] = self.saveHistory.isChecked()
        settings.save()


class NotificationsSettings(CenteredWidget):
    """Notifications settings form"""

    def __init__(self):
        super(NotificationsSettings, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName("notificationsForm")
        self.resize(300, 200)
        self.setMinimumSize(QtCore.QSize(300, 200))
        self.setMaximumSize(QtCore.QSize(300, 200))
        self.setBaseSize(QtCore.QSize(300, 200))
        self.enableNotifications = QtGui.QCheckBox(self)
        self.enableNotifications.setGeometry(QtCore.QRect(30, 20, 241, 22))
        self.enableNotifications.setObjectName("enableNotifications")
        self.soundNotifications = QtGui.QCheckBox(self)
        self.soundNotifications.setGeometry(QtCore.QRect(30, 100, 231, 22))
        self.soundNotifications.setObjectName("sound_notifications")
        self.callsSound = QtGui.QCheckBox(self)
        self.callsSound.setGeometry(QtCore.QRect(30, 60, 231, 22))
        self.callsSound.setObjectName("calls_sound")
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
        self.themeSelect.setGeometry(QtCore.QRect(30, 60, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.themeSelect.setFont(font)
        self.themeSelect.setObjectName("themeSelect")
        list_of_themes = ['default', 'windows', 'gtk', 'cde', 'plastique', 'motif']
        self.themeSelect.addItems(list_of_themes)
        theme = Settings.get_instance()['theme']
        index = list_of_themes.index(theme)
        self.themeSelect.setCurrentIndex(index)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("interfaceForm", "Interface settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("interfaceForm", "Theme:", None, QtGui.QApplication.UnicodeUTF8))

    def closeEvent(self, event):
        settings = Settings.get_instance()
        style = str(self.themeSelect.currentText())
        settings['theme'] = style
        settings.save()
        QtGui.QApplication.setStyle(get_style(style))
