from PySide import QtGui
# TODO: add sound notifications
# TODO: add reaction om mouse move


def tray_notification(title, text):
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        tray = QtGui.QSystemTrayIcon()
        tray.setContextMenu(QtGui.QMenu())
        tray.show()
        if len(text) > 50:
            text = text[:50] + '...'
        tray.showMessage(title, text, QtGui.QSystemTrayIcon.NoIcon, 4000)
