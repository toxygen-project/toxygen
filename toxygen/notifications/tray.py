from PyQt5 import QtCore, QtWidgets


def tray_notification(title, text, tray, window):
    """
    Show tray notification and activate window icon
    NOTE: different behaviour on different OS
    :param title: Name of user who sent message or file
    :param text: text of message or file info
    :param tray: ref to tray icon
    :param window: main window
    """
    if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
        if len(text) > 30:
            text = text[:27] + '...'
        tray.showMessage(title, text, QtWidgets.QSystemTrayIcon.NoIcon, 3000)
        QtWidgets.QApplication.alert(window, 0)

        def message_clicked():
            window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            window.activateWindow()
        tray.messageClicked.connect(message_clicked)
