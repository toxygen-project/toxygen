from widgets import CenteredWidget
from PySide import QtCore, QtGui


class PasswordArea(QtGui.QLineEdit):

    def __init__(self, parent):
        super(PasswordArea, self).__init__(parent)
        self.parent = parent
        self.setEchoMode(QtGui.QLineEdit.EchoMode.Password)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.parent.button_click()
        else:
            super(PasswordArea, self).keyPressEvent(event)


class PasswordScreen(CenteredWidget):

    def __init__(self, encrypt, data):
        super(PasswordScreen, self).__init__()
        self._encrypt = encrypt
        self._data = data
        self.initUI()

    def initUI(self):
        self.resize(360, 170)
        self.setMinimumSize(QtCore.QSize(360, 170))
        self.setMaximumSize(QtCore.QSize(360, 170))

        self.enter_pass = QtGui.QLabel(self)
        self.enter_pass.setGeometry(QtCore.QRect(30, 10, 300, 30))

        self.password = PasswordArea(self)
        self.password.setGeometry(QtCore.QRect(30, 50, 300, 30))

        self.button = QtGui.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(30, 90, 300, 30))
        self.button.setText('OK')
        self.button.clicked.connect(self.button_click)

        self.warning = QtGui.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(30, 130, 300, 30))
        self.warning.setStyleSheet('QLabel { color: #F70D1A; }')
        self.warning.setVisible(False)

        self.retranslateUi()
        self.center()
        QtCore.QMetaObject.connectSlotsByName(self)

    def button_click(self):
        if self.password.text():
            try:
                self._encrypt.set_password(self.password.text())
                new_data = self._encrypt.pass_decrypt(self._data[0])
            except Exception:
                self.warning.setVisible(True)
            else:
                self._data[0] = new_data
                self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            self.button_click()
        else:
            super(PasswordScreen, self).keyPressEvent(event)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("pass", "Enter password", None, QtGui.QApplication.UnicodeUTF8))
        self.enter_pass.setText(QtGui.QApplication.translate("pass", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.warning.setText(QtGui.QApplication.translate("pass", "Incorrect password", None, QtGui.QApplication.UnicodeUTF8))

