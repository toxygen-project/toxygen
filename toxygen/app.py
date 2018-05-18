from middleware import threads
import middleware.callbacks as callbacks
from PyQt5 import QtWidgets, QtGui, QtCore
import ui.password_screen as password_screen
import updater.updater as updater
import os
from middleware.tox_factory import tox_factory
import wrapper.toxencryptsave as tox_encrypt_save
import user_data.toxes
from user_data.settings import Settings
from ui.login_screen import LoginScreen
from user_data.profile_manager import ProfileManager
from plugin_support.plugin_support import PluginLoader
from ui.main_screen import MainWindow
from ui import tray
import utils.ui as util_ui
import utils.util as util
from contacts.profile import Profile
from file_transfers.file_transfers_handler import FileTransfersHandler
from contacts.contact_provider import ContactProvider
from contacts.friend_factory import FriendFactory
from contacts.group_factory import GroupFactory
from contacts.contacts_manager import ContactsManager
from av.calls_manager import CallsManager
from history.database import Database
from ui.widgets_factory import WidgetsFactory
from smileys.smileys import SmileyLoader
from ui.items_factories import MessagesItemsFactory, FriendItemsFactory
from messenger.messenger import Messenger
from network.tox_dns import ToxDns
from history.history import History
from file_transfers.file_transfers_messages_service import FileTransfersMessagesService
import styles.style  # TODO: dynamic loading


