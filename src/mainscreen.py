# -*- coding: utf-8 -*-

from menu import *
from profile import *
from list_items import *
from widgets import QRightClickButton
import plugin_support


class MessageArea(QtGui.QPlainTextEdit):

    def __init__(self, parent, form):
        super(MessageArea, self).__init__(parent)
        self.parent = form
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.parent.profile.send_typing(False))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            modifiers = event.modifiers()
            if modifiers & QtCore.Qt.ControlModifier or modifiers & QtCore.Qt.ShiftModifier:
                self.appendPlainText('')
            else:
                if self.timer.isActive():
                    self.timer.stop()
                self.parent.profile.send_typing(False)
                self.parent.send_message()
        elif event.key() == QtCore.Qt.Key_Up and not self.toPlainText():
            self.appendPlainText(Profile.get_instance().get_last_message())
        else:
            self.parent.profile.send_typing(True)
            if self.timer.isActive():
                self.timer.stop()
            self.timer.start(5000)
            super(MessageArea, self).keyPressEvent(event)


class MainWindow(QtGui.QMainWindow):

    def __init__(self, tox, reset):
        super(MainWindow, self).__init__()
        self.reset = reset
        self.initUI(tox)

    def setup_menu(self, MainWindow):
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setNativeMenuBar(False)
        self.menubar.setMinimumSize(self.width(), 25)
        self.menubar.setMaximumSize(self.width(), 25)
        self.menubar.setBaseSize(self.width(), 25)

        self.menuProfile = QtGui.QMenu(self.menubar)
        self.menuProfile.setObjectName("menuProfile")
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuPlugins = QtGui.QMenu(self.menubar)
        self.menuPlugins.setObjectName("menuPlugins")
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")

        self.actionAdd_friend = QtGui.QAction(MainWindow)
        self.actionAdd_friend.setObjectName("actionAdd_friend")
        self.actionProfile_settings = QtGui.QAction(MainWindow)
        self.actionProfile_settings.setObjectName("actionProfile_settings")
        self.actionPrivacy_settings = QtGui.QAction(MainWindow)
        self.actionPrivacy_settings.setObjectName("actionPrivacy_settings")
        self.actionInterface_settings = QtGui.QAction(MainWindow)
        self.actionInterface_settings.setObjectName("actionInterface_settings")
        self.actionNotifications = QtGui.QAction(MainWindow)
        self.actionNotifications.setObjectName("actionNotifications")
        self.actionNetwork = QtGui.QAction(MainWindow)
        self.actionNetwork.setObjectName("actionNetwork")
        self.actionAbout_program = QtGui.QAction(MainWindow)
        self.actionAbout_program.setObjectName("actionAbout_program")
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.audioSettings = QtGui.QAction(MainWindow)
        self.pluginData = QtGui.QAction(MainWindow)
        self.menuProfile.addAction(self.actionAdd_friend)
        self.menuProfile.addAction(self.actionSettings)
        self.menuSettings.addAction(self.actionPrivacy_settings)
        self.menuSettings.addAction(self.actionInterface_settings)
        self.menuSettings.addAction(self.actionNotifications)
        self.menuSettings.addAction(self.actionNetwork)
        self.menuSettings.addAction(self.audioSettings)
        self.menuPlugins.addAction(self.pluginData)
        self.menuAbout.addAction(self.actionAbout_program)
        self.menubar.addAction(self.menuProfile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuPlugins.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.actionAbout_program.triggered.connect(self.about_program)
        self.actionNetwork.triggered.connect(self.network_settings)
        self.actionAdd_friend.triggered.connect(self.add_contact)
        self.actionSettings.triggered.connect(self.profile_settings)
        self.actionPrivacy_settings.triggered.connect(self.privacy_settings)
        self.actionInterface_settings.triggered.connect(self.interface_settings)
        self.actionNotifications.triggered.connect(self.notification_settings)
        self.audioSettings.triggered.connect(self.audio_settings)
        self.pluginData.triggered.connect(self.plugins_menu)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def languageChange(self, *args, **kwargs):
        self.retranslateUi()

    def retranslateUi(self):
        self.menuPlugins.setTitle(QtGui.QApplication.translate("MainWindow", "Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginData.setText(QtGui.QApplication.translate("MainWindow", "List of plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.menuProfile.setTitle(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAbout.setTitle(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd_friend.setText(QtGui.QApplication.translate("MainWindow", "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProfile_settings.setText(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrivacy_settings.setText(QtGui.QApplication.translate("MainWindow", "Privacy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInterface_settings.setText(QtGui.QApplication.translate("MainWindow", "Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNotifications.setText(QtGui.QApplication.translate("MainWindow", "Notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNetwork.setText(QtGui.QApplication.translate("MainWindow", "Network", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_program.setText(QtGui.QApplication.translate("MainWindow", "About program", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.audioSettings.setText(QtGui.QApplication.translate("MainWindow", "Audio", None, QtGui.QApplication.UnicodeUTF8))
        self.contact_name.setPlaceholderText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.screenshotButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Send screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.fileTransferButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Send file", None, QtGui.QApplication.UnicodeUTF8))
        self.sendMessageButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Send message", None, QtGui.QApplication.UnicodeUTF8))
        self.callButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Start audio call with friend", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.clear()
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Online", None, QtGui.QApplication.UnicodeUTF8))

    def setup_right_bottom(self, Form):
        Form.setObjectName("right_bottom")
        Form.resize(650, 60)
        self.messageEdit = MessageArea(Form, self)
        self.messageEdit.setGeometry(QtCore.QRect(0, 3, 450, 55))
        self.messageEdit.setObjectName("messageEdit")
        font = QtGui.QFont()
        font.setPointSize(10)
        self.messageEdit.setFont(font)

        self.screenshotButton = QRightClickButton(Form)
        self.screenshotButton.setGeometry(QtCore.QRect(455, 3, 55, 55))
        self.screenshotButton.setObjectName("screenshotButton")

        self.fileTransferButton = QtGui.QPushButton(Form)
        self.fileTransferButton.setGeometry(QtCore.QRect(510, 3, 55, 55))
        self.fileTransferButton.setObjectName("fileTransferButton")

        self.sendMessageButton = QtGui.QPushButton(Form)
        self.sendMessageButton.setGeometry(QtCore.QRect(565, 3, 60, 55))
        self.sendMessageButton.setObjectName("sendMessageButton")

        pixmap = QtGui.QPixmap(curr_directory() + '/images/send.png')
        icon = QtGui.QIcon(pixmap)
        self.sendMessageButton.setIcon(icon)
        self.sendMessageButton.setIconSize(QtCore.QSize(45, 60))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/file.png')
        icon = QtGui.QIcon(pixmap)
        self.fileTransferButton.setIcon(icon)
        self.fileTransferButton.setIconSize(QtCore.QSize(40, 40))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/screenshot.png')
        icon = QtGui.QIcon(pixmap)
        self.screenshotButton.setIcon(icon)
        self.screenshotButton.setIconSize(QtCore.QSize(40, 60))

        self.fileTransferButton.clicked.connect(self.send_file)
        self.screenshotButton.clicked.connect(self.send_screenshot)
        self.sendMessageButton.clicked.connect(self.send_message)
        self.connect(self.screenshotButton, QtCore.SIGNAL("rightClicked()"), lambda: self.send_screenshot(True))

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_center_menu(self, Form):
        Form.resize(270, 25)
        self.search_label = QtGui.QLabel(Form)
        self.search_label.setGeometry(QtCore.QRect(3, 0, 25, 25))
        pixmap = QtGui.QPixmap(QtCore.QSize(25, 25))
        pixmap.load(curr_directory() + '/images/search.png')
        self.search_label.setScaledContents(False)
        self.search_label.setPixmap(pixmap.scaled(25, 25, QtCore.Qt.KeepAspectRatio))

        self.contact_name = QtGui.QLineEdit(Form)
        self.contact_name.setGeometry(QtCore.QRect(30, 0, 120, 25))
        self.contact_name.setObjectName("contact_name")
        self.contact_name.textChanged.connect(self.filtering)
        self.online_contacts = QtGui.QComboBox(Form)
        self.online_contacts.setGeometry(QtCore.QRect(150, 0, 120, 25))
        self.online_contacts.activated[int].connect(lambda x: self.filtering())

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_top(self, Form):
        Form.setObjectName("left_top")
        Form.setCursor(QtCore.Qt.PointingHandCursor)
        Form.setMinimumSize(QtCore.QSize(250, 80))
        Form.setMaximumSize(QtCore.QSize(250, 80))
        Form.setBaseSize(QtCore.QSize(250, 80))
        self.avatar_label = Form.avatar_label = QtGui.QLabel(Form)
        self.avatar_label.setGeometry(QtCore.QRect(5, 15, 64, 64))
        self.avatar_label.setScaledContents(True)
        self.name = Form.name = DataLabel(Form)
        Form.name.setGeometry(QtCore.QRect(80, 25, 150, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(True)
        Form.name.setFont(font)
        Form.name.setObjectName("name")
        self.status_message = Form.status_message = DataLabel(Form)
        Form.status_message.setGeometry(QtCore.QRect(80, 55, 170, 20))
        font.setPointSize(12)
        font.setBold(False)
        Form.status_message.setFont(font)
        Form.status_message.setObjectName("status_message")
        self.connection_status = Form.connection_status = StatusCircle(self)
        Form.connection_status.setGeometry(QtCore.QRect(230, 29, 64, 64))
        Form.connection_status.setMinimumSize(QtCore.QSize(32, 32))
        Form.connection_status.setMaximumSize(QtCore.QSize(32, 32))
        Form.connection_status.setBaseSize(QtCore.QSize(32, 32))
        self.avatar_label.mouseReleaseEvent = self.profile_settings
        self.status_message.mouseReleaseEvent = self.profile_settings
        self.name.mouseReleaseEvent = self.profile_settings
        self.connection_status.raise_()
        Form.connection_status.setObjectName("connection_status")

    def setup_right_top(self, Form):
        Form.setObjectName("Form")
        Form.resize(650, 80)
        self.account_avatar = QtGui.QLabel(Form)
        self.account_avatar.setGeometry(QtCore.QRect(10, 17, 64, 64))
        self.account_avatar.setScaledContents(True)
        self.account_name = DataLabel(Form)
        self.account_name.setGeometry(QtCore.QRect(100, 25, 400, 25))
        self.account_name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(True)
        self.account_name.setFont(font)
        self.account_name.setObjectName("account_name")
        self.account_status = DataLabel(Form)
        self.account_status.setGeometry(QtCore.QRect(100, 45, 400, 25))
        self.account_status.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font.setPointSize(12)
        font.setBold(False)
        self.account_status.setFont(font)
        self.account_status.setObjectName("account_status")
        self.callButton = QtGui.QPushButton(Form)
        self.callButton.setGeometry(QtCore.QRect(550, 30, 50, 50))
        self.callButton.setObjectName("callButton")
        self.callButton.clicked.connect(self.call)
        self.update_call_state('call')
        self.typing = QtGui.QLabel(Form)
        self.typing.setGeometry(QtCore.QRect(500, 40, 50, 30))
        pixmap = QtGui.QPixmap(QtCore.QSize(50, 30))
        pixmap.load(curr_directory() + '/images/typing.png')
        self.typing.setScaledContents(False)
        self.typing.setPixmap(pixmap.scaled(50, 30, QtCore.Qt.KeepAspectRatio))
        self.typing.setVisible(False)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_center(self, widget):
        self.friends_list = QtGui.QListWidget(widget)
        self.friends_list.setObjectName("friends_list")
        self.friends_list.setGeometry(0, 0, 270, 310)
        self.friends_list.clicked.connect(self.friend_click)
        self.friends_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.friends_list.connect(self.friends_list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                                  self.friend_right_click)
        self.friends_list.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def setup_right_center(self, widget):
        self.messages = QtGui.QListWidget(widget)
        self.messages.setGeometry(0, 0, 620, 310)
        self.messages.setObjectName("messages")
        self.messages.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.messages.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.messages.setFocusPolicy(QtCore.Qt.NoFocus)

        def load(pos):
            if not pos:
                self.profile.load_history()
                self.messages.verticalScrollBar().setValue(1)
        self.messages.verticalScrollBar().valueChanged.connect(load)
        self.messages.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

    def initUI(self, tox):
        self.setMinimumSize(920, 500)
        self.setGeometry(400, 400, 920, 500)
        self.setWindowTitle('Toxygen')
        os.chdir(curr_directory() + '/images/')
        main = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        search = QtGui.QWidget()
        self.setup_left_center_menu(search)
        grid.addWidget(search, 1, 0)
        name = QtGui.QWidget()
        self.setup_left_top(name)
        grid.addWidget(name, 0, 0)
        messages = QtGui.QWidget()
        self.setup_right_center(messages)
        grid.addWidget(messages, 1, 1, 2, 1)
        info = QtGui.QWidget()
        self.setup_right_top(info)
        grid.addWidget(info, 0, 1)
        message_buttons = QtGui.QWidget()
        self.setup_right_bottom(message_buttons)
        grid.addWidget(message_buttons, 3, 1)
        main_list = QtGui.QWidget()
        self.setup_left_center(main_list)
        grid.addWidget(main_list, 2, 0, 2, 1)
        grid.setColumnMinimumWidth(1, 500)
        grid.setColumnMinimumWidth(0, 270)
        grid.setRowMinimumHeight(0, 82)
        grid.setRowMinimumHeight(1, 25)
        grid.setRowMinimumHeight(2, 410)
        grid.setRowMinimumHeight(3, 60)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)
        main.setLayout(grid)
        self.setCentralWidget(main)
        self.setup_menu(self)
        self.messageEdit.setFocus()
        self.user_info = name
        self.friend_info = info
        self.retranslateUi()
        self.profile = Profile(tox, self)

    def closeEvent(self, *args, **kwargs):
        self.profile.save_history()
        self.profile.close()
        QtGui.QApplication.closeAllWindows()

    def resizeEvent(self, *args, **kwargs):
        self.messages.setGeometry(0, 0, self.width() - 300, self.height() - 172)
        self.friends_list.setGeometry(0, 0, 270, self.height() - 142)
        self.callButton.setGeometry(QtCore.QRect(self.width() - 370, 20, 50, 50))
        self.typing.setGeometry(QtCore.QRect(self.width() - 420, 30, 50, 30))

        self.messageEdit.setGeometry(QtCore.QRect(120, 2, self.width() - 490, 55))
        self.screenshotButton.setGeometry(QtCore.QRect(0, 2, 55, 55))
        self.fileTransferButton.setGeometry(QtCore.QRect(60, 2, 55, 55))
        self.sendMessageButton.setGeometry(QtCore.QRect(self.width() - 360, 2, 60, 55))

        self.account_name.setGeometry(QtCore.QRect(100, 30, self.width() - 520, 25))
        self.account_status.setGeometry(QtCore.QRect(100, 50, self.width() - 520, 25))
        self.profile.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        else:
            super(MainWindow, self).keyPressEvent(event)

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user click in menu
    # -----------------------------------------------------------------------------------------------------------------

    def about_program(self):
        import util
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        text = (QtGui.QApplication.translate("MainWindow", 'Toxygen is Tox client written on Python.\nVersion: ', None, QtGui.QApplication.UnicodeUTF8))
        msgBox.setText(text + util.program_version + '\nGitHub: github.com/xveduk/toxygen/')
        msgBox.exec_()

    def network_settings(self):
        self.n_s = NetworkSettings(self.reset)
        self.n_s.show()

    def plugins_menu(self):
        self.p_s = PluginsSettings()
        self.p_s.show()

    def add_contact(self):
        self.a_c = AddContact()
        self.a_c.show()

    def profile_settings(self, *args):
        self.p_s = ProfileSettings()
        self.p_s.show()

    def privacy_settings(self):
        self.priv_s = PrivacySettings()
        self.priv_s.show()

    def notification_settings(self):
        self.notif_s = NotificationsSettings()
        self.notif_s.show()

    def interface_settings(self):
        self.int_s = InterfaceSettings()
        self.int_s.show()

    def audio_settings(self):
        self.audio_s = AudioSettings()
        self.audio_s.show()

    # -----------------------------------------------------------------------------------------------------------------
    # Messages, calls and file transfers
    # -----------------------------------------------------------------------------------------------------------------

    def send_message(self):
        text = self.messageEdit.toPlainText()
        self.profile.send_message(text)

    def send_file(self):
        if self.profile.is_active_online():  # active friend exists and online
            choose_file = QtGui.QApplication.translate("MainWindow", 'Choose file', None, QtGui.QApplication.UnicodeUTF8)
            choose = QtGui.QApplication.translate("MainWindow", choose_file, None, QtGui.QApplication.UnicodeUTF8)
            name = QtGui.QFileDialog.getOpenFileName(self, choose)
            if name[0]:
                self.profile.send_file(name[0])

    def send_screenshot(self, hide=False):
        if self.profile.is_active_online():  # active friend exists and online
            self.sw = ScreenShotWindow(self)
            self.sw.show()
            if hide:
                self.hide()

    def call(self):
        if self.profile.is_active_online():  # active friend exists and online
            self.profile.call_click(True)

    def active_call(self):
        self.update_call_state('finish_call')

    def incoming_call(self):
        self.update_call_state('incoming_call')

    def call_finished(self):
        self.update_call_state('call')

    def update_call_state(self, fl):
        pixmap = QtGui.QPixmap(curr_directory() + '/images/{}.png'.format(fl))
        icon = QtGui.QIcon(pixmap)
        self.callButton.setIcon(icon)
        self.callButton.setIconSize(QtCore.QSize(50, 50))

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user open context menu in friends list
    # -----------------------------------------------------------------------------------------------------------------

    def friend_right_click(self, pos):
        item = self.friends_list.itemAt(pos)
        num = self.friends_list.indexFromItem(item).row()
        friend = Profile.get_instance().get_friend(num)
        settings = Settings.get_instance()
        allowed = friend.tox_id in settings['auto_accept_from_friends']
        auto = QtGui.QApplication.translate("MainWindow", 'Disallow auto accept', None, QtGui.QApplication.UnicodeUTF8) if allowed else QtGui.QApplication.translate("MainWindow", 'Allow auto accept', None, QtGui.QApplication.UnicodeUTF8)
        if item is not None:
            self.listMenu = QtGui.QMenu()
            set_alias_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Set alias', None, QtGui.QApplication.UnicodeUTF8))
            clear_history_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Clear history', None, QtGui.QApplication.UnicodeUTF8))
            copy_key_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Copy public key', None, QtGui.QApplication.UnicodeUTF8))
            auto_accept_item = self.listMenu.addAction(auto)
            remove_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Remove friend', None, QtGui.QApplication.UnicodeUTF8))
            submenu = plugin_support.PluginLoader.get_instance().get_menu(self.listMenu, num)
            if len(submenu):
                plug = self.listMenu.addMenu(QtGui.QApplication.translate("MainWindow", 'Plugins', None, QtGui.QApplication.UnicodeUTF8))
                plug.addActions(submenu)
            self.connect(set_alias_item, QtCore.SIGNAL("triggered()"), lambda: self.set_alias(num))
            self.connect(remove_item, QtCore.SIGNAL("triggered()"), lambda: self.remove_friend(num))
            self.connect(copy_key_item, QtCore.SIGNAL("triggered()"), lambda: self.copy_friend_key(num))
            self.connect(clear_history_item, QtCore.SIGNAL("triggered()"), lambda: self.clear_history(num))
            self.connect(auto_accept_item, QtCore.SIGNAL("triggered()"), lambda: self.auto_accept(num, not allowed))
            parent_position = self.friends_list.mapToGlobal(QtCore.QPoint(0, 0))
            self.listMenu.move(parent_position + pos)
            self.listMenu.show()

    def set_alias(self, num):
        self.profile.set_alias(num)

    def remove_friend(self, num):
        self.profile.delete_friend(num)

    def copy_friend_key(self, num):
        tox_id = self.profile.friend_public_key(num)
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(tox_id)

    def clear_history(self, num):
        self.profile.clear_history(num)

    def auto_accept(self, num, value):
        settings = Settings.get_instance()
        tox_id = self.profile.friend_public_key(num)
        if value:
            settings['auto_accept_from_friends'].append(tox_id)
        else:
            settings['auto_accept_from_friends'].remove(tox_id)
        settings.save()

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user click somewhere else
    # -----------------------------------------------------------------------------------------------------------------

    def friend_click(self, index):
        num = index.row()
        self.profile.set_active(num)

    def mouseReleaseEvent(self, event):
        x, y = event.x(), event.y()
        pos = self.connection_status.pos()
        if (pos.x() < x < pos.x() + 32) and (pos.y() < y < pos.y() + 32):
            self.profile.change_status()
        else:
            super(self.__class__, self).mouseReleaseEvent(event)

    def filtering(self):
        self.profile.filtration(self.online_contacts.currentIndex() == 1, self.contact_name.text())


class ScreenShotWindow(QtGui.QWidget):

    def __init__(self, parent):
        super(ScreenShotWindow, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setWindowOpacity(0.5)
        self.rubberband = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, None)

    def closeEvent(self, *args):
        if self.parent.isHidden():
            self.parent.show()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            left = QtGui.QRegion(QtCore.QRect(0, 0, self.rubberband.x(), self.height()))
            right = QtGui.QRegion(QtCore.QRect(self.rubberband.x() + self.rubberband.width(), 0, self.width(), self.height()))
            top = QtGui.QRegion(0, 0, self.width(), self.rubberband.y())
            bottom = QtGui.QRegion(0, self.rubberband.y() + self.rubberband.height(), self.width(), self.height())
            self.setMask(left + right + top + bottom)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            print rect
            if rect.width() and rect.height():
                p = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),
                                             rect.x() + 4,
                                             rect.y() + 4,
                                             rect.width() - 8,
                                             rect.height() - 8)
                byte_array = QtCore.QByteArray()
                buffer = QtCore.QBuffer(byte_array)
                buffer.open(QtCore.QIODevice.WriteOnly)
                p.save(buffer, 'PNG')
                Profile.get_instance().send_screenshot(str(byte_array.data()))
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.rubberband.setHidden(True)
            self.close()
        else:
            super(ScreenShotWindow, self).keyPressEvent(event)



