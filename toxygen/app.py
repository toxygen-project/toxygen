from middleware import threads
from PyQt5 import QtWidgets, QtGui, QtCore
import ui.password_screen as passwordscreen
from util.util import *
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
import util.ui as util_ui


class App:

    def __init__(self, version, path_to_profile=None, uri=None):
        self._version = version
        self._app = None
        self._tox = self._ms = self._init = self._app = self.tray = self._main_loop = self._av_loop = None
        self.uri = self._toxes = self._tray = None
        if uri is not None and uri.startswith('tox:'):
            self.uri = uri[4:]
        self._path = path_to_profile

    def enter_pass(self, data):
        """
        Show password screen
        """
        p = passwordscreen.PasswordScreen(self._toxes, data)
        p.show()
        self._app.lastWindowClosed.connect(self._app.quit)
        self._app.exec_()
        result = p.result
        if result is None:
            raise SystemExit()
        else:
            return result

    def main(self):
        """
        Main function of app. loads login screen if needed and starts main screen
        """
        self._app= QtWidgets.QApplication([])
        icon_file = os.path.join(get_images_directory(), 'icon.png')
        self._app.setWindowIcon(QtGui.QIcon(icon_file))

        if get_platform() == 'Linux':
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

        with open(os.path.join(get_styles_directory(), 'dark_style.qss')) as fl:
            style = fl.read()
        self._app.setStyleSheet(style)

        encrypt_save = tox_encrypt_save.ToxEncryptSave()
        self._toxes = user_data.toxes.ToxES(encrypt_save)

        if self._path is not None:
            path = os.path.dirname(self._path) + '/'
            name = os.path.basename(self._path)[:-4]
            self._settings = Settings(self._toxes, self._path.replace('.tox', '.json'))
            self._profile_manager = ProfileManager(self._settings, self._toxes, path)
            data = self._profile_manager.open_profile()
            if encrypt_save.is_data_encrypted(data):
                data = self.enter_pass(data)
            self._tox = self.create_tox(data)
        else:
            auto_profile = Settings.get_auto_profile()
            if not auto_profile[0]:
                # show login screen if default profile not found
                current_locale = QtCore.QLocale()
                curr_lang = current_locale.languageToString(current_locale.language())
                langs = Settings.supported_languages()
                if curr_lang in langs:
                    lang_path = langs[curr_lang]
                    translator = QtCore.QTranslator()
                    translator.load(get_translations_directory() + lang_path)
                    self._app.installTranslator(translator)
                    self._app.translator = translator
                ls = LoginScreen()
                ls.setWindowIconText("Toxygen")
                profiles = ProfileManager.find_profiles()
                ls.update_select(profiles)
                ls.show()
                self._app.exec_()
                result = ls.result
                if result is None:
                    return
                elif result.is_new_profile():  # create new profile
                    name = get_profile_name_from_path(result.profile_path) or 'toxygen_user'
                    pr = map(lambda x: x[1], ProfileManager.find_profiles())
                    if name in list(pr):
                        util_ui.message_box(util_ui.tr('Profile with this name already exists'),
                                            util_ui.tr('Error'))
                        return
                    self._tox = tox_factory()
                    self._tox.self_set_name(bytes(name, 'utf-8') if name else b'Toxygen User')
                    self._tox.self_set_status_message(b'Toxing on Toxygen')
                    # TODO: set profile password
                    path = result.profile_path
                    self._profile_manager = ProfileManager(self._toxes, path)
                    try:
                        self._profile_manager.save_profile(self._tox.get_savedata())
                    except Exception as ex:
                        print(str(ex))
                        log('Profile creation exception: ' + str(ex))
                        text = util_ui.tr('Profile saving error! Does Toxygen have permission to write to this directory?')
                        util_ui.message_box(text, util_ui.tr('Error'))
                        return
                    path = Settings.get_default_path()
                    self._settings = Settings()
                    if curr_lang in langs:
                        self._settings['language'] = curr_lang
                    self._settings.save()
                else:  # load existing profile
                    path = result.profile_path
                    if result.load_as_default:
                        Settings.set_auto_profile(path)
                    self._settings = Settings(self._toxes, path.replace('.tox', '.json'))
                    self._profile_manager = ProfileManager(self._settings, self._toxes, path)
                    data = self._profile_manager.open_profile()
                    if self._toxes.is_data_encrypted(data):
                        data = self.enter_pass(data)
                    self._tox = self.create_tox(data)
            else:
                path, name = auto_profile
                self._settings = Settings(self._toxes, path + name + '.json')
                self._profile_manager = ProfileManager(self._settings, self._toxes, path)
                data = self._profile_manager.open_profile()
                if encrypt_save.is_data_encrypted(data):
                    data = self.enter_pass(data)
                self.tox = self.create_tox(data)

        if Settings.is_active_profile(path, get_profile_name_from_path(path)):  # profile is in use
            title = util_ui.tr('Profile {}').format(name)
            text = util_ui.tr('Other instance of Toxygen uses this profile or profile was not properly closed. Continue?')
            reply = util_ui.question(text, title)
            if not reply:
                return
        else:
            self._settings.set_active_profile()

        self.load_app_styles()
        self.load_app_translations()

        if self.try_to_update():
            return

        self._ms = MainWindow(self._settings, self._tox, self.reset, self._tray)
        self._profile = self._ms.profile
        self._ms.show()

        self._tray = tray.init_tray(self._profile, self._settings, self._ms)
        self._tray.show()

        self._plugin_loader = PluginLoader(self._tox, self._toxes, self._profile, self._settings)  # plugins support
        self._plugin_loader.load()  # TODO; move to separate thread?

        if self.uri is not None:
            self._ms.add_contact(self.uri)

        self._app.lastWindowClosed.connect(self._app.quit)
        self._app.exec_()

        self._plugin_loader.stop()
        self.stop_threads()
        self._tray.hide()
        data = self._tox.get_savedata()
        self._profile_manager.save_profile(data)
        self._settings.close()
        del self._tox

    def reset(self):
        """
        Create new tox instance (new network settings)
        :return: tox instance
        """
        self.stop_threads()
        data = self._tox.get_savedata()
        self._profile_manager.save_profile(data)
        del self._tox
        # create new tox instance
        self._tox = tox_factory(data, self._settings)
        self.start_threads()

        self._plugin_loader.set_tox(self._tox)

        return self._tox

    def load_app_styles(self):
        # application color scheme
        for theme in self._settings.built_in_themes().keys():
            if self._settings['theme'] == theme:
                with open(curr_directory(__file__) + self._settings.built_in_themes()[theme]) as fl:
                    style = fl.read()
                self._app.setStyleSheet(style)

    def load_app_translations(self):
        lang = Settings.supported_languages()[self._settings['language']]
        translator = QtCore.QTranslator()
        translator.load(curr_directory(__file__) + '/translations/' + lang)
        self._app.installTranslator(translator)
        self._app.translator = translator

    def try_to_update(self):
        updating = updater.start_update_if_needed(self._version, self._settings)
        if updating:
            data = self._tox.get_savedata()
            self._profile_manager.save_profile(data)
            self._settings.close()
            del self._tox
        return updating

    def start_threads(self):
        # init thread
        self._init = threads.InitThread(self._tox, self._ms, self._tray)
        self._init.start()

        # starting threads for tox iterate and toxav iterate
        self._main_loop = threads.ToxIterateThread(self._tox)
        self._main_loop.start()
        self._av_loop = threads.ToxAVIterateThread(self._tox.AV)
        self._av_loop.start()

    def stop_threads(self):
        self._init.stop_thread()

        self._main_loop.stop_thread()
        self._av_loop.stop_thread()

    def create_tox(self, data):
        return tox_factory(data, self._settings)
