from PySide import QtGui
from PySide.phonon import Phonon
from util import curr_directory
# TODO: make app icon active


SOUND_NOTIFICATION = {
    'MESSAGE': 0,
    'FRIEND_CONNECTION_STATUS': 1,
    'FILE_TRANSFER': 2
}


def tray_notification(title, text):
    if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        tray = QtGui.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        tray.setContextMenu(QtGui.QMenu())
        tray.show()
        if len(text) > 30:
            text = text[:27] + '...'
        tray.showMessage(title, text, QtGui.QSystemTrayIcon.NoIcon, 3000)


def sound_notification(t):
    # TODO: add other sound notifications
    if t == SOUND_NOTIFICATION['MESSAGE']:
        f = curr_directory() + '/sounds/message.wav'
    else:
        return
    m = Phonon.MediaSource(f)
    player = Phonon.createPlayer(Phonon.MusicCategory, m)
    player.play()
