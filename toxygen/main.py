import sys
from loginscreen import LoginScreen
import profile
from settings import *
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from bootstrap import node_generator
from mainscreen import MainWindow
from callbacks import init_callbacks
from util import curr_directory, program_version
import styles.style
import platform
import toxencryptsave
from passwordscreen import PasswordScreen, UnlockAppScreen, SetProfilePasswordScreen
from plugin_support import PluginLoader


class Toxygen:

    def __init__(self, path_or_uri=None):
        super(Toxygen, self).__init__()
        self.tox = self.ms = self.init = self.mainloop = self.avloop = None
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
        p = PasswordScreen(toxencryptsave.ToxEncryptSave.get_instance(), tmp)
        p.show()
        self.app.connect(self.app, QtCore.SIGNAL("lastWindowClosed()"), self.app, QtCore.SLOT("quit()"))
        self.app.exec_()
        if tmp[0] == data:
            raise SystemExit()
        else:
            return tmp[0]

    def main(self):
        """
        Main function of app. loads login screen if needed and starts main screen
        """
        app = QtGui.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        self.app = app

        if platform.system() == 'Linux':
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)

        # application color scheme
        with open(curr_directory() + '/styles/style.qss') as fl:
            dark_style = fl.read()
        app.setStyleSheet(dark_style)

        encrypt_save = toxencryptsave.ToxEncryptSave()

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
                app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
                app.exec_()
                if not _login.t:
                    return
                elif _login.t == 1:  # create new profile
                    _login.name = _login.name.strip()
                    name = _login.name if _login.name else 'toxygen_user'
                    pr = map(lambda x: x[1], ProfileHelper.find_profiles())
                    if name in list(pr):
                        msgBox = QtGui.QMessageBox()
                        msgBox.setWindowTitle(
                            QtGui.QApplication.translate("MainWindow", "Error", None, QtGui.QApplication.UnicodeUTF8))
                        text = (QtGui.QApplication.translate("MainWindow",
                                                             'Profile with this name already exists',
                                                             None, QtGui.QApplication.UnicodeUTF8))
                        msgBox.setText(text)
                        msgBox.exec_()
                        return
                    self.tox = profile.tox_factory()
                    self.tox.self_set_name(bytes(_login.name, 'utf-8') if _login.name else b'Toxygen User')
                    self.tox.self_set_status_message(b'Toxing on Toxygen')
                    reply = QtGui.QMessageBox.question(None,
                                                       'Profile {}'.format(name),
                                                       QtGui.QApplication.translate("login",
                                                                                    'Do you want to set profile password?',
                                                                                    None,
                                                                                    QtGui.QApplication.UnicodeUTF8),
                                                       QtGui.QMessageBox.Yes,
                                                       QtGui.QMessageBox.No)
                    if reply == QtGui.QMessageBox.Yes:
                        set_pass = SetProfilePasswordScreen(encrypt_save)
                        set_pass.show()
                        self.app.connect(self.app, QtCore.SIGNAL("lastWindowClosed()"), self.app, QtCore.SLOT("quit()"))
                        self.app.exec_()
                    ProfileHelper(Settings.get_default_path(), name).save_profile(self.tox.get_savedata())
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
            reply = QtGui.QMessageBox.question(None,
                                               'Profile {}'.format(name),
                                               QtGui.QApplication.translate("login", 'Other instance of Toxygen uses this profile or profile was not properly closed. Continue?', None, QtGui.QApplication.UnicodeUTF8),
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply != QtGui.QMessageBox.Yes:
                return
        else:
            settings.set_active_profile()

        lang = Settings.supported_languages()[settings['language']]
        translator = QtCore.QTranslator()
        translator.load(curr_directory() + '/translations/' + lang)
        app.installTranslator(translator)
        app.translator = translator

        # tray icon
        self.tray = QtGui.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        self.tray.setObjectName('tray')

        self.ms = MainWindow(self.tox, self.reset, self.tray)

        class Menu(QtGui.QMenu):

            def newStatus(self, status):
                profile.Profile.get_instance().set_status(status)
                self.aboutToShow()
                self.hide()

            def aboutToShow(self):
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
                self.actions()[0].setText(QtGui.QApplication.translate('tray', 'Open Toxygen', None, QtGui.QApplication.UnicodeUTF8))
                self.actions()[1].setText(QtGui.QApplication.translate('tray', 'Set status', None, QtGui.QApplication.UnicodeUTF8))
                self.actions()[2].setText(QtGui.QApplication.translate('tray', 'Exit', None, QtGui.QApplication.UnicodeUTF8))
                self.act.actions()[0].setText(QtGui.QApplication.translate('tray', 'Online', None, QtGui.QApplication.UnicodeUTF8))
                self.act.actions()[1].setText(QtGui.QApplication.translate('tray', 'Away', None, QtGui.QApplication.UnicodeUTF8))
                self.act.actions()[2].setText(QtGui.QApplication.translate('tray', 'Busy', None, QtGui.QApplication.UnicodeUTF8))

        m = Menu()
        show = m.addAction(QtGui.QApplication.translate('tray', 'Open Toxygen', None, QtGui.QApplication.UnicodeUTF8))
        sub = m.addMenu(QtGui.QApplication.translate('tray', 'Set status', None, QtGui.QApplication.UnicodeUTF8))
        onl = sub.addAction(QtGui.QApplication.translate('tray', 'Online', None, QtGui.QApplication.UnicodeUTF8))
        away = sub.addAction(QtGui.QApplication.translate('tray', 'Away', None, QtGui.QApplication.UnicodeUTF8))
        busy = sub.addAction(QtGui.QApplication.translate('tray', 'Busy', None, QtGui.QApplication.UnicodeUTF8))
        onl.setCheckable(True)
        away.setCheckable(True)
        busy.setCheckable(True)
        m.act = sub
        exit = m.addAction(QtGui.QApplication.translate('tray', 'Exit', None, QtGui.QApplication.UnicodeUTF8))

        def show_window():
            def show():
                if not self.ms.isActiveWindow():
                    self.ms.setWindowState(self.ms.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                    self.ms.activateWindow()
                self.ms.show()
            if not Settings.get_instance().locked:
                show()
            else:
                def correct_pass():
                    show()
                    Settings.get_instance().locked = False
                self.p = UnlockAppScreen(toxencryptsave.ToxEncryptSave.get_instance(), correct_pass)
                self.p.show()

        m.connect(show, QtCore.SIGNAL("triggered()"), show_window)
        m.connect(exit, QtCore.SIGNAL("triggered()"), lambda: app.exit())
        m.connect(m, QtCore.SIGNAL("aboutToShow()"), lambda: m.aboutToShow())
        sub.connect(onl, QtCore.SIGNAL("triggered()"), lambda: m.newStatus(0))
        sub.connect(away, QtCore.SIGNAL("triggered()"), lambda: m.newStatus(1))
        sub.connect(busy, QtCore.SIGNAL("triggered()"), lambda: m.newStatus(2))

        self.tray.setContextMenu(m)
        self.tray.show()

        self.ms.show()

        plugin_helper = PluginLoader(self.tox, settings)  # plugin support
        plugin_helper.load()

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

        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
        app.exec_()
        self.init.stop = True
        self.mainloop.stop = True
        self.avloop.stop = True
        plugin_helper.stop()
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
    for fl in ('libtox64.dll', 'libtox.dll', 'libsodium64.a', 'libsodium.a'):
        if os.path.exists(d + fl):
            os.remove(d + fl)


def configure():
    """Removes unused libs"""
    d = curr_directory() + '/libs/'
    is_64bits = sys.maxsize > 2 ** 32
    if not is_64bits:
        if os.path.exists(d + 'libtox64.dll'):
            os.remove(d + 'libtox64.dll')
        if os.path.exists(d + 'libsodium64.a'):
            os.remove(d + 'libsodium64.a')
    else:
        if os.path.exists(d + 'libtox.dll'):
            os.remove(d + 'libtox.dll')
        if os.path.exists(d + 'libsodium.a'):
            os.remove(d + 'libsodium.a')
        try:
            os.rename(d + 'libtox64.dll', d + 'libtox.dll')
            os.rename(d + 'libsodium64.a', d + 'libsodium.a')
        except:
            pass


def main():
    if len(sys.argv) == 1:
        toxygen = Toxygen()
    else:  # started with argument(s)
        arg = sys.argv[1]
        if arg == '--version':
            print('Toxygen ' + program_version)
            return
        elif arg == '--help':
            print('Usage:\ntoxygen path_to_profile\ntoxygen tox_id\ntoxygen --version')
            return
        elif arg == '--configure':
            configure()
            return
        elif arg == '--clean':
            clean()
            return
        else:
            toxygen = Toxygen(arg)
    toxygen.main()


if __name__ == '__main__':
    main()
