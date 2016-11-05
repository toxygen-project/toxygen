from menu import *
from profile import *
from list_items import *
from widgets import MultilineEdit, LineEdit, ComboBox
import plugin_support
from mainscreen_widgets import *
import settings


class MainWindow(QtGui.QMainWindow, Singleton):

    def __init__(self, tox, reset, tray):
        super().__init__()
        Singleton.__init__(self)
        self.reset = reset
        self.tray = tray
        self.setAcceptDrops(True)
        self.initUI(tox)
        self._saved = False
        if settings.Settings.get_instance()['show_welcome_screen']:
            self.ws = WelcomeScreen()

    def setup_menu(self, Form):
        box = QtGui.QHBoxLayout()
        box.setContentsMargins(0, 0, 0, 0)
        box.setAlignment(QtCore.Qt.AlignLeft)
        self.profile_button = MainMenuButton(Form)
        box.addWidget(self.profile_button)
        self.settings_button = MainMenuButton(Form)
        box.addWidget(self.settings_button)
        self.plugins_button = MainMenuButton(Form)
        box.addWidget(self.plugins_button)
        self.about_button = MainMenuButton(Form)
        box.addWidget(self.about_button)
        box.setSpacing(0)

        self.menuProfile = QtGui.QMenu()
        self.menuProfile.setObjectName("menuProfile")
        self.menuSettings = QtGui.QMenu()
        self.menuSettings.setObjectName("menuSettings")
        self.menuPlugins = QtGui.QMenu()
        self.menuPlugins.setObjectName("menuPlugins")
        self.menuAbout = QtGui.QMenu()
        self.menuAbout.setObjectName("menuAbout")

        self.actionAdd_friend = QtGui.QAction(Form)
        self.actionAdd_friend.setObjectName("actionAdd_friend")
        self.actionprofilesettings = QtGui.QAction(Form)
        self.actionprofilesettings.setObjectName("actionprofilesettings")
        self.actionPrivacy_settings = QtGui.QAction(Form)
        self.actionPrivacy_settings.setObjectName("actionPrivacy_settings")
        self.actionInterface_settings = QtGui.QAction(Form)
        self.actionInterface_settings.setObjectName("actionInterface_settings")
        self.actionNotifications = QtGui.QAction(Form)
        self.actionNotifications.setObjectName("actionNotifications")
        self.actionNetwork = QtGui.QAction(Form)
        self.actionNetwork.setObjectName("actionNetwork")
        self.actionAbout_program = QtGui.QAction(Form)
        self.actionAbout_program.setObjectName("actionAbout_program")
        self.updateSettings = QtGui.QAction(Form)
        self.actionSettings = QtGui.QAction(Form)
        self.actionSettings.setObjectName("actionSettings")
        self.audioSettings = QtGui.QAction(Form)
        self.pluginData = QtGui.QAction(Form)
        self.importPlugin = QtGui.QAction(Form)
        self.lockApp = QtGui.QAction(Form)
        self.menuProfile.addAction(self.actionAdd_friend)
        self.menuProfile.addAction(self.actionSettings)
        self.menuProfile.addAction(self.lockApp)
        self.menuSettings.addAction(self.actionPrivacy_settings)
        self.menuSettings.addAction(self.actionInterface_settings)
        self.menuSettings.addAction(self.actionNotifications)
        self.menuSettings.addAction(self.actionNetwork)
        self.menuSettings.addAction(self.audioSettings)
        self.menuSettings.addAction(self.updateSettings)
        self.menuPlugins.addAction(self.pluginData)
        self.menuPlugins.addAction(self.importPlugin)
        self.menuAbout.addAction(self.actionAbout_program)

        self.profile_button.setMenu(self.menuProfile)
        self.settings_button.setMenu(self.menuSettings)
        self.plugins_button.setMenu(self.menuPlugins)
        self.about_button.setMenu(self.menuAbout)

        self.actionAbout_program.triggered.connect(self.about_program)
        self.actionNetwork.triggered.connect(self.network_settings)
        self.actionAdd_friend.triggered.connect(self.add_contact)
        self.actionSettings.triggered.connect(self.profile_settings)
        self.actionPrivacy_settings.triggered.connect(self.privacy_settings)
        self.actionInterface_settings.triggered.connect(self.interface_settings)
        self.actionNotifications.triggered.connect(self.notification_settings)
        self.audioSettings.triggered.connect(self.audio_settings)
        self.updateSettings.triggered.connect(self.update_settings)
        self.pluginData.triggered.connect(self.plugins_menu)
        self.lockApp.triggered.connect(self.lock_app)
        self.importPlugin.triggered.connect(self.import_plugin)

        Form.setLayout(box)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def languageChange(self, *args, **kwargs):
        self.retranslateUi()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.tray.setIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
            self.messages.repaint()
        return super(MainWindow, self).event(event)

    def retranslateUi(self):
        self.lockApp.setText(QtGui.QApplication.translate("MainWindow", "Lock", None, QtGui.QApplication.UnicodeUTF8))
        self.plugins_button.setText(QtGui.QApplication.translate("MainWindow", "Plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.pluginData.setText(QtGui.QApplication.translate("MainWindow", "List of plugins", None, QtGui.QApplication.UnicodeUTF8))
        self.profile_button.setText(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.settings_button.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.about_button.setText(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd_friend.setText(QtGui.QApplication.translate("MainWindow", "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.actionprofilesettings.setText(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrivacy_settings.setText(QtGui.QApplication.translate("MainWindow", "Privacy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInterface_settings.setText(QtGui.QApplication.translate("MainWindow", "Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNotifications.setText(QtGui.QApplication.translate("MainWindow", "Notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNetwork.setText(QtGui.QApplication.translate("MainWindow", "Network", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_program.setText(QtGui.QApplication.translate("MainWindow", "About program", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.audioSettings.setText(QtGui.QApplication.translate("MainWindow", "Audio", None, QtGui.QApplication.UnicodeUTF8))
        self.updateSettings.setText(QtGui.QApplication.translate("MainWindow", "Updates", None, QtGui.QApplication.UnicodeUTF8))
        self.contact_name.setPlaceholderText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.sendMessageButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Send message", None, QtGui.QApplication.UnicodeUTF8))
        self.callButton.setToolTip(QtGui.QApplication.translate("MainWindow", "Start audio call with friend", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.clear()
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Online", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Online first", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Online and by name", None, QtGui.QApplication.UnicodeUTF8))
        self.online_contacts.addItem(QtGui.QApplication.translate("MainWindow", "Online first and by name", None, QtGui.QApplication.UnicodeUTF8))
        ind = Settings.get_instance()['sorting']
        d = {0: 0, 1: 1, 2: 2, 3: 4, 1 | 4: 4, 2 | 4: 5}
        self.online_contacts.setCurrentIndex(d[ind])
        self.importPlugin.setText(QtGui.QApplication.translate("MainWindow", "Import plugin", None, QtGui.QApplication.UnicodeUTF8))

    def setup_right_bottom(self, Form):
        Form.resize(650, 60)
        self.messageEdit = MessageArea(Form, self)
        self.messageEdit.setGeometry(QtCore.QRect(0, 3, 450, 55))
        self.messageEdit.setObjectName("messageEdit")
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setFamily(settings.Settings.get_instance()['font'])
        self.messageEdit.setFont(font)

        self.sendMessageButton = QtGui.QPushButton(Form)
        self.sendMessageButton.setGeometry(QtCore.QRect(565, 3, 60, 55))
        self.sendMessageButton.setObjectName("sendMessageButton")

        self.menuButton = MenuButton(Form, self.show_menu)
        self.menuButton.setGeometry(QtCore.QRect(QtCore.QRect(455, 3, 55, 55)))

        pixmap = QtGui.QPixmap('send.png')
        icon = QtGui.QIcon(pixmap)
        self.sendMessageButton.setIcon(icon)
        self.sendMessageButton.setIconSize(QtCore.QSize(45, 60))

        pixmap = QtGui.QPixmap('menu.png')
        icon = QtGui.QIcon(pixmap)
        self.menuButton.setIcon(icon)
        self.menuButton.setIconSize(QtCore.QSize(40, 40))

        self.sendMessageButton.clicked.connect(self.send_message)

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_center_menu(self, Form):
        Form.resize(270, 25)
        self.search_label = QtGui.QLabel(Form)
        self.search_label.setGeometry(QtCore.QRect(3, 2, 20, 20))
        pixmap = QtGui.QPixmap()
        pixmap.load(curr_directory() + '/images/search.png')
        self.search_label.setScaledContents(False)
        self.search_label.setPixmap(pixmap)

        self.contact_name = LineEdit(Form)
        self.contact_name.setGeometry(QtCore.QRect(0, 0, 150, 25))
        self.contact_name.setObjectName("contact_name")
        self.contact_name.textChanged.connect(self.filtering)

        self.online_contacts = ComboBox(Form)
        self.online_contacts.setGeometry(QtCore.QRect(150, 0, 120, 25))
        self.online_contacts.activated[int].connect(lambda x: self.filtering())
        self.search_label.raise_()

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_top(self, Form):
        Form.setCursor(QtCore.Qt.PointingHandCursor)
        Form.setMinimumSize(QtCore.QSize(270, 75))
        Form.setMaximumSize(QtCore.QSize(270, 75))
        Form.setBaseSize(QtCore.QSize(270, 75))
        self.avatar_label = Form.avatar_label = QtGui.QLabel(Form)
        self.avatar_label.setGeometry(QtCore.QRect(5, 5, 64, 64))
        self.avatar_label.setScaledContents(False)
        self.avatar_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name = Form.name = DataLabel(Form)
        Form.name.setGeometry(QtCore.QRect(75, 15, 150, 25))
        font = QtGui.QFont()
        font.setFamily(settings.Settings.get_instance()['font'])
        font.setPointSize(14)
        font.setBold(True)
        Form.name.setFont(font)
        Form.name.setObjectName("name")
        self.status_message = Form.status_message = DataLabel(Form)
        Form.status_message.setGeometry(QtCore.QRect(75, 35, 170, 25))
        font.setPointSize(12)
        font.setBold(False)
        Form.status_message.setFont(font)
        Form.status_message.setObjectName("status_message")
        self.connection_status = Form.connection_status = StatusCircle(Form)
        Form.connection_status.setGeometry(QtCore.QRect(230, 10, 32, 32))
        self.avatar_label.mouseReleaseEvent = self.profile_settings
        self.status_message.mouseReleaseEvent = self.profile_settings
        self.name.mouseReleaseEvent = self.profile_settings
        self.connection_status.raise_()
        Form.connection_status.setObjectName("connection_status")

    def setup_right_top(self, Form):
        Form.resize(650, 75)
        self.account_avatar = QtGui.QLabel(Form)
        self.account_avatar.setGeometry(QtCore.QRect(10, 5, 64, 64))
        self.account_avatar.setScaledContents(False)
        self.account_name = DataLabel(Form)
        self.account_name.setGeometry(QtCore.QRect(100, 0, 400, 25))
        self.account_name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font = QtGui.QFont()
        font.setFamily(settings.Settings.get_instance()['font'])
        font.setPointSize(14)
        font.setBold(True)
        self.account_name.setFont(font)
        self.account_name.setObjectName("account_name")
        self.account_status = DataLabel(Form)
        self.account_status.setGeometry(QtCore.QRect(100, 20, 400, 25))
        self.account_status.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font.setPointSize(12)
        font.setBold(False)
        self.account_status.setFont(font)
        self.account_status.setObjectName("account_status")
        self.callButton = QtGui.QPushButton(Form)
        self.callButton.setGeometry(QtCore.QRect(550, 5, 50, 50))
        self.callButton.setObjectName("callButton")
        self.callButton.clicked.connect(lambda: self.profile.call_click(True))
        self.videocallButton = QtGui.QPushButton(Form)
        self.videocallButton.setGeometry(QtCore.QRect(550, 5, 50, 50))
        self.videocallButton.setObjectName("videocallButton")
        self.videocallButton.clicked.connect(lambda: self.profile.call_click(True, True))
        self.update_call_state('call')
        self.typing = QtGui.QLabel(Form)
        self.typing.setGeometry(QtCore.QRect(500, 25, 50, 30))
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
        self.friends_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.friends_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.friends_list.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def setup_right_center(self, widget):
        self.messages = QtGui.QListWidget(widget)
        self.messages.setGeometry(0, 0, 620, 310)
        self.messages.setObjectName("messages")
        self.messages.setSpacing(1)
        self.messages.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.messages.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.messages.focusOutEvent = lambda event: self.messages.clearSelection()
        self.messages.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        def load(pos):
            if not pos:
                self.profile.load_history()
                self.messages.verticalScrollBar().setValue(1)
        self.messages.verticalScrollBar().valueChanged.connect(load)
        self.messages.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.messages.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

    def initUI(self, tox):
        self.setMinimumSize(920, 500)
        s = Settings.get_instance()
        self.setGeometry(s['x'], s['y'], s['width'], s['height'])
        self.setWindowTitle('Toxygen')
        os.chdir(curr_directory() + '/images/')
        menu = QtGui.QWidget()
        main = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        search = QtGui.QWidget()
        name = QtGui.QWidget()
        info = QtGui.QWidget()
        main_list = QtGui.QWidget()
        messages = QtGui.QWidget()
        message_buttons = QtGui.QWidget()
        self.setup_left_center_menu(search)
        self.setup_left_top(name)
        self.setup_right_center(messages)
        self.setup_right_top(info)
        self.setup_right_bottom(message_buttons)
        self.setup_left_center(main_list)
        self.setup_menu(menu)
        if not Settings.get_instance()['mirror_mode']:
            grid.addWidget(search, 2, 0)
            grid.addWidget(name, 1, 0)
            grid.addWidget(messages, 2, 1, 2, 1)
            grid.addWidget(info, 1, 1)
            grid.addWidget(message_buttons, 4, 1)
            grid.addWidget(main_list, 3, 0, 2, 1)
            grid.setColumnMinimumWidth(1, 500)
            grid.setColumnMinimumWidth(0, 270)
        else:
            grid.addWidget(search, 2, 1)
            grid.addWidget(name, 1, 1)
            grid.addWidget(messages, 2, 0, 2, 1)
            grid.addWidget(info, 1, 0)
            grid.addWidget(message_buttons, 4, 0)
            grid.addWidget(main_list, 3, 1, 2, 1)
            grid.setColumnMinimumWidth(0, 500)
            grid.setColumnMinimumWidth(1, 270)

        grid.addWidget(menu, 0, 0, 1, 2)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setRowMinimumHeight(0, 25)
        grid.setRowMinimumHeight(1, 75)
        grid.setRowMinimumHeight(2, 25)
        grid.setRowMinimumHeight(3, 320)
        grid.setRowMinimumHeight(4, 55)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(3, 1)
        main.setLayout(grid)
        self.setCentralWidget(main)
        self.messageEdit.setFocus()
        self.user_info = name
        self.friend_info = info
        self.retranslateUi()
        self.profile = Profile(tox, self)

    def closeEvent(self, event):
        s = Settings.get_instance()
        if not s['close_to_tray'] or s.closing:
            if not self._saved:
                self._saved = True
                self.profile.save_history()
                self.profile.close()
                s['x'] = self.geometry().x()
                s['y'] = self.geometry().y()
                s['width'] = self.width()
                s['height'] = self.height()
                s.save()
                QtGui.QApplication.closeAllWindows()
                event.accept()
        elif QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()

    def close_window(self):
        Settings.get_instance().closing = True
        self.close()

    def resizeEvent(self, *args, **kwargs):
        self.messages.setGeometry(0, 0, self.width() - 270, self.height() - 159)
        self.friends_list.setGeometry(0, 0, 270, self.height() - 129)

        self.videocallButton.setGeometry(QtCore.QRect(self.width() - 330, 10, 50, 50))
        self.callButton.setGeometry(QtCore.QRect(self.width() - 390, 10, 50, 50))
        self.typing.setGeometry(QtCore.QRect(self.width() - 450, 20, 50, 30))

        self.messageEdit.setGeometry(QtCore.QRect(55, 0, self.width() - 395, 55))
        self.menuButton.setGeometry(QtCore.QRect(0, 0, 55, 55))
        self.sendMessageButton.setGeometry(QtCore.QRect(self.width() - 340, 0, 70, 55))

        self.account_name.setGeometry(QtCore.QRect(100, 15, self.width() - 560, 25))
        self.account_status.setGeometry(QtCore.QRect(100, 35, self.width() - 560, 25))
        self.messageEdit.setFocus()
        self.profile.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape and QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
        elif event.key() == QtCore.Qt.Key_C and event.modifiers() & QtCore.Qt.ControlModifier and self.messages.selectedIndexes():
            rows = list(map(lambda x: self.messages.row(x), self.messages.selectedItems()))
            indexes = (rows[0] - self.messages.count(), rows[-1] - self.messages.count())
            s = self.profile.export_history(self.profile.active_friend, True, indexes)
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(s)
        elif event.key() == QtCore.Qt.Key_Z and event.modifiers() & QtCore.Qt.ControlModifier and self.messages.selectedIndexes():
            self.messages.clearSelection()
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
        msgBox.setText(text + util.program_version + '\nGitHub: https://github.com/toxygen-project/toxygen/')
        msgBox.exec_()

    def network_settings(self):
        self.n_s = NetworkSettings(self.reset)
        self.n_s.show()

    def plugins_menu(self):
        self.p_s = PluginsSettings()
        self.p_s.show()

    def add_contact(self, link=''):
        self.a_c = AddContact(link or '')
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

    def update_settings(self):
        self.update_s = UpdateSettings()
        self.update_s.show()

    def import_plugin(self):
        import util
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                           QtGui.QApplication.translate("MainWindow", 'Choose folder with plugin',
                                                                                        None,
                                                                                        QtGui.QApplication.UnicodeUTF8),
                                                           util.curr_directory(),
                                                           QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)
        if directory:
            src = directory + '/'
            dest = curr_directory() + '/plugins/'
            util.copy(src, dest)
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(
                QtGui.QApplication.translate("MainWindow", "Restart Toxygen", None, QtGui.QApplication.UnicodeUTF8))
            msgBox.setText(
                QtGui.QApplication.translate("MainWindow", 'Plugin will be loaded after restart', None,
                                             QtGui.QApplication.UnicodeUTF8))
            msgBox.exec_()

    def lock_app(self):
        if toxencryptsave.ToxEncryptSave.get_instance().has_password():
            Settings.get_instance().locked = True
            self.hide()
        else:
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowTitle(
                QtGui.QApplication.translate("MainWindow", "Cannot lock app", None, QtGui.QApplication.UnicodeUTF8))
            msgBox.setText(
                QtGui.QApplication.translate("MainWindow", 'Error. Profile password is not set.', None,
                                             QtGui.QApplication.UnicodeUTF8))
            msgBox.exec_()

    def show_menu(self):
        if not hasattr(self, 'menu'):
            self.menu = DropdownMenu(self)
        self.menu.setGeometry(QtCore.QRect(0 if Settings.get_instance()['mirror_mode'] else 270,
                                           self.height() - 120,
                                           180,
                                           120))
        self.menu.show()

    # -----------------------------------------------------------------------------------------------------------------
    # Messages, calls and file transfers
    # -----------------------------------------------------------------------------------------------------------------

    def send_message(self):
        text = self.messageEdit.toPlainText()
        self.profile.send_message(text)

    def send_file(self):
        self.menu.hide()
        if self.profile.active_friend + 1:
            choose = QtGui.QApplication.translate("MainWindow", 'Choose file', None, QtGui.QApplication.UnicodeUTF8)
            name = QtGui.QFileDialog.getOpenFileName(self, choose, options=QtGui.QFileDialog.DontUseNativeDialog)
            if name[0]:
                self.profile.send_file(name[0])

    def send_screenshot(self, hide=False):
        self.menu.hide()
        if self.profile.active_friend + 1:
            self.sw = ScreenShotWindow(self)
            self.sw.show()
            if hide:
                self.hide()

    def send_smiley(self):
        self.menu.hide()
        if self.profile.active_friend + 1:
            self.smiley = SmileyWindow(self)
            self.smiley.setGeometry(QtCore.QRect(self.x() if Settings.get_instance()['mirror_mode'] else 270 + self.x(),
                                                 self.y() + self.height() - 200,
                                                 self.smiley.width(),
                                                 self.smiley.height()))
            self.smiley.show()

    def send_sticker(self):
        self.menu.hide()
        if self.profile.active_friend + 1:
            self.sticker = StickerWindow(self)
            self.sticker.setGeometry(QtCore.QRect(self.x() if Settings.get_instance()['mirror_mode'] else 270 + self.x(),
                                                  self.y() + self.height() - 200,
                                                  self.sticker.width(),
                                                  self.sticker.height()))
            self.sticker.show()

    def active_call(self):
        self.update_call_state('finish_call')

    def incoming_call(self):
        self.update_call_state('incoming_call')

    def call_finished(self):
        self.update_call_state('call')

    def update_call_state(self, fl):
        # TODO: do smth with video call button
        os.chdir(curr_directory() + '/images/')
        pixmap = QtGui.QPixmap(curr_directory() + '/images/{}.png'.format(fl))
        icon = QtGui.QIcon(pixmap)
        self.callButton.setIcon(icon)
        self.callButton.setIconSize(QtCore.QSize(50, 50))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/videocall.png')
        icon = QtGui.QIcon(pixmap)
        self.videocallButton.setIcon(icon)
        self.videocallButton.setIconSize(QtCore.QSize(35, 35))

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user open context menu in friends list
    # -----------------------------------------------------------------------------------------------------------------

    def friend_right_click(self, pos):
        item = self.friends_list.itemAt(pos)
        num = self.friends_list.indexFromItem(item).row()
        friend = Profile.get_instance().get_friend(num)
        if friend is None:
            return
        settings = Settings.get_instance()
        allowed = friend.tox_id in settings['auto_accept_from_friends']
        auto = QtGui.QApplication.translate("MainWindow", 'Disallow auto accept', None, QtGui.QApplication.UnicodeUTF8) if allowed else QtGui.QApplication.translate("MainWindow", 'Allow auto accept', None, QtGui.QApplication.UnicodeUTF8)
        if item is not None:
            self.listMenu = QtGui.QMenu()
            set_alias_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Set alias', None, QtGui.QApplication.UnicodeUTF8))

            history_menu = self.listMenu.addMenu(QtGui.QApplication.translate("MainWindow", 'Chat history', None, QtGui.QApplication.UnicodeUTF8))
            clear_history_item = history_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Clear history', None, QtGui.QApplication.UnicodeUTF8))
            export_to_text_item = history_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Export as text', None, QtGui.QApplication.UnicodeUTF8))
            export_to_html_item = history_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Export as HTML', None, QtGui.QApplication.UnicodeUTF8))

            copy_menu = self.listMenu.addMenu(QtGui.QApplication.translate("MainWindow", 'Copy', None, QtGui.QApplication.UnicodeUTF8))
            copy_name_item = copy_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Name', None, QtGui.QApplication.UnicodeUTF8))
            copy_status_item = copy_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Status message', None, QtGui.QApplication.UnicodeUTF8))
            copy_key_item = copy_menu.addAction(QtGui.QApplication.translate("MainWindow", 'Public key', None, QtGui.QApplication.UnicodeUTF8))

            auto_accept_item = self.listMenu.addAction(auto)
            remove_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Remove friend', None, QtGui.QApplication.UnicodeUTF8))
            notes_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Notes', None, QtGui.QApplication.UnicodeUTF8))

            submenu = plugin_support.PluginLoader.get_instance().get_menu(self.listMenu, num)
            if len(submenu):
                plug = self.listMenu.addMenu(QtGui.QApplication.translate("MainWindow", 'Plugins', None, QtGui.QApplication.UnicodeUTF8))
                plug.addActions(submenu)
            self.connect(set_alias_item, QtCore.SIGNAL("triggered()"), lambda: self.set_alias(num))
            self.connect(remove_item, QtCore.SIGNAL("triggered()"), lambda: self.remove_friend(num))
            self.connect(copy_key_item, QtCore.SIGNAL("triggered()"), lambda: self.copy_friend_key(num))
            self.connect(clear_history_item, QtCore.SIGNAL("triggered()"), lambda: self.clear_history(num))
            self.connect(auto_accept_item, QtCore.SIGNAL("triggered()"), lambda: self.auto_accept(num, not allowed))
            self.connect(notes_item, QtCore.SIGNAL("triggered()"), lambda: self.show_note(friend))
            self.connect(copy_name_item, QtCore.SIGNAL("triggered()"), lambda: self.copy_name(friend))
            self.connect(copy_status_item, QtCore.SIGNAL("triggered()"), lambda: self.copy_status(friend))
            self.connect(export_to_text_item, QtCore.SIGNAL("triggered()"), lambda: self.export_history(num))
            self.connect(export_to_html_item, QtCore.SIGNAL("triggered()"),
                         lambda: self.export_history(num, False))
            parent_position = self.friends_list.mapToGlobal(QtCore.QPoint(0, 0))
            self.listMenu.move(parent_position + pos)
            self.listMenu.show()

    def show_note(self, friend):
        s = Settings.get_instance()
        note = s['notes'][friend.tox_id] if friend.tox_id in s['notes'] else ''
        user = QtGui.QApplication.translate("MainWindow", 'Notes about user', None, QtGui.QApplication.UnicodeUTF8)
        user = '{} {}'.format(user, friend.name)

        def save_note(text):
            if friend.tox_id in s['notes']:
                del s['notes'][friend.tox_id]
            if text:
                s['notes'][friend.tox_id] = text
            s.save()
        self.note = MultilineEdit(user, note, save_note)
        self.note.show()

    def export_history(self, num, as_text=True):
        s = self.profile.export_history(num, as_text)
        directory = QtGui.QFileDialog.getExistingDirectory(None,
                                                           QtGui.QApplication.translate("MainWindow", 'Choose folder',
                                                                                        None,
                                                                                        QtGui.QApplication.UnicodeUTF8),
                                                           curr_directory(),
                                                           QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)

        if directory:
            name = 'exported_history_{}.{}'.format(convert_time(time.time()), 'txt' if as_text else 'html')
            with open(directory + '/' + name, 'wt') as fl:
                fl.write(s)

    def set_alias(self, num):
        self.profile.set_alias(num)

    def remove_friend(self, num):
        self.profile.delete_friend(num)

    def copy_friend_key(self, num):
        tox_id = self.profile.friend_public_key(num)
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(tox_id)

    def copy_name(self, friend):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(friend.name)

    def copy_status(self, friend):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(friend.status_message)

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
        pos = self.connection_status.pos()
        x, y = pos.x() + self.user_info.pos().x(), pos.y() + self.user_info.pos().y()
        if (x < event.x() < x + 32) and (y < event.y() < y + 32):
            self.profile.change_status()
        else:
            super(MainWindow, self).mouseReleaseEvent(event)

    def filtering(self):
        ind = self.online_contacts.currentIndex()
        d = {0: 0, 1: 1, 2: 2, 3: 4, 4: 1 | 4, 5: 2 | 4}
        self.profile.filtration_and_sorting(d[ind], self.contact_name.text())
