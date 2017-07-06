import sys
from loginscreen import LoginScreen
import profile
from settings import *
from PyQt5 import QtCore, QtGui, QtWidgets
from bootstrap import node_generator
from mainscreen import MainWindow
from callbacks import init_callbacks, stop, start
from util import curr_directory, program_version, remove, is_64_bit
import styles.style
import platform
import toxes
from passwordscreen import PasswordScreen, UnlockAppScreen, SetProfilePasswordScreen
from plugin_support import PluginLoader
import updater


class Toxygen:

    def __init__(self, path_or_uri=None):
        super(Toxygen, self).__init__()
        self.tox = self.ms = self.init = self.app = self.tray = self.mainloop = self.avloop = None
        if path_or_uri is None:
            self.uri = self.path = None
        elif path_or_uri.startswith('tox:'):
            self.path = None
            self.uri = path_or_uri[4:]
        else:
            self.path = path_or_uri
            self.uri = None

    def enter_pass(self, data):
        """
        Show password screen
        """
        tmp = [data]
        p = PasswordScreen(toxes.ToxES.get_instance(), tmp)
        p.show()
        self.app.lastWindowClosed.connect(self.app.quit)
        self.app.exec_()
        if tmp[0] == data:
            raise SystemExit()
        else:
            return tmp[0]

    def main(self):
        """
        Main function of app. loads login screen if needed and starts main screen
        """
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        self.app = app

        if platform.system() == 'Linux':
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

        with open(curr_directory() + '/styles/dark_style.qss') as fl:
            style = fl.read()
        app.setStyleSheet(style)

        encrypt_save = toxes.ToxES()

        if self.path is not None:
            path = os.path.dirname(self.path) + '/'
            name = os.path.basename(self.path)[:-4]
            data = ProfileHelper(path, name).open_profile()
            if encrypt_save.is_data_encrypted(data):
                data = self.enter_pass(data)
            settings = Settings(name)
            self.tox = profile.tox_factory(data, settings)
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
                profiles = ProfileHelper.find_profiles()
                ls.update_select(map(lambda x: x[1], profiles))
                _login = self.Login(profiles)
                ls.update_on_close(_login.login_screen_close)
                ls.show()
                app.exec_()
                if not _login.t:
                    return
                elif _login.t == 1:  # create new profile
                    _login.name = _login.name.strip()
                    name = _login.name if _login.name else 'toxygen_user'
                    pr = map(lambda x: x[1], ProfileHelper.find_profiles())
                    if name in list(pr):
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setWindowTitle(
                            QtWidgets.QApplication.translate("MainWindow", "Error"))
                        text = (QtWidgets.QApplication.translate("MainWindow",
                                                                 'Profile with this name already exists'))
                        msgBox.setText(text)
                        msgBox.exec_()
                        return
                    self.tox = profile.tox_factory()
                    self.tox.self_set_name(bytes(_login.name, 'utf-8') if _login.name else b'Toxygen User')
                    self.tox.self_set_status_message(b'Toxing on T03')
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
                        ProfileHelper(path, name).save_profile(self.tox.get_savedata())
                    except Exception as ex:
                        print(str(ex))
                        log('Profile creation exception: ' + str(ex))
                        msgBox = QtWidgets.QMessageBox()
                        msgBox.setText(QtWidgets.QApplication.translate("login",
                                                                        'Profile saving error! Does Toxygen have permission to write to this directory?'))
                        msgBox.exec_()
                        return
                    path = Settings.get_default_path()
                    settings = Settings(name)
                    if curr_lang in langs:
                        settings['language'] = curr_lang
                    settings.save()
                else:  # load existing profile
                    path, name = _login.get_data()
                    if _login.default:
                        Settings.set_auto_profile(path, name)
                    data = ProfileHelper(path, name).open_profile()
                    if encrypt_save.is_data_encrypted(data):
                        data = self.enter_pass(data)
                    settings = Settings(name)
                    self.tox = profile.tox_factory(data, settings)
            else:
                path, name = auto_profile
                data = ProfileHelper(path, name).open_profile()
                if encrypt_save.is_data_encrypted(data):
                    data = self.enter_pass(data)
                settings = Settings(name)
                self.tox = profile.tox_factory(data, settings)

        if Settings.is_active_profile(path, name):  # profile is in use
            reply = QtWidgets.QMessageBox.question(None,
                                                   'Profile {}'.format(name),
                                                   QtWidgets.QApplication.translate("login", 'Other instance of Toxygen uses this profile or profile was not properly closed. Continue?'),
                                                   QtWidgets.QMessageBox.Yes,
                                                   QtWidgets.QMessageBox.No)
            if reply != QtWidgets.QMessageBox.Yes:
                return
        else:
            settings.set_active_profile()

        # application color scheme
        for theme in settings.built_in_themes().keys():
            if settings['theme'] == theme:
                with open(curr_directory() + settings.built_in_themes()[theme]) as fl:
                    style = fl.read()
                app.setStyleSheet(style)

        lang = Settings.supported_languages()[settings['language']]
        translator = QtCore.QTranslator()
        translator.load(curr_directory() + '/translations/' + lang)
        app.installTranslator(translator)
        app.translator = translator

        # tray icon
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        self.tray.setObjectName('tray')

        self.ms = MainWindow(self.tox, self.reset, self.tray)
        app.aboutToQuit.connect(self.ms.close_window)

        class Menu(QtWidgets.QMenu):

            def newStatus(self, status):
                if not Settings.get_instance().locked:
                    profile.Profile.get_instance().set_status(status)
                    self.aboutToShowHandler()
                    self.hide()

            def aboutToShowHandler(self):
                status = profile.Profile.get_instance().status
                act = self.act
                if status is None or Settings.get_instance().locked:
                    self.actions()[1].setVisible(False)
                else:
                    self.actions()[1].setVisible(True)
                    act.actions()[0].setChecked(False)
                    act.actions()[1].setChecked(False)
                    act.actions()[2].setChecked(False)
                    act.actions()[status].setChecked(True)
                self.actions()[2].setVisible(not Settings.get_instance().locked)

            def languageChange(self, *args, **kwargs):
                self.actions()[0].setText(QtWidgets.QApplication.translate('tray', 'Open Toxygen'))
                self.actions()[1].setText(QtWidgets.QApplication.translate('tray', 'Set status'))
                self.actions()[2].setText(QtWidgets.QApplication.translate('tray', 'Exit'))
                self.act.actions()[0].setText(QtWidgets.QApplication.translate('tray', 'Online'))
                self.act.actions()[1].setText(QtWidgets.QApplication.translate('tray', 'Away'))
                self.act.actions()[2].setText(QtWidgets.QApplication.translate('tray', 'Busy'))

        m = Menu()
        show = m.addAction(QtWidgets.QApplication.translate('tray', 'Open Toxygen'))
        sub = m.addMenu(QtWidgets.QApplication.translate('tray', 'Set status'))
        onl = sub.addAction(QtWidgets.QApplication.translate('tray', 'Online'))
        away = sub.addAction(QtWidgets.QApplication.translate('tray', 'Away'))
        busy = sub.addAction(QtWidgets.QApplication.translate('tray', 'Busy'))
        onl.setCheckable(True)
        away.setCheckable(True)
        busy.setCheckable(True)
        m.act = sub
        exit = m.addAction(QtWidgets.QApplication.translate('tray', 'Exit'))

        def show_window():
            s = Settings.get_instance()

            def show():
                if not self.ms.isActiveWindow():
                    self.ms.setWindowState(self.ms.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                    self.ms.activateWindow()
                self.ms.show()
            if not s.locked:
                show()
            else:
                def correct_pass():
                    show()
                    s.locked = False
                    s.unlockScreen = False
                if not s.unlockScreen:
                    s.unlockScreen = True
                    self.p = UnlockAppScreen(toxes.ToxES.get_instance(), correct_pass)
                    self.p.show()

        def tray_activated(reason):
            if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
                show_window()

        def close_app():
            if not Settings.get_instance().locked:
                settings.closing = True
                self.ms.close()

        show.triggered.connect(show_window)
        exit.triggered.connect(close_app)
        m.aboutToShow.connect(lambda: m.aboutToShowHandler())
        onl.triggered.connect(lambda: m.newStatus(0))
        away.triggered.connect(lambda: m.newStatus(1))
        busy.triggered.connect(lambda: m.newStatus(2))

        self.tray.setContextMenu(m)
        self.tray.show()
        self.tray.activated.connect(tray_activated)

        self.ms.show()

        updating = False
        if settings['update'] and updater.updater_available() and updater.connection_available():  # auto update
            version = updater.check_for_updates()
            if version is not None:
                if settings['update'] == 2:
                    updater.download(version)
                    updating = True
                else:
                    reply = QtWidgets.QMessageBox.question(None,
                                                           'Toxygen',
                                                           QtWidgets.QApplication.translate("login",
                                                                                            'Update for Toxygen was found. Download and install it?'),
                                                           QtWidgets.QMessageBox.Yes,
                                                           QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        updater.download(version)
                        updating = True

        if updating:
            data = self.tox.get_savedata()
            ProfileHelper.get_instance().save_profile(data)
            settings.close()
            del self.tox
            return

        plugin_helper = PluginLoader(self.tox, settings)  # plugin support
        plugin_helper.load()

        start()
        # init thread
        self.init = self.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting threads for tox iterate and toxav iterate
        self.mainloop = self.ToxIterateThread(self.tox)
        self.mainloop.start()
        self.avloop = self.ToxAVIterateThread(self.tox.AV)
        self.avloop.start()

        if self.uri is not None:
            self.ms.add_contact(self.uri)

        app.lastWindowClosed.connect(app.quit)
        app.exec_()

        self.init.stop = True
        self.mainloop.stop = True
        self.avloop.stop = True
        plugin_helper.stop()
        stop()
        self.mainloop.wait()
        self.init.wait()
        self.avloop.wait()
        data = self.tox.get_savedata()
        ProfileHelper.get_instance().save_profile(data)
        settings.close()
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
        ProfileHelper.get_instance().save_profile(data)
        del self.tox
        # create new tox instance
        self.tox = profile.tox_factory(data, Settings.get_instance())
        # init thread
        self.init = self.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting threads for tox iterate and toxav iterate
        self.mainloop = self.ToxIterateThread(self.tox)
        self.mainloop.start()

        self.avloop = self.ToxAVIterateThread(self.tox.AV)
        self.avloop.start()

        plugin_helper = PluginLoader.get_instance()
        plugin_helper.set_tox(self.tox)

        return self.tox

    # -----------------------------------------------------------------------------------------------------------------
    # Inner classes
    # -----------------------------------------------------------------------------------------------------------------

    class InitThread(QtCore.QThread):

        def __init__(self, tox, ms, tray):
            QtCore.QThread.__init__(self)
            self.tox, self.ms, self.tray = tox, ms, tray
            self.stop = False

        def run(self):
            # initializing callbacks
            init_callbacks(self.tox, self.ms, self.tray)
            # bootstrap
            try:
                for data in node_generator():
                    if self.stop:
                        return
                    self.tox.bootstrap(*data)
                    self.tox.add_tcp_relay(*data)
            except:
                pass
            for _ in range(10):
                if self.stop:
                    return
                self.msleep(1000)
            while not self.tox.self_get_connection_status():
                try:
                    for data in node_generator():
                        if self.stop:
                            return
                        self.tox.bootstrap(*data)
                        self.tox.add_tcp_relay(*data)
                except:
                    pass
                finally:
                    self.msleep(5000)

    class ToxIterateThread(QtCore.QThread):

        def __init__(self, tox):
            QtCore.QThread.__init__(self)
            self.tox = tox
            self.stop = False

        def run(self):
            while not self.stop:
                self.tox.iterate()
                self.msleep(self.tox.iteration_interval())

    class ToxAVIterateThread(QtCore.QThread):

        def __init__(self, toxav):
            QtCore.QThread.__init__(self)
            self.toxav = toxav
            self.stop = False

        def run(self):
            while not self.stop:
                self.toxav.iterate()
                self.msleep(self.toxav.iteration_interval())

    class Login:

        def __init__(self, arr):
            self.arr = arr

        def login_screen_close(self, t, number=-1, default=False, name=None):
            """ Function which processes data from login screen
            :param t: 0 - window was closed, 1 - new profile was created, 2 - profile loaded
            :param number: num of chosen profile in list (-1 by default)
            :param default: was or not chosen profile marked as default
            :param name: name of new profile
            """
            self.t = t
            self.num = number
            self.default = default
            self.name = name

        def get_data(self):
            return self.arr[self.num]


def clean():
    """Removes all windows libs from libs folder"""
    d = curr_directory() + '/libs/'
    remove(d)


def reset():
    Settings.reset_auto_profile()


def main():
    if len(sys.argv) == 1:
        toxygen = Toxygen()
    else:  # started with argument(s)
        arg = sys.argv[1]
        if arg == '--version':
            print('Toxygen v' + program_version)
            return
        elif arg == '--help':
            print('Usage:\ntoxygen path_to_profile\ntoxygen tox_id\ntoxygen --version\ntoxygen --reset')
            return
        elif arg == '--clean':
            clean()
            return
        elif arg == '--reset':
            reset()
            return
        else:
            toxygen = Toxygen(arg)
    toxygen.main()


if __name__ == '__main__':
    main()
