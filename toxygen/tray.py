from PyQt5 import QtWidgets, QtGui, QtCore
from util.ui import tr
from util.util import curr_directory


class Menu(QtWidgets.QMenu):

    def __init__(self, settings, profile, *args):
        super().__init__(*args)
        self._settings = settings
        self._profile = profile

    def newStatus(self, status):
        if not self._settings.locked:
            self._profile.Profile.get_instance().set_status(status)
            self.aboutToShowHandler()
            self.hide()

    def aboutToShowHandler(self):
        status = self._profile.status
        act = self.act
        if status is None or self._ettings.get_instance().locked:
            self.actions()[1].setVisible(False)
        else:
            self.actions()[1].setVisible(True)
            act.actions()[0].setChecked(False)
            act.actions()[1].setChecked(False)
            act.actions()[2].setChecked(False)
            act.actions()[status].setChecked(True)
        self.actions()[2].setVisible(not self._settings.locked)

    def languageChange(self, *args, **kwargs):
        self.actions()[0].setText(tr('Open Toxygen'))
        self.actions()[1].setText(tr('Set status'))
        self.actions()[2].setText(tr('Exit'))
        self.act.actions()[0].setText(tr('Online'))
        self.act.actions()[1].setText(tr('Away'))
        self.act.actions()[2].setText(tr('Busy'))


def init_tray(profile, settings, main_screen):
    tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
    tray.setObjectName('tray')

    m = Menu(settings, profile)
    show = m.addAction(tr('Open Toxygen'))
    sub = m.addMenu(tr('Set status'))
    online = sub.addAction(tr('Online'))
    away = sub.addAction(tr('Away'))
    busy = sub.addAction(tr('Busy'))
    online.setCheckable(True)
    away.setCheckable(True)
    busy.setCheckable(True)
    m.act = sub
    exit = m.addAction(tr('Exit'))

    def show_window():
        def show():
            if not main_screen.isActiveWindow():
                main_screen.setWindowState(main_screen.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                main_screen.activateWindow()
                main_screen.show()
        if not settings.locked:
            show()
        else:
            def correct_pass():
                show()
                settings.locked = False
                settings.unlockScreen = False
            if not settings.unlockScreen:
                settings.unlockScreen = True
                self.p = UnlockAppScreen(toxes.ToxES.get_instance(), correct_pass)
                self.p.show()

    def tray_activated(reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            show_window()

    def close_app():
        if not settings.locked:
            settings.closing = True
            main_screen.close()

    show.triggered.connect(show_window)
    exit.triggered.connect(close_app)
    m.aboutToShow.connect(lambda: m.aboutToShowHandler())
    online.triggered.connect(lambda: m.newStatus(0))
    away.triggered.connect(lambda: m.newStatus(1))
    busy.triggered.connect(lambda: m.newStatus(2))

    tray.setContextMenu(m)
    tray.show()
    tray.activated.connect(tray_activated)

    return tray
