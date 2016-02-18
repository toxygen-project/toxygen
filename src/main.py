from loginscreen import LoginScreen
from settings import Settings
from profile import Profile
import sys
from PySide import QtCore, QtGui


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    settings = Settings()
    if not settings['auto_profile']:
        # show login screen if default profile not found
        ls = LoginScreen()
        win = QtGui.QMainWindow()
        ls.setupUi(win)
        profiles = Profile.find_profiles()
        ls.update_select(map(lambda x: x[1], profiles))
        win.show()
        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
        app.exec_()
        # TODO: get result from loginscreen
        # add new default profile (if needed)
        # save selected profile to open
        # create new profile?
    else:
        path, name = settings['auto_profile']
    # TODO: open mainscreen
