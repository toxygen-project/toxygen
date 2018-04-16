import communication.callbacks
import threads
from PyQt5 import QtWidgets, QtGui, QtCore
import ui.password_screen as passwordscreen
from util.util import *
import updater.updater as updater
import os
from communication.tox_factory import tox_factory
import wrapper.toxencryptsave as tox_encrypt_save
import user_data.toxes
from user_data.settings import Settings
from ui.login_screen import LoginScreen
from user_data.profile_manager import ProfileManager
from plugin_support.plugin_support import PluginLoader
from ui.main_screen import MainWindow


class App:

    def __init__(self, version, path_to_profile=None, uri=None):
        self._version = version
        self._app = None
        self.tox = self.ms = self.init = self.app = self.tray = self.mainloop = self.avloop = None
        self.uri = self.path = self.toxes = None
        if uri is not None and uri.startswith('tox:'):
            self.uri = uri[4:]
        if path_to_profile is not None:
            self.path = path_to_profile

    def enter_pass(self, data):
        """
        Show password screen
        """
        p = passwordscreen.PasswordScreen(self.toxes, data)
        p.show()
        self.app.lastWindowClosed.connect(self.app.quit)
        self.app.exec_()
        result = p.result
        if result is None:
            raise SystemExit()
        else:
            return result

    def main(self):
        """
        Main function of app. loads login screen if needed and starts main screen
        """
        app = QtWidgets.QApplication([])
        icon_file = os.path.join(get_images_directory(), 'icon.png')
        app.setWindowIcon(QtGui.QIcon(icon_file))
        self._app = app

        if get_platform() == 'Linux':
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

        with open(os.path.join(get_styles_directory(), 'dark_style.qss')) as fl:
            style = fl.read()
        app.setStyleSheet(style)

        encrypt_save = tox_encrypt_save.ToxEncryptSave()
        self._toxes = user_data.toxes.ToxES(encrypt_save)

        if self.path is not None:
            path = os.path.dirname(self.path) + '/'
            name = os.path.basename(self.path)[:-4]
            self._settings = Settings(self._toxes, self.path.replace('.tox', '.json'))
            self._profile_manager = ProfileManager(self._settings, self._toxes, path)
            data = self._profile_manager.open_profile()
            if encrypt_save.is_data_encrypted(data):
                data = self.enter_pass(data)
            self.tox = tox_factory(data, self._settings)
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
                    translator.load(curr_directory() + '/translations/' + lang_path)
                    app.installTranslator(translator)
                    app.translator = translator
                ls = LoginScreen()
                ls.setWindowIconText("Toxygen")
                profiles = ProfileManager.find_profiles()
                ls.update_select(profiles)
                ls.show()
                app.exec_()
                result = ls.result
                if result is None:
                    return
                elif result.is_new_profile():  # create new profile
                    name = get_profile_name_from_path(result.profile_path) or 'toxygen_user'
                    pr = map(lambda x: x[1], ProfileManager.find_profiles())
                    if name in list(pr):
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setWindowTitle(
                            QtWidgets.QApplication.translate("MainWindow", "Error"))
                        text = (QtWidgets.QApplication.translate("MainWindow",
                                                                 'Profile with this name already exists'))
                        msgBox.setText(text)
                        msgBox.exec_()
                        return
                    self.tox = tox_factory()
                    self.tox.self_set_name(bytes(name, 'utf-8') if name else b'Toxygen User')
                    self.tox.self_set_status_message(b'Toxing on Toxygen')
                    reply = QtWidgets.QMessageBox.question(None,
                                                           'Profile {}'.format(name),
                                                           QtWidgets.QApplication.translate("login",
                                                                                            'Do you want to set profile password?'),
                                                           QtWidgets.QMessageBox.Yes,
                                                           QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        set_pass = SetProfilePasswordScreen(encrypt_save)
                        set_pass.show()
                        self.app.lastWindowClosed.connect(self.app.quit)
                        self.app.exec_()
                    reply = QtWidgets.QMessageBox.question(None,
                                                           'Profile {}'.format(name),
                                                           QtWidgets.QApplication.translate("login",
                                                                                            'Do you want to save profile in default folder? If no, profile will be saved in program folder'),
                                                           QtWidgets.QMessageBox.Yes,
                                                           QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        path = Settings.get_default_path()
                    else:
                        path = curr_directory() + '/'
                    try:
                        ProfileManager(path, name).save_profile(self.tox.get_savedata())
                    except Exception as ex:
                        print(str(ex))
                        log('Profile creation exception: ' + str(ex))
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText(QtWidgets.QApplication.translate("login",
                                                                        'Profile saving error! Does Toxygen have permission to write to this directory?'))
                        msgBox.exec_()
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
                    self._tox = tox_factory(data, self._settings)
            else:
                path, name = auto_profile
                self._settings = Settings(self._toxes, path + name + '.json')
                self._profile_manager = ProfileManager(self._settings, self._toxes, path)
                data = self._profile_manager.open_profile()
                if encrypt_save.is_data_encrypted(data):
                    data = self.enter_pass(data)
                self.tox = tox_factory(data, self._settings)

        if Settings.is_active_profile(path, get_profile_name_from_path(path)):  # profile is in use
            reply = QtWidgets.QMessageBox.question(None,
                                                   'Profile {}'.format(name),
                                                   QtWidgets.QApplication.translate("login", 'Other instance of Toxygen uses this profile or profile was not properly closed. Continue?'),
                                                   QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
            if reply != QtWidgets.QMessageBox.Yes:
                return
        else:
            self._settings.set_active_profile()

        self.load_app_styles()
        self.load_app_translations()

        # tray icon

        self.ms = MainWindow(self._settings, self._tox, self.reset, self.tray)
        self._profile = self.ms.profile
        self.ms.show()

        updating = updater.start_update_if_needed(self._version, self._settings)
        if updating:
            data = self.tox.get_savedata()
            self._profile_manager.save_profile(data)
            self._settings.close()
            del self.tox
            return

        plugin_helper = PluginLoader(self._tox, self._toxes, self._profile, self._settings)  # plugin support
        plugin_helper.load()

        # init thread
        self.init = threads.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting threads for tox iterate and toxav iterate
        self.mainloop = threads.ToxIterateThread(self._tox)
        self.mainloop.start()
        self.avloop = threads.ToxAVIterateThread(self._tox.AV)
        self.avloop.start()

        if self.uri is not None:
            self.ms.add_contact(self.uri)

        app.lastWindowClosed.connect(app.quit)
        app.exec_()

        self.init.stop = True
        self.mainloop.stop = True
        self.avloop.stop = True
        plugin_helper.stop()
        self.mainloop.wait()
        self.init.wait()
        self.avloop.wait()
        self.tray.hide()
        data = self.tox.get_savedata()
        self._profile_manager.save_profile(data)
        self._settings.close()
        del self.tox

    def reset(self):
        """
        Create new tox instance (new network settings)
        :return: tox instance
        """
        self.mainloop.stop = True
        self.init.stop = True
        self.avloop.stop = True
        self.mainloop.wait()
        self.init.wait()
        self.avloop.wait()
        data = self.tox.get_savedata()
        self._profile_manager.save_profile(data)
        del self.tox
        # create new tox instance
        self.tox = tox_factory(data, self._settings)
        # init thread
        self.init = threads.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting threads for tox iterate and toxav iterate
        self.mainloop = threads.ToxIterateThread(self.tox)
        self.mainloop.start()

        self.avloop = threads.ToxAVIterateThread(self.tox.AV)
        self.avloop.start()

        self._plugin_loader.set_tox(self.tox)

        return self.tox

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
