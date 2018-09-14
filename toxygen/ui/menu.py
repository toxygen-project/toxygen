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
        uic.loadUi(get_views_path('add_contact_screen'), self)
        self._update_ui(tox_id)
        self._adding = False

    def _update_ui(self, tox_id):
        self.toxIdLineEdit = LineEdit(self)
        self.toxIdLineEdit.setGeometry(QtCore.QRect(50, 40, 460, 30))
        self.toxIdLineEdit.setText(tox_id)

        self.messagePlainTextEdit.document().setPlainText(util_ui.tr('Hello! Please add me to your contact list.'))
        self.addContactPushButton.clicked.connect(self._add_friend)
        self._retranslate_ui()

    def _add_friend(self):
        if self._adding:
            return
        self._adding = True
        tox_id = self.toxIdLineEdit.text().strip()
        if tox_id.startswith('tox:'):
            tox_id = tox_id[4:]
        message = self.messagePlainTextEdit.toPlainText()
        send = self._contacts_manager.send_friend_request(tox_id, message)
        self._adding = False
        if send is True:
            # request was successful
            self.close()
        else:  # print error data
            self.errorLabel.setText(send)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Add contact'))
        self.addContactPushButton.setText(util_ui.tr('Send request'))
        self.toxIdLabel.setText(util_ui.tr('TOX ID:'))
        self.messageLabel.setText(util_ui.tr('Message:'))
        self.toxIdLineEdit.setPlaceholderText(util_ui.tr('TOX ID or public key of contact'))


