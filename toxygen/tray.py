self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(curr_directory() + '/images/icon.png'))
        self.tray.setObjectName('tray')

        class Menu(QtWidgets.QMenu):

            def newStatus(self, status):
                if not Settings.get_instance().locked:
                    profile.Profile.get_instance().set_status(status)
                    self.aboutToShowHandler()
                    self.hide()

            def aboutToShowHandler(self):
                status = profile.Profile.get_instance().status
                act = self.act
                if status is None or Settings.get_instance().locked:
                    self.actions()[1].setVisible(False)
                else:
                    self.actions()[1].setVisible(True)
                    act.actions()[0].setChecked(False)
                    act.actions()[1].setChecked(False)
                    act.actions()[2].setChecked(False)
                    act.actions()[status].setChecked(True)
                self.actions()[2].setVisible(not Settings.get_instance().locked)

            def languageChange(self, *args, **kwargs):
                self.actions()[0].setText(QtWidgets.QApplication.translate('tray', 'Open Toxygen'))
                self.actions()[1].setText(QtWidgets.QApplication.translate('tray', 'Set status'))
                self.actions()[2].setText(QtWidgets.QApplication.translate('tray', 'Exit'))
                self.act.actions()[0].setText(QtWidgets.QApplication.translate('tray', 'Online'))
                self.act.actions()[1].setText(QtWidgets.QApplication.translate('tray', 'Away'))
                self.act.actions()[2].setText(QtWidgets.QApplication.translate('tray', 'Busy'))

        m = Menu()
        show = m.addAction(QtWidgets.QApplication.translate('tray', 'Open Toxygen'))
        sub = m.addMenu(QtWidgets.QApplication.translate('tray', 'Set status'))
        onl = sub.addAction(QtWidgets.QApplication.translate('tray', 'Online'))
        away = sub.addAction(QtWidgets.QApplication.translate('tray', 'Away'))
        busy = sub.addAction(QtWidgets.QApplication.translate('tray', 'Busy'))
        onl.setCheckable(True)
        away.setCheckable(True)
        busy.setCheckable(True)
        m.act = sub
        exit = m.addAction(QtWidgets.QApplication.translate('tray', 'Exit'))

        def show_window():
            s = Settings.get_instance()

            def show():
                if not self.ms.isActiveWindow():
                    self.ms.setWindowState(self.ms.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                    self.ms.activateWindow()
                self.ms.show()
            if not s.locked:
                show()
            else:
                def correct_pass():
                    show()
                    s.locked = False
                    s.unlockScreen = False
                if not s.unlockScreen:
                    s.unlockScreen = True
                    self.p = UnlockAppScreen(toxes.ToxES.get_instance(), correct_pass)
                    self.p.show()

        def tray_activated(reason):
            if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
                show_window()

        def close_app():
            if not Settings.get_instance().locked:
                settings.closing = True
                self.ms.close()

        show.triggered.connect(show_window)
        exit.triggered.connect(close_app)
        m.aboutToShow.connect(lambda: m.aboutToShowHandler())
        onl.triggered.connect(lambda: m.newStatus(0))
        away.triggered.connect(lambda: m.newStatus(1))
        busy.triggered.connect(lambda: m.newStatus(2))

        self.tray.setContextMenu(m)
        self.tray.show()
        self.tray.activated.connect(tray_activated)