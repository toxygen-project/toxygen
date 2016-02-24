from PySide import QtGui, QtCore
# TODO: add sound notifications


def tray_notification(title, text):
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        tray = QtGui.QSystemTrayIcon()
        tray.setContextMenu(QtGui.QMenu())
        tray.show()
        tray.showMessage(title, text)
