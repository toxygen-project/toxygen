from loginscreen import LoginScreen
from settings import Settings
from mainscreen import MainWindow
from profile import Profile
import sys
from PySide import QtCore, QtGui
from tox import Tox


class login(object):

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


def main():
    """
    main function of app. loads loginscreen if needed and starts mainscreen
    """
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('images/icon.png'))
    settings = Settings()
    if not settings['auto_profile']:
        # show login screen if default profile not found
        ls = LoginScreen()
        ls.setWindowIconText("Toxygen")
        profiles = Profile.find_profiles()
        ls.update_select(map(lambda x: x[1], profiles))
        _login = login(profiles)
        ls.update_on_close(_login.login_screen_close)
        ls.show()
        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
        app.exec_()
        if not _login.t:
            return
        elif _login.t == 1:  # create new profile
            # TODO: add creation of new profile
            path = Settings.get_default_path()
            name = _login.name if _login.name else 'Toxygen User'
            return
        else:  # load existing profile
            path, name = _login.get_data()
            if _login.default:
                settings['auto_profile'] = (path, name)
                settings.save()
    else:
        path, name = settings['auto_profile']
    # loading profile
    print str(path), str(name)
    data = Profile.open_profile(path, name)
    # TODO: start tox iterate and set callbacks
    tox = Tox(data, settings)
    ms = MainWindow()
    ms.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()
    del tox


class ToxIterateThread(QtCore.QThread):

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        pass


if __name__ == '__main__':
    main()
