from PySide import QtGui
from util import curr_directory
# TODO: add sound notifications
# TODO: add reaction om mouse move


def tray_notification(title, text):
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        tray = QtGui.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        tray.setContextMenu(QtGui.QMenu())
        tray.show()
        if len(text) > 30:
            text = text[:30] + '...'
        tray.showMessage(title, text, QtGui.QSystemTrayIcon.NoIcon, 3000)
