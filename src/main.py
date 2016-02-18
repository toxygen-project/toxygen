from loginscreen import LoginScreen
from settings import Settings
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

        ls.update_select(['tox_save'])
        win.show()
        app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
        app.exec_()
    # TODO: get result from loginscreen and open mainscreen
