import sys
from loginscreen import LoginScreen
from settings import Settings
from PySide import QtCore, QtGui
from bootstrap import node_generator
from mainscreen import MainWindow
from profile import ProfileHelper, tox_factory
from callbacks import init_callbacks
from util import curr_directory, get_style
import styles.style


class Toxygen(object):

    def __init__(self):
        super(Toxygen, self).__init__()
        self.tox = self.ms = self.init = self.mainloop = None

    def main(self):
        """
            main function of app. loads login screen if needed and starts main screen
        """
        app = QtGui.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))

        # application color scheme
        with open(curr_directory() + '/styles/style.qss') as fl:
            dark_style = fl.read()
        app.setStyleSheet(dark_style)

        auto_profile = Settings.get_auto_profile()
        if not auto_profile:
            # show login screen if default profile not found
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
                name = _login.name if _login.name else 'toxygen_user'
                settings = Settings(name)
                self.tox = tox_factory()
                self.tox.self_set_name(_login.name if _login.name else 'Toxygen User')
                self.tox.self_set_status_message('Toxing on Toxygen')
                ProfileHelper.save_profile(self.tox.get_savedata(), name)
            else:  # load existing profile
                path, name = _login.get_data()
                settings = Settings(name)
                if _login.default:
                    Settings.set_auto_profile(path, name)
                data = ProfileHelper.open_profile(path, name)
                self.tox = tox_factory(data, settings)
        else:
            path, name = auto_profile
            settings = Settings(name)
            data = ProfileHelper.open_profile(path, name)
            self.tox = tox_factory(data, settings)

        self.ms = MainWindow(self.tox, self.reset)

        # tray icon
        self.tray = QtGui.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        m = QtGui.QMenu()
        show = m.addAction('Open Toxygen')
        exit = m.addAction('Exit')

        def show_window():
            if not self.ms.isActiveWindow():
                self.ms.setWindowState(self.ms.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                self.ms.activateWindow()

        m.connect(show, QtCore.SIGNAL("triggered()"), show_window)
        m.connect(exit, QtCore.SIGNAL("triggered()"), lambda: app.exit())
        self.tray.setContextMenu(m)
        self.tray.show()

        self.ms.show()
        QtGui.QApplication.setStyle(get_style(settings['theme']))  # set application style

        # init thread
        self.init = self.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting thread for tox iterate
        self.mainloop = self.ToxIterateThread(self.tox)
        self.mainloop.start()
        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
        app.exec_()
        self.init.stop = True
        self.mainloop.stop = True
        self.mainloop.wait()
        self.init.wait()
        data = self.tox.get_savedata()
        ProfileHelper.save_profile(data)
        del self.tox

    def reset(self):
        """
        Create new tox instance (new network settings)
        :return: tox instance
        """
        self.mainloop.stop = True
        self.init.stop = True
        self.mainloop.wait()
        self.init.wait()
        data = self.tox.get_savedata()
        ProfileHelper.save_profile(data)
        del self.tox
        # create new tox instance
        self.tox = tox_factory(data, Settings.get_instance())
        # init thread
        self.init = self.InitThread(self.tox, self.ms, self.tray)
        self.init.start()

        # starting thread for tox iterate
        self.mainloop = self.ToxIterateThread(self.tox)
        self.mainloop.start()
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
                    self.tox.bootstrap(*data)
            except:
                pass
            self.msleep(10000)
            while not self.tox.self_get_connection_status() and not self.stop:
                try:
                    for data in node_generator():
                        self.tox.bootstrap(*data)
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

    class Login(object):

        def __init__(self, arr):
            self.arr = arr

        def login_screen_close(self, t, number=-1, default=False, name=None):
            """ Function which processes data from login screen
            :param t: 0 - window was closed, 1 - new profile was created, 2 - profile loaded
            :param number: num of choosen profile in list (-1 by default)
            :param default: was or not choosen profile marked as default
            :param name: name of new profile
            """
            print str(t), str(number), str(default), str(name)
            self.t = t
            self.num = number
            self.default = default
            self.name = name

        def get_data(self):
            return self.arr[self.num]


if __name__ == '__main__':
    # TODO: add command line options
    toxygen = Toxygen()
    toxygen.main()
