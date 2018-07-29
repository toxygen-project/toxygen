from ui.contact_items import *
from ui.widgets import MultilineEdit, ComboBox
from ui.main_screen_widgets import *
import utils.util as util
import utils.ui as util_ui
from PyQt5 import uic


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, settings, tray):
        super().__init__()
        self._settings = settings
        self._contacts_manager = None
        self._tray = tray
        self._widget_factory = None
        self._modal_window = None
        self._plugins_loader = None
        self.setAcceptDrops(True)
        self._saved = False
        self._profile = self._toxes = self._messenger = None
        self._file_transfer_handler = self._history_loader = self._groups_service = self._calls_manager = None
        self._should_show_group_peers_list = False
        self.initUI()

    def set_dependencies(self, widget_factory, tray, contacts_manager, messenger, profile, plugins_loader,
                         file_transfer_handler, history_loader, calls_manager, groups_service, toxes):
        self._widget_factory = widget_factory
        self._tray = tray
        self._contacts_manager = contacts_manager
        self._profile = profile
        self._plugins_loader = plugins_loader
        self._file_transfer_handler = file_transfer_handler
        self._history_loader = history_loader
        self._calls_manager = calls_manager
        self._groups_service = groups_service
        self._toxes = toxes
        self._messenger = messenger
        self._contacts_manager.active_contact_changed.add_callback(self._new_contact_selected)
        self.messageEdit.set_messenger(messenger)

        self.update_gc_invites_button_state()

    def show(self):
        super().show()
        self._contacts_manager.update()
        if self._settings['show_welcome_screen']:
            self._modal_window = self._widget_factory.create_welcome_window()

    def setup_menu(self, window):
        self.menubar = QtWidgets.QMenuBar(window)
        self.menubar.setObjectName("menubar")
        self.menubar.setNativeMenuBar(False)
        self.menubar.setMinimumSize(self.width(), 25)
        self.menubar.setMaximumSize(self.width(), 25)
        self.menubar.setBaseSize(self.width(), 25)
        self.menuProfile = QtWidgets.QMenu(self.menubar)

        self.menuProfile = QtWidgets.QMenu(self.menubar)
        self.menuProfile.setObjectName("menuProfile")
        self.menuGC = QtWidgets.QMenu(self.menubar)
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuPlugins = QtWidgets.QMenu(self.menubar)
        self.menuPlugins.setObjectName("menuPlugins")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")

        self.actionAdd_friend = QtWidgets.QAction(window)
        self.actionAdd_friend.setObjectName("actionAdd_friend")
        self.actionprofilesettings = QtWidgets.QAction(window)
        self.actionprofilesettings.setObjectName("actionprofilesettings")
        self.actionPrivacy_settings = QtWidgets.QAction(window)
        self.actionPrivacy_settings.setObjectName("actionPrivacy_settings")
        self.actionInterface_settings = QtWidgets.QAction(window)
        self.actionInterface_settings.setObjectName("actionInterface_settings")
        self.actionNotifications = QtWidgets.QAction(window)
        self.actionNotifications.setObjectName("actionNotifications")
        self.actionNetwork = QtWidgets.QAction(window)
        self.actionNetwork.setObjectName("actionNetwork")
        self.actionAbout_program = QtWidgets.QAction(window)
        self.actionAbout_program.setObjectName("actionAbout_program")
        self.updateSettings = QtWidgets.QAction(window)
        self.actionSettings = QtWidgets.QAction(window)
        self.actionSettings.setObjectName("actionSettings")
        self.audioSettings = QtWidgets.QAction(window)
        self.videoSettings = QtWidgets.QAction(window)
        self.pluginData = QtWidgets.QAction(window)
        self.importPlugin = QtWidgets.QAction(window)
        self.reloadPlugins = QtWidgets.QAction(window)
        self.lockApp = QtWidgets.QAction(window)
        self.createGC = QtWidgets.QAction(window)
        self.joinGC = QtWidgets.QAction(window)
        self.gc_invites = QtWidgets.QAction(window)

        self.menuProfile.addAction(self.actionAdd_friend)
        self.menuProfile.addAction(self.actionSettings)
        self.menuProfile.addAction(self.lockApp)
        self.menuGC.addAction(self.createGC)
        self.menuGC.addAction(self.joinGC)
        self.menuGC.addAction(self.gc_invites)
        self.menuSettings.addAction(self.actionPrivacy_settings)
        self.menuSettings.addAction(self.actionInterface_settings)
        self.menuSettings.addAction(self.actionNotifications)
        self.menuSettings.addAction(self.actionNetwork)
        self.menuSettings.addAction(self.audioSettings)
        self.menuSettings.addAction(self.videoSettings)
        self.menuSettings.addAction(self.updateSettings)
        self.menuPlugins.addAction(self.pluginData)
        self.menuPlugins.addAction(self.importPlugin)
        self.menuPlugins.addAction(self.reloadPlugins)
        self.menuAbout.addAction(self.actionAbout_program)

        self.menubar.addAction(self.menuProfile.menuAction())
        self.menubar.addAction(self.menuGC.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuPlugins.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.actionAbout_program.triggered.connect(self.about_program)
        self.actionNetwork.triggered.connect(self.network_settings)
        self.actionAdd_friend.triggered.connect(self.add_contact_triggered)
        self.createGC.triggered.connect(self.create_gc)
        self.joinGC.triggered.connect(self.join_gc)
        self.actionSettings.triggered.connect(self.profile_settings)
        self.actionPrivacy_settings.triggered.connect(self.privacy_settings)
        self.actionInterface_settings.triggered.connect(self.interface_settings)
        self.actionNotifications.triggered.connect(self.notification_settings)
        self.audioSettings.triggered.connect(self.audio_settings)
        self.videoSettings.triggered.connect(self.video_settings)
        self.updateSettings.triggered.connect(self.update_settings)
        self.pluginData.triggered.connect(self.plugins_menu)
        self.lockApp.triggered.connect(self.lock_app)
        self.importPlugin.triggered.connect(self.import_plugin)
        self.reloadPlugins.triggered.connect(self.reload_plugins)
        self.gc_invites.triggered.connect(self._open_gc_invites_list)

    def languageChange(self, *args, **kwargs):
        self.retranslateUi()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self._tray.setIcon(QtGui.QIcon(util.join_path(util.get_images_directory(), 'icon.png')))
            self.messages.repaint()
        return super().event(event)

    def retranslateUi(self):
        self.lockApp.setText(util_ui.tr("Lock"))
        self.menuPlugins.setTitle(util_ui.tr("Plugins"))
        self.menuGC.setTitle(util_ui.tr("Group chats"))
        self.pluginData.setText(util_ui.tr("List of plugins"))
        self.menuProfile.setTitle(util_ui.tr("Profile"))
        self.menuSettings.setTitle(util_ui.tr("Settings"))
        self.menuAbout.setTitle(util_ui.tr("About"))
        self.actionAdd_friend.setText(util_ui.tr("Add contact"))
        self.createGC.setText(util_ui.tr("Create group chat"))
        self.joinGC.setText(util_ui.tr("Join group chat"))
        self.gc_invites.setText(util_ui.tr("Group invites"))
        self.actionprofilesettings.setText(util_ui.tr("Profile"))
        self.actionPrivacy_settings.setText(util_ui.tr("Privacy"))
        self.actionInterface_settings.setText(util_ui.tr("Interface"))
        self.actionNotifications.setText(util_ui.tr("Notifications"))
        self.actionNetwork.setText(util_ui.tr("Network"))
        self.actionAbout_program.setText(util_ui.tr("About program"))
        self.actionSettings.setText(util_ui.tr("Settings"))
        self.audioSettings.setText(util_ui.tr("Audio"))
        self.videoSettings.setText(util_ui.tr("Video"))
        self.updateSettings.setText(util_ui.tr("Updates"))
        self.importPlugin.setText(util_ui.tr("Import plugin"))
        self.reloadPlugins.setText(util_ui.tr("Reload plugins"))

        self.searchLineEdit.setPlaceholderText(util_ui.tr("Search"))
        self.sendMessageButton.setToolTip(util_ui.tr("Send message"))
        self.callButton.setToolTip(util_ui.tr("Start audio call with friend"))
        self.contactsFilterComboBox.clear()
        self.contactsFilterComboBox.addItem(util_ui.tr("All"))
        self.contactsFilterComboBox.addItem(util_ui.tr("Online"))
        self.contactsFilterComboBox.addItem(util_ui.tr("Online first"))
        self.contactsFilterComboBox.addItem(util_ui.tr("Name"))
        self.contactsFilterComboBox.addItem(util_ui.tr("Online and by name"))
        self.contactsFilterComboBox.addItem(util_ui.tr("Online first and by name"))

    def setup_right_bottom(self, Form):
        Form.resize(650, 60)
        self.messageEdit = MessageArea(Form, self)
        self.messageEdit.setGeometry(QtCore.QRect(0, 3, 450, 55))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setFamily(self._settings['font'])
        self.messageEdit.setFont(font)

        self.sendMessageButton = QtWidgets.QPushButton(Form)
        self.sendMessageButton.setGeometry(QtCore.QRect(565, 3, 60, 55))

        self.menuButton = MenuButton(Form, self.show_menu)
        self.menuButton.setGeometry(QtCore.QRect(QtCore.QRect(455, 3, 55, 55)))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'send.png'))
        icon = QtGui.QIcon(pixmap)
        self.sendMessageButton.setIcon(icon)
        self.sendMessageButton.setIconSize(QtCore.QSize(45, 60))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'menu.png'))
        icon = QtGui.QIcon(pixmap)
        self.menuButton.setIcon(icon)
        self.menuButton.setIconSize(QtCore.QSize(40, 40))

        self.sendMessageButton.clicked.connect(self.send_message)

        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_column(self, left_column):
        uic.loadUi(util.get_views_path('ms_left_column'), left_column)

        pixmap = QtGui.QPixmap()
        pixmap.load(util.join_path(util.get_images_directory(), 'search.png'))
        left_column.searchLabel.setPixmap(pixmap)

        self.name = DataLabel(left_column)
        self.name.setGeometry(QtCore.QRect(75, 15, 150, 25))
        font = QtGui.QFont()
        font.setFamily(self._settings['font'])
        font.setPointSize(14)
        font.setBold(True)
        self.name.setFont(font)

        self.status_message = DataLabel(left_column)
        self.status_message.setGeometry(QtCore.QRect(75, 35, 170, 25))

        self.connection_status = StatusCircle(left_column)
        self.connection_status.setGeometry(QtCore.QRect(230, 10, 32, 32))

        left_column.contactsFilterComboBox.activated[int].connect(lambda x: self._filtering())

        self.avatar_label = left_column.avatarLabel
        self.searchLineEdit = left_column.searchLineEdit
        self.contacts_filter = self.contactsFilterComboBox = left_column.contactsFilterComboBox

        self.groupInvitesPushButton = left_column.groupInvitesPushButton

        self.groupInvitesPushButton.clicked.connect(self._open_gc_invites_list)
        self.avatar_label.mouseReleaseEvent = self.profile_settings
        self.status_message.mouseReleaseEvent = self.profile_settings
        self.name.mouseReleaseEvent = self.profile_settings

        self.friends_list = left_column.friendsListWidget
        self.friends_list.clicked.connect(self._friend_click)
        self.friends_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.friends_list.customContextMenuRequested.connect(self._friend_right_click)
        self.friends_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.friends_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.friends_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.friends_list.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def setup_right_top(self, Form):
        Form.resize(650, 75)
        self.account_avatar = QtWidgets.QLabel(Form)
        self.account_avatar.setGeometry(QtCore.QRect(10, 5, 64, 64))
        self.account_avatar.setScaledContents(False)
        self.account_name = DataLabel(Form)
        self.account_name.setGeometry(QtCore.QRect(100, 0, 400, 25))
        self.account_name.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font = QtGui.QFont()
        font.setFamily(self._settings['font'])
        font.setPointSize(14)
        font.setBold(True)
        self.account_name.setFont(font)
        self.account_status = DataLabel(Form)
        self.account_status.setGeometry(QtCore.QRect(100, 20, 400, 25))
        self.account_status.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse)
        font.setPointSize(12)
        font.setBold(False)
        self.account_status.setFont(font)
        self.account_status.setObjectName("account_status")
        self.callButton = QtWidgets.QPushButton(Form)
        self.callButton.setGeometry(QtCore.QRect(550, 5, 50, 50))
        self.callButton.setObjectName("callButton")
        self.callButton.clicked.connect(lambda: self._calls_manager.call_click(True))
        self.videocallButton = QtWidgets.QPushButton(Form)
        self.videocallButton.setGeometry(QtCore.QRect(550, 5, 50, 50))
        self.videocallButton.setObjectName("videocallButton")
        self.videocallButton.clicked.connect(lambda: self._calls_manager.call_click(True, True))
        self.groupMenuButton = QtWidgets.QPushButton(Form)
        self.groupMenuButton.setGeometry(QtCore.QRect(470, 10, 50, 50))
        self.groupMenuButton.clicked.connect(self._toggle_gc_peers_list)
        self.groupMenuButton.setVisible(False)
        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'menu.png'))
        icon = QtGui.QIcon(pixmap)
        self.groupMenuButton.setIcon(icon)
        self.groupMenuButton.setIconSize(QtCore.QSize(45, 60))
        self.update_call_state('call')
        self.typing = QtWidgets.QLabel(Form)
        self.typing.setGeometry(QtCore.QRect(500, 25, 50, 30))
        pixmap = QtGui.QPixmap(QtCore.QSize(50, 30))
        pixmap.load(util.join_path(util.get_images_directory(), 'typing.png'))
        self.typing.setScaledContents(False)
        self.typing.setPixmap(pixmap.scaled(50, 30, QtCore.Qt.KeepAspectRatio))
        self.typing.setVisible(False)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_right_center(self, widget):
        self.messages = QtWidgets.QListWidget(widget)
        self.messages.setGeometry(0, 0, 620, 310)
        self.messages.setObjectName("messages")
        self.messages.setSpacing(1)
        self.messages.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.messages.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.messages.focusOutEvent = lambda event: self.messages.clearSelection()
        self.messages.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        def load(pos):
            if not pos:
                contact = self._contacts_manager.get_curr_contact()
                self._history_loader.load_history(contact)
                self.messages.verticalScrollBar().setValue(1)
        self.messages.verticalScrollBar().valueChanged.connect(load)
        self.messages.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.messages.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.peers_list = QtWidgets.QListWidget(widget)
        self.peers_list.setGeometry(0, 0, 0, 0)
        self.peers_list.setObjectName("peersList")
        self.peers_list.setSpacing(1)
        self.peers_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.peers_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.peers_list.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.peers_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

    def initUI(self):
        self.setMinimumSize(920, 500)
        s = self._settings
        self.setGeometry(s['x'], s['y'], s['width'], s['height'])
        self.setWindowTitle('Toxygen')
        menu = QtWidgets.QWidget()
        main = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        info = QtWidgets.QWidget()
        left_column = QtWidgets.QWidget()
        messages = QtWidgets.QWidget()
        message_buttons = QtWidgets.QWidget()
        self.setup_right_center(messages)
        self.setup_right_top(info)
        self.setup_right_bottom(message_buttons)
        self.setup_left_column(left_column)
        self.setup_menu(menu)
        if not s['mirror_mode']:
            grid.addWidget(left_column, 1, 0, 4, 1)
            grid.addWidget(messages, 2, 1, 2, 1)
            grid.addWidget(info, 1, 1)
            grid.addWidget(message_buttons, 4, 1)
            grid.setColumnMinimumWidth(1, 500)
            grid.setColumnMinimumWidth(0, 270)
        else:
            grid.addWidget(left_column, 1, 1, 4, 1)
            grid.addWidget(messages, 2, 0, 2, 1)
            grid.addWidget(info, 1, 0)
            grid.addWidget(message_buttons, 4, 0)
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
        self.friend_info = info
        self.retranslateUi()

    def closeEvent(self, event):
        if not self._settings['close_to_tray'] or self._settings.closing:
            if self._saved:
                return
            self._saved = True
            self._settings['x'] = self.geometry().x()
            self._settings['y'] = self.geometry().y()
            self._settings['width'] = self.width()
            self._settings['height'] = self.height()
            self._settings.save()
            util_ui.close_all_windows()
            event.accept()
        elif QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()

    def close_window(self):
        self._settings.closing = True
        self.close()

    def resizeEvent(self, *args, **kwargs):
        width = self.width() - 270
        if not self._should_show_group_peers_list:
            self.messages.setGeometry(0, 0, width, self.height() - 155)
            self.peers_list.setGeometry(0, 0, 0, 0)
        else:
            self.messages.setGeometry(0, 0, width * 3 // 4, self.height() - 155)
            self.peers_list.setGeometry(width * 3 // 4, 0, width - width * 3 // 4, self.height() - 155)

        invites_button_visible = self.groupInvitesPushButton.isVisible()
        self.friends_list.setGeometry(0, 125 if invites_button_visible else 100,
                                      270, self.height() - 150 if invites_button_visible else self.height() - 125)

        self.videocallButton.setGeometry(QtCore.QRect(self.width() - 330, 10, 50, 50))
        self.callButton.setGeometry(QtCore.QRect(self.width() - 390, 10, 50, 50))
        self.groupMenuButton.setGeometry(QtCore.QRect(self.width() - 450, 10, 50, 50))
        self.typing.setGeometry(QtCore.QRect(self.width() - 450, 20, 50, 30))

        self.messageEdit.setGeometry(QtCore.QRect(55, 0, self.width() - 395, 55))
        self.menuButton.setGeometry(QtCore.QRect(0, 0, 55, 55))
        self.sendMessageButton.setGeometry(QtCore.QRect(self.width() - 340, 0, 70, 55))

        self.account_name.setGeometry(QtCore.QRect(100, 15, self.width() - 560, 25))
        self.account_status.setGeometry(QtCore.QRect(100, 35, self.width() - 560, 25))
        self.messageEdit.setFocus()

    def keyPressEvent(self, event):
        key, modifiers = event.key(), event.modifiers()
        if key == QtCore.Qt.Key_Escape and QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            self.hide()
        elif key == QtCore.Qt.Key_C and modifiers & QtCore.Qt.ControlModifier and self.messages.selectedIndexes():
            rows = list(map(lambda x: self.messages.row(x), self.messages.selectedItems()))
            indexes = (rows[0] - self.messages.count(), rows[-1] - self.messages.count())
            s = self._history_loader.export_history(self._contacts_manager.get_curr_friend(), True, indexes)
            self.copy_text(s)
        elif key == QtCore.Qt.Key_Z and modifiers & QtCore.Qt.ControlModifier and self.messages.selectedIndexes():
            self.messages.clearSelection()
        elif key == QtCore.Qt.Key_F and modifiers & QtCore.Qt.ControlModifier:
            self.show_search_field()
        else:
            super().keyPressEvent(event)

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user click in menu
    # -----------------------------------------------------------------------------------------------------------------

    def about_program(self):
        # TODO: replace with window
        text = util_ui.tr('Toxygen is Tox client written on Python.\nVersion: ')
        text += '' + '\nGitHub: https://github.com/toxygen-project/toxygen/'
        title = util_ui.tr('About')
        util_ui.message_box(text, title)

    def network_settings(self):
        self._modal_window = self._widget_factory.create_network_settings_window()
        self._modal_window.show()

    def plugins_menu(self):
        self._modal_window = self._widget_factory.create_plugins_settings_window()
        self._modal_window.show()

    def add_contact_triggered(self, _):
        self.add_contact()

    def add_contact(self, link=''):
        self._modal_window = self._widget_factory.create_add_contact_window(link)
        self._modal_window.show()

    def create_gc(self):
        self._modal_window = self._widget_factory.create_group_screen_window()
        self._modal_window.show()

    def join_gc(self):
        self._modal_window = self._widget_factory.create_join_group_screen_window()
        self._modal_window.show()

    def profile_settings(self, _):
        self._modal_window = self._widget_factory.create_profile_settings_window()
        self._modal_window.show()

    def privacy_settings(self):
        self._modal_window = self._widget_factory.create_privacy_settings_window()
        self._modal_window.show()

    def notification_settings(self):
        self._modal_window = self._widget_factory.create_notification_settings_window()
        self._modal_window.show()

    def interface_settings(self):
        self._modal_window = self._widget_factory.create_interface_settings_window()
        self._modal_window.show()

    def audio_settings(self):
        self._modal_window = self._widget_factory.create_audio_settings_window()
        self._modal_window.show()

    def video_settings(self):
        self._modal_window = self._widget_factory.create_video_settings_window()
        self._modal_window.show()

    def update_settings(self):
        self._modal_window = self._widget_factory.create_update_settings_window()
        self._modal_window.show()

    def reload_plugins(self):
        if self._plugin_loader is not None:
            self._plugin_loader.reload()

    @staticmethod
    def import_plugin():
        directory = util_ui.directory_dialog(util_ui.tr('Choose folder with plugin'))
        if directory:
            src = directory + '/'
            dest = util.get_plugins_directory()
            util.copy(src, dest)
            util_ui.message_box(util_ui.tr('Plugin will be loaded after restart'), util_ui.tr("Restart Toxygen"))

    def lock_app(self):
        if self._toxes.has_password():
            self._settings.locked = True
            self.hide()
        else:
            util_ui.message_box(util_ui.tr('Error. Profile password is not set.'), util_ui.tr("Cannot lock app"))

    def show_menu(self):
        if not hasattr(self, 'menu'):
            self.menu = DropdownMenu(self)
        self.menu.setGeometry(QtCore.QRect(0 if self._settings['mirror_mode'] else 270,
                                           self.height() - 120,
                                           180,
                                           120))
        self.menu.show()

    # -----------------------------------------------------------------------------------------------------------------
    # Messages, calls and file transfers
    # -----------------------------------------------------------------------------------------------------------------

    def send_message(self):
        self._messenger.send_message()

    def send_file(self):
        self.menu.hide()
        if self._contacts_manager.is_active_a_friend():
            caption = util_ui.tr('Choose file')
            name = util_ui.file_dialog(caption)
            if name[0]:
                self._file_transfer_handler.send_file(name[0], self._contacts_manager.get_active_number())

    def send_screenshot(self, hide=False):
        self.menu.hide()
        if self._contacts_manager.is_active_a_friend():
            self.sw = self._widget_factory.create_screenshot_window(self)
            self.sw.show()
            if hide:
                self.hide()

    def send_smiley(self):
        self.menu.hide()
        if self._contacts_manager.get_curr_contact() is not None:
            self.smiley = self._widget_factory.create_smiley_window(self)
            self.smiley.setGeometry(QtCore.QRect(self.x() if self._settings['mirror_mode'] else 200 + self.x(),
                                                 self.y() + self.height() - 400,
                                                 self.smiley.width(),
                                                 self.smiley.height()))
            self.smiley.show()

    def send_sticker(self):
        self.menu.hide()
        if self._contacts_manager.is_active_a_friend():
            self.sticker = self._widget_factory.create_sticker_window()
            self.sticker.setGeometry(QtCore.QRect(self.x() if self._settings['mirror_mode'] else 270 + self.x(),
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

    def update_call_state(self, state):
        pixmap = QtGui.QPixmap(os.path.join(util.get_images_directory(), '{}.png'.format(state)))
        icon = QtGui.QIcon(pixmap)
        self.callButton.setIcon(icon)
        self.callButton.setIconSize(QtCore.QSize(50, 50))

        pixmap = QtGui.QPixmap(os.path.join(util.get_images_directory(), '{}_video.png'.format(state)))
        icon = QtGui.QIcon(pixmap)
        self.videocallButton.setIcon(icon)
        self.videocallButton.setIconSize(QtCore.QSize(35, 35))

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user open context menu in friends list
    # -----------------------------------------------------------------------------------------------------------------

    def _friend_right_click(self, pos):
        item = self.friends_list.itemAt(pos)
        number = self.friends_list.indexFromItem(item).row()
        contact = self._contacts_manager.get_contact(number)
        if contact is None or item is None:
            return
        generator = contact.get_context_menu_generator()
        self.listMenu = generator.generate(self._plugins_loader, self._contacts_manager, self, self._settings, number,
                                           self._groups_service)
        parent_position = self.friends_list.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parent_position + pos)
        self.listMenu.show()

    def show_note(self, friend):
        note = self._settings['notes'][friend.tox_id] if friend.tox_id in self._settings['notes'] else ''
        user = util_ui.tr('Notes about user')
        user = '{} {}'.format(user, friend.name)

        def save_note(text):
            if friend.tox_id in self._settings['notes']:
                del self._settings['notes'][friend.tox_id]
            if text:
                self._settings['notes'][friend.tox_id] = text
            self._settings.save()
        self.note = MultilineEdit(user, note, save_note)
        self.note.show()

    def export_history(self, num, as_text=True):
        s = self._contacts_manager.export_history(num, as_text)
        extension = 'txt' if as_text else 'html'
        file_name, _ = util_ui.save_file_dialog(util_ui.tr('Choose file name'), extension)

        if not file_name:
            return

        if not file_name.endswith('.' + extension):
            file_name += '.' + extension
        with open(file_name, 'wt') as fl:
            fl.write(s)

    def set_alias(self, num):
        self._contacts_manager.set_alias(num)

    def remove_friend(self, num):
        self._contacts_manager.delete_friend(num)

    def block_friend(self, num):
        friend = self._contacts_managere.get_contact(num)
        self._contacts_manager.block_user(friend.tox_id)

    @staticmethod
    def copy_text(text):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

    def clear_history(self, num):
        self._contacts_manager.clear_history(num)

    def leave_gc(self, num):
        self.profile.leave_gc(num)

    def set_title(self, num):
        self.profile.set_title(num)

    def auto_accept(self, num, value):
        tox_id = self._contacts_manager.friend_public_key(num)
        if value:
            self._settings['auto_accept_from_friends'].append(tox_id)
        else:
            self._settings['auto_accept_from_friends'].remove(tox_id)
        self._settings.save()

    def invite_friend_to_gc(self, friend_number, group_number):
        self._contacts_manager.invite_friend(friend_number, group_number)

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user click somewhere else
    # -----------------------------------------------------------------------------------------------------------------

    def _friend_click(self, index):
        num = index.row()
        self._contacts_manager.active_contact = num
        self.groupMenuButton.setVisible(not self._contacts_manager.is_active_a_friend())

    def mouseReleaseEvent(self, event):
        pos = self.connection_status.pos()
        x, y = pos.x(), pos.y() + 25
        if (x < event.x() < x + 32) and (y < event.y() < y + 32):
            self._profile.change_status()
        else:
            super().mouseReleaseEvent(event)

    def _filtering(self):
        index = self.contactsFilterComboBox.currentIndex()
        search_text = self.searchLineEdit.text()
        self._contacts_manager.filtration_and_sorting(index, search_text)

    def show_search_field(self):
        if hasattr(self, 'search_field') and self.search_field.isVisible():
            return
        if self._contacts_manager.get_curr_friend() is None:
            return
        self.search_field = self._widget_factory.create_search_screen(self.messages)
        x, y = self.messages.x(), self.messages.y() + self.messages.height() - 40
        self.search_field.setGeometry(x, y, self.messages.width(), 40)
        self.messages.setGeometry(x, self.messages.y(), self.messages.width(), self.messages.height() - 40)
        if self._should_show_group_peers_list:
            self.peers_list.setFixedHeight(self.peers_list.height() - 40)
        self.search_field.show()

    def _toggle_gc_peers_list(self):
        self._should_show_group_peers_list = not self._should_show_group_peers_list
        self.resizeEvent()
        if self._should_show_group_peers_list:
            self._groups_service.generate_peers_list()

    def _new_contact_selected(self, contact):
        if self._should_show_group_peers_list:
            self._toggle_gc_peers_list()
        self.resizeEvent()

    def _open_gc_invites_list(self):
        self._modal_window = self._widget_factory.create_group_invites_window()
        self._modal_window.show()

    def update_gc_invites_button_state(self):
        invites_count = self._groups_service.group_invites_count
        self.groupInvitesPushButton.setVisible(invites_count > 0)
        text = util_ui.tr('{} new invites to group chats').format(invites_count)
        self.groupInvitesPushButton.setText(text)
        self.resizeEvent()