class NetworkSettings(CenteredWidget):
    """Network settings form: UDP, Ipv6 and proxy"""
    def __init__(self, settings, reset):
        super().__init__()
        self._settings = settings
        self._reset = reset
        uic.loadUi(get_views_path('network_settings_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self.ipLineEdit = LineEdit(self)
        self.ipLineEdit.setGeometry(100, 280, 270, 30)

        self.portLineEdit = LineEdit(self)
        self.portLineEdit.setGeometry(100, 325, 270, 30)

        self.restartCorePushButton.clicked.connect(self._restart_core)
        self.ipv6CheckBox.setChecked(self._settings['ipv6_enabled'])
        self.udpCheckBox.setChecked(self._settings['udp_enabled'])
        self.proxyCheckBox.setChecked(self._settings['proxy_type'])
        self.ipLineEdit.setText(self._settings['proxy_host'])
        self.portLineEdit.setText(str(self._settings['proxy_port']))
        self.httpProxyRadioButton.setChecked(self._settings['proxy_type'] == 1)
        self.socksProxyRadioButton.setChecked(self._settings['proxy_type'] != 1)
        self.downloadNodesCheckBox.setChecked(self._settings['download_nodes_list'])
        self.lanCheckBox.setChecked(self._settings['lan_discovery'])
        self._retranslate_ui()
        self.proxyCheckBox.stateChanged.connect(lambda x: self._activate_proxy())
        self._activate_proxy()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Network settings"))
        self.ipv6CheckBox.setText(util_ui.tr("IPv6"))
        self.udpCheckBox.setText(util_ui.tr("UDP"))
        self.lanCheckBox.setText(util_ui.tr("LAN"))
        self.proxyCheckBox.setText(util_ui.tr("Proxy"))
        self.ipLabel.setText(util_ui.tr("IP:"))
        self.portLabel.setText(util_ui.tr("Port:"))
        self.restartCorePushButton.setText(util_ui.tr("Restart TOX core"))
        self.httpProxyRadioButton.setText(util_ui.tr("HTTP"))
        self.socksProxyRadioButton.setText(util_ui.tr("Socks 5"))
        self.downloadNodesCheckBox.setText(util_ui.tr("Download nodes list from tox.chat"))
        self.warningLabel.setText(util_ui.tr("WARNING:\nusing proxy with enabled UDP\ncan produce IP leak"))

    def _activate_proxy(self):
        bl = self.proxyCheckBox.isChecked()
        self.ipLineEdit.setEnabled(bl)
        self.portLineEdit.setEnabled(bl)
        self.httpProxyRadioButton.setEnabled(bl)
        self.socksProxyRadioButton.setEnabled(bl)
        self.ipLabel.setEnabled(bl)
        self.portLabel.setEnabled(bl)

    def _restart_core(self):
        try:
            self._settings['ipv6_enabled'] = self.ipv6CheckBox.isChecked()
            self._settings['udp_enabled'] = self.udpCheckBox.isChecked()
            proxy_enabled = self.proxyCheckBox.isChecked()
            self._settings['proxy_type'] = 2 - int(self.httpProxyRadioButton.isChecked()) if proxy_enabled else 0
            self._settings['proxy_host'] = str(self.ipLineEdit.text())
            self._settings['proxy_port'] = int(self.portLineEdit.text())
            self._settings['download_nodes_list'] = self.downloadNodesCheckBox.isChecked()
            self._settings['lan_discovery'] = self.lanCheckBox.isChecked()
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

        uic.loadUi(get_views_path('interface_settings_screen'), self)
        self._update_ui()
        self.center()

    def _update_ui(self):
        themes = list(self._settings.built_in_themes().keys())
        self.themeComboBox.addItems(themes)
        theme = self._settings['theme']
        if theme in self._settings.built_in_themes().keys():
            index = themes.index(theme)
        else:
            index = 0
        self.themeComboBox.setCurrentIndex(index)

        supported_languages = sorted(Settings.supported_languages().keys(), reverse=True)
        for key in supported_languages:
            self.languageComboBox.insertItem(0, key)
            if self._settings['language'] == key:
                self.languageComboBox.setCurrentIndex(0)

        smiley_packs = self._smiley_loader.get_packs_list()
        self.smileysPackComboBox.addItems(smiley_packs)
        try:
            index = smiley_packs.index(self._settings['smiley_pack'])
        except:
            index = smiley_packs.index('default')
        self.smileysPackComboBox.setCurrentIndex(index)

        app_closing_setting = self._settings['close_app']
        self.closeRadioButton.setChecked(app_closing_setting == 0)
        self.hideRadioButton.setChecked(app_closing_setting == 1)
        self.closeToTrayRadioButton.setChecked(app_closing_setting == 2)

        self.compactModeCheckBox.setChecked(self._settings['compact_mode'])
        self.showAvatarsCheckBox.setChecked(self._settings['show_avatars'])
        self.smileysCheckBox.setChecked(self._settings['smileys'])

        self.importSmileysPushButton.clicked.connect(self._import_smileys)
        self.importStickersPushButton.clicked.connect(self._import_stickers)

        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Interface settings"))
        self.showAvatarsCheckBox.setText(util_ui.tr("Show avatars in chat"))
        self.themeLabel.setText(util_ui.tr("Theme:"))
        self.languageLabel.setText(util_ui.tr("Language:"))
        self.smileysGroupBox.setTitle(util_ui.tr("Smileys settings"))
        self.smileysPackLabel.setText(util_ui.tr("Smiley pack:"))
        self.smileysCheckBox.setText(util_ui.tr("Smileys"))
        self.closeRadioButton.setText(util_ui.tr("Close app"))
        self.hideRadioButton.setText(util_ui.tr("Hide app"))
        self.closeToTrayRadioButton.setText(util_ui.tr("Close to tray"))
        self.mirrorModeCheckBox.setText(util_ui.tr("Mirror mode"))
        self.compactModeCheckBox.setText(util_ui.tr("Compact contact list"))
        self.importSmileysPushButton.setText(util_ui.tr("Import smiley pack"))
        self.importStickersPushButton.setText(util_ui.tr("Import sticker pack"))
        self.appClosingGroupBox.setTitle(util_ui.tr("App closing settings"))

    @staticmethod
    def _import_stickers():
        directory = util_ui.directory_dialog(util_ui.tr('Choose folder with sticker pack'))
        if directory:
            dest = join_path(get_stickers_directory(), os.path.basename(directory))
            copy(directory, dest)

    @staticmethod
    def _import_smileys():
        directory = util_ui.directory_dialog(util_ui.tr('Choose folder with smiley pack'))
        if not directory:
            return
        src = directory + '/'
        dest = join_path(get_smileys_directory(), os.path.basename(directory))
        copy(src, dest)

    def closeEvent(self, event):
        app = QtWidgets.QApplication.instance()

        self._settings['theme'] = str(self.themeComboBox.currentText())
        try:
            theme = self._settings['theme']
            styles_path = join_path(get_styles_directory(), self._settings.built_in_themes()[theme])
            with open(styles_path) as fl:
                style = fl.read()
            app.setStyleSheet(style)
        except IsADirectoryError:
            pass

        self._settings['smileys'] = self.smileysCheckBox.isChecked()

        restart = False
        if self._settings['mirror_mode'] != self.mirrorModeCheckBox.isChecked():
            self._settings['mirror_mode'] = self.mirrorModeCheckBox.isChecked()
            restart = True

        if self._settings['compact_mode'] != self.compactModeCheckBox.isChecked():
            self._settings['compact_mode'] = self.compactModeCheckBox.isChecked()
            restart = True

        if self._settings['show_avatars'] != self.showAvatarsCheckBox.isChecked():
            self._settings['show_avatars'] = self.showAvatarsCheckBox.isChecked()
            restart = True

        self._settings['smiley_pack'] = self.smileysPackComboBox.currentText()
        self._smiley_loader.load_pack()

        language = self.languageComboBox.currentText()
        if self._settings['language'] != language:
            self._settings['language'] = language
            path = Settings.supported_languages()[language]
            app.removeTranslator(app.translator)
            app.translator.load(join_path(get_translations_directory(), path))
            app.installTranslator(app.translator)

        app_closing_setting = 0
        if self.hideRadioButton.isChecked():
            app_closing_setting = 1
        elif self.closeToTrayRadioButton.isChecked():
            app_closing_setting = 2
        self._settings['close_app'] = app_closing_setting
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