class App:

    def __init__(self, version, path_to_profile=None, uri=None):
        self._version = version
        self._app = self._settings = self._profile_manager = self._plugin_loader = self._messenger = None
        self._tox = self._ms = self._init = self._main_loop = self._av_loop = None
        self._uri = self._toxes = self._tray = self._file_transfer_handler = self._contacts_provider = None
        self._friend_factory = self._calls_manager = self._contacts_manager = self._smiley_loader = self._tox_dns = None
        self._group_factory = None
        if uri is not None and uri.startswith('tox:'):
            self._uri = uri[4:]
        self._path = path_to_profile

    # -----------------------------------------------------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------------------------------------------------

    def main(self):
        """
        Main function of app. loads login screen if needed and starts main screen
        """
        self._app = QtWidgets.QApplication([])
        self._load_icon()

        if util.get_platform() == 'Linux':
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

        self._load_base_style()

        if not self._select_and_load_profile():
            return

        if self._try_to_update():
            return

        self._load_app_styles()
        self._load_app_translations()

        self._create_dependencies()
        self._start_threads()

        if self._uri is not None:
            self._ms.add_contact(self._uri)

        self._app.lastWindowClosed.connect(self._app.quit)

        self._execute_app()

        self._stop_app()

    # -----------------------------------------------------------------------------------------------------------------
    # App executing
    # -----------------------------------------------------------------------------------------------------------------

    def _execute_app(self):
        while True:
            try:
                self._app.exec_()
            except Exception as ex:
                util.log('Unhandled exception: ' + str(ex))
            else:
                break

    def _stop_app(self):
        self._plugin_loader.stop()
        self._stop_threads()
        self._tray.hide()
        self._save_profile()
        self._settings.close()
        del self._tox

    # -----------------------------------------------------------------------------------------------------------------
    # App loading
    # -----------------------------------------------------------------------------------------------------------------

    def _load_base_style(self):
        with open(util.join_path(util.get_styles_directory(), 'dark_style.qss')) as fl:
            style = fl.read()
        self._app.setStyleSheet(style)

    def _load_app_styles(self):
        # application color scheme
        if self._settings['theme'] == 'dark':
            return
        for theme in self._settings.built_in_themes().keys():
            if self._settings['theme'] == theme:
                with open(util.curr_directory(__file__) + self._settings.built_in_themes()[theme]) as fl:
                    style = fl.read()
                self._app.setStyleSheet(style)

    def _load_login_screen_translations(self):
        current_language, supported_languages = self._get_languages()
        if current_language in supported_languages:
            lang_path = supported_languages[current_language]
            translator = QtCore.QTranslator()
            translator.load(util.get_translations_directory() + lang_path)
            self._app.installTranslator(translator)
            self._app.translator = translator

    def _load_icon(self):
        icon_file = os.path.join(util.get_images_directory(), 'icon.png')
        self._app.setWindowIcon(QtGui.QIcon(icon_file))

    @staticmethod
    def _get_languages():
        current_locale = QtCore.QLocale()
        curr_language = current_locale.languageToString(current_locale.language())
        supported_languages = Settings.supported_languages()

        return curr_language, supported_languages

    def _load_app_translations(self):
        lang = Settings.supported_languages()[self._settings['language']]
        translator = QtCore.QTranslator()
        translator.load(os.path.join(util.get_translations_directory(), lang))
        self._app.installTranslator(translator)
        self._app.translator = translator

    def _select_and_load_profile(self):
        encrypt_save = tox_encrypt_save.ToxEncryptSave()
        self._toxes = user_data.toxes.ToxES(encrypt_save)

        if self._path is not None:  # toxygen was started with path to profile
            self._load_existing_profile(self._path)
        else:
            auto_profile = Settings.get_auto_profile()
            if auto_profile is None:  # no default profile
                result = self._select_profile()
                if result is None:
                    return False
                if result.is_new_profile():  # create new profile
                    self._create_new_profile(result.profile_path)
                else:  # load existing profile
                    self._load_existing_profile(result.profile_path)
                self._path = result.profile_path
            else:  # default profile
                self._path = auto_profile
                self._load_existing_profile(auto_profile)

        if Settings.is_active_profile(self._path):  # profile is in use
            profile_name = util.get_profile_name_from_path(self._path)
            title = util_ui.tr('Profile {}').format(profile_name)
            text = util_ui.tr(
                'Other instance of Toxygen uses this profile or profile was not properly closed. Continue?')
            reply = util_ui.question(text, title)
            if not reply:
                return False

        self._settings.set_active_profile()

        return True

    # -----------------------------------------------------------------------------------------------------------------
    # Threads
    # -----------------------------------------------------------------------------------------------------------------

    def _start_threads(self):
        # init thread
        self._init = threads.InitThread(self._tox, self._plugin_loader, self._settings)
        self._init.start()

        # starting threads for tox iterate and toxav iterate
        self._main_loop = threads.ToxIterateThread(self._tox)
        self._main_loop.start()
        self._av_loop = threads.ToxAVIterateThread(self._tox.AV)
        self._av_loop.start()

        threads.start_file_transfer_thread()

    def _stop_threads(self):
        self._init.stop_thread()

        self._av_loop.stop_thread()
        self._main_loop.stop_thread()

        threads.stop_file_transfer_thread()

    # -----------------------------------------------------------------------------------------------------------------
    # Profiles
    # -----------------------------------------------------------------------------------------------------------------

    def _select_profile(self):
        self._load_login_screen_translations()
        ls = LoginScreen()
        profiles = ProfileManager.find_profiles()
        ls.update_select(profiles)
        ls.show()
        self._app.exec_()

        return ls.result

    def _load_existing_profile(self, profile_path):
        self._settings = Settings(self._toxes, profile_path.replace('.tox', '.json'))
        self._profile_manager = ProfileManager(self._settings, self._toxes, profile_path)
        data = self._profile_manager.open_profile()
        if self._toxes.is_data_encrypted(data):
            data = self._enter_pass(data)
        self._tox = self._create_tox(data)

    def _create_new_profile(self, profile_path):
        name = util.get_profile_name_from_path(profile_path) or 'toxygen_user'
        if os.path.isfile(profile_path):
            util_ui.message_box(util_ui.tr('Profile with this name already exists'),
                                util_ui.tr('Error'))
            return
        self._tox = tox_factory()
        self._tox.self_set_name(bytes(name, 'utf-8') if name else b'Toxygen User')
        self._tox.self_set_status_message(b'Toxing on Toxygen')
        # TODO: set profile password
        self._settings = Settings(self._toxes, self._path.replace('.tox', '.json'))
        self._profile_manager = ProfileManager(self._settings, self._toxes, profile_path)
        try:
            self._save_profile()
        except Exception as ex:
            print(ex)
            util.log('Profile creation exception: ' + str(ex))
            text = util_ui.tr('Profile saving error! Does Toxygen have permission to write to this directory?')
            util_ui.message_box(text, util_ui.tr('Error'))
            return
        current_language, supported_languages = self._get_languages()
        if current_language in supported_languages:
            self._settings['language'] = current_language
        self._settings.save()

    def _save_profile(self, data=None):
        data = data or self._tox.get_savedata()
        self._profile_manager.save_profile(data)

    # -----------------------------------------------------------------------------------------------------------------
    # Other private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _enter_pass(self, data):
        """
        Show password screen
        """
        p = password_screen.PasswordScreen(self._toxes, data)
        p.show()
        self._app.lastWindowClosed.connect(self._app.quit)
        self._app.exec_()
        if p.result is not None:
            return p.result
        raise SystemExit()

    def _reset(self):
        """
        Create new tox instance (new network settings)
        :return: tox instance
        """
        self._stop_threads()
        data = self._tox.get_savedata()
        self._save_profile(data)
        del self._tox
        # create new tox instance
        self._tox = self._create_tox(data)
        self._start_threads()

        # TODO: foreach in list of tox savers set_tox

        return self._tox

    def _create_dependencies(self):
        self._smiley_loader = SmileyLoader(self._settings)
        self._tox_dns = ToxDns(self._settings)
        self._ms = MainWindow(self._settings, self._tray)
        db = Database(self._path.replace('.tox', '.db'), self._toxes)

        friend_items_factory = FriendItemsFactory(self._settings, self._ms)
        self._friend_factory = FriendFactory(self._profile_manager, self._settings, self._tox, db, friend_items_factory)
        self._group_factory = GroupFactory()
        self._contacts_provider = ContactProvider(self._tox, self._friend_factory, self._group_factory)
        profile = Profile(self._profile_manager, self._tox, self._ms, self._contacts_provider, self._reset)
        self._plugin_loader = PluginLoader(self._tox, self._toxes, profile, self._settings)
        history = None
        messages_items_factory = MessagesItemsFactory(self._settings, self._plugin_loader, self._smiley_loader,
                                                      self._ms, lambda m: history.delete_message(m))
        history = History(self._contacts_provider, db, self._settings, self._ms, messages_items_factory)
        self._contacts_manager = ContactsManager(self._tox, self._settings, self._ms, self._profile_manager,
                                                 self._contacts_provider, history, self._tox_dns,
                                                 messages_items_factory)
        history.set_contacts_manager(self._contacts_manager)
        self._calls_manager = CallsManager(self._tox.AV, self._settings, self._ms, self._contacts_manager)
        self._messenger = Messenger(self._tox, self._plugin_loader, self._ms, self._contacts_manager,
                                    self._contacts_provider, messages_items_factory, profile, self._calls_manager)
        file_transfers_message_service = FileTransfersMessagesService(self._contacts_manager, messages_items_factory,
                                                                      profile, self._ms)
        self._file_transfer_handler = FileTransfersHandler(self._tox, self._settings, self._contacts_provider,
                                                           file_transfers_message_service, profile)
        messages_items_factory.set_file_transfers_handler(self._file_transfer_handler)
        widgets_factory = WidgetsFactory(self._settings, profile, self._profile_manager, self._contacts_manager,
                                         self._file_transfer_handler, self._smiley_loader, self._plugin_loader,
                                         self._toxes, self._version)
        self._tray = tray.init_tray(profile, self._settings, self._ms)
        self._ms.set_dependencies(widgets_factory, self._tray, self._contacts_manager, self._messenger, profile,
                                  self._plugin_loader, self._file_transfer_handler, history, self._calls_manager)

        self._tray.show()
        self._ms.show()

        # callbacks initialization
        callbacks.init_callbacks(self._tox, profile, self._settings, self._plugin_loader, self._contacts_manager,
                                 self._calls_manager, self._file_transfer_handler, self._ms, self._tray,
                                 self._messenger)

    def _try_to_update(self):
        updating = updater.start_update_if_needed(self._version, self._settings)
        if updating:
            self._save_profile()
            self._settings.close()
            del self._tox
        return updating

    def _create_tox(self, data):
        return tox_factory(data, self._settings)
