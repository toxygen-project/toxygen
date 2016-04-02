from PySide import QtGui, QtCore
from PySide.phonon import Phonon
from util import curr_directory
# TODO: rewrite sound notifications


SOUND_NOTIFICATION = {
    'MESSAGE': 0,
    'FRIEND_CONNECTION_STATUS': 1,
    'FILE_TRANSFER': 2
}


def tray_notification(title, text, tray, window):
    """
    Show tray notification and activate window icon
    NOTE: different behaviour on different OS
    :param title: Name of user who sent message or file
    :param text: text of message or file info
    :param tray: ref to tray icon
    :param window: main window
    """
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        if len(text) > 30:
            text = text[:27] + '...'
        tray.showMessage(title, text, QtGui.QSystemTrayIcon.NoIcon, 3000)
        QtGui.QApplication.alert(window, 0)

        def message_clicked():
            window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
            window.activateWindow()
        tray.connect(tray, QtCore.SIGNAL("messageClicked()"), message_clicked)


def sound_notification(t):
    """
    Plays sound notification
    :param t: type of notification
    """
    if t == SOUND_NOTIFICATION['MESSAGE']:
        f = curr_directory() + '/sounds/message.wav'
    elif t == SOUND_NOTIFICATION['FILE_TRANSFER']:
        f = curr_directory() + '/sounds/file.wav'
    else:
        f = curr_directory() + '/sounds/contact.wav'
    m = Phonon.MediaSource(f)
    player = Phonon.createPlayer(Phonon.MusicCategory, m)
    player.play()
