from widgets import CenteredWidget, LineEdit
from PyQt5 import QtCore, QtWidgets


class PasswordArea(LineEdit):

    def __init__(self, parent):
        super(PasswordArea, self).__init__(parent)
        self.parent = parent
        self.setEchoMode(QtWidgets.QLineEdit.Password)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.parent.button_click()
        else:
            super(PasswordArea, self).keyPressEvent(event)


class PasswordScreenBase(CenteredWidget):

    def __init__(self, encrypt):
        super(PasswordScreenBase, self).__init__()
        self._encrypt = encrypt
        self.initUI()

    def initUI(self):
        self.resize(360, 170)
        self.setMinimumSize(QtCore.QSize(360, 170))
        self.setMaximumSize(QtCore.QSize(360, 170))

        self.enter_pass = QtWidgets.QLabel(self)
        self.enter_pass.setGeometry(QtCore.QRect(30, 10, 300, 30))

        self.password = PasswordArea(self)
        self.password.setGeometry(QtCore.QRect(30, 50, 300, 30))

        self.button = QtWidgets.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(30, 90, 300, 30))
        self.button.setText('OK')
        self.button.clicked.connect(self.button_click)

        self.warning = QtWidgets.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(30, 130, 300, 30))
        self.warning.setStyleSheet('QLabel { color: #F70D1A; }')
        self.warning.setVisible(False)

        self.retranslateUi()
        self.center()
        QtCore.QMetaObject.connectSlotsByName(self)

    def button_click(self):
        pass

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            self.button_click()
        else:
            super(PasswordScreenBase, self).keyPressEvent(event)

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("pass", "Enter password"))
        self.enter_pass.setText(QtWidgets.QApplication.translate("pass", "Password:"))
        self.warning.setText(QtWidgets.QApplication.translate("pass", "Incorrect password"))


class PasswordScreen(PasswordScreenBase):

    def __init__(self, encrypt, data):
        super(PasswordScreen, self).__init__(encrypt)
        self._data = data

    def button_click(self):
        if self.password.text():
            try:
                self._encrypt.set_password(self.password.text())
                new_data = self._encrypt.pass_decrypt(self._data[0])
            except Exception as ex:
                self.warning.setVisible(True)
                print('Decryption error:', ex)
            else:
                self._data[0] = new_data
                self.close()


class UnlockAppScreen(PasswordScreenBase):

    def __init__(self, encrypt, callback):
        super(UnlockAppScreen, self).__init__(encrypt)
        self._callback = callback
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def button_click(self):
        if self.password.text():
            if self._encrypt.is_password(self.password.text()):
                self._callback()
                self.close()
            else:
                self.warning.setVisible(True)
                print('Wrong password!')


class SetProfilePasswordScreen(CenteredWidget):

    def __init__(self, encrypt):
        super(SetProfilePasswordScreen, self).__init__()
        self._encrypt = encrypt
        self.initUI()
        self.retranslateUi()
        self.center()

    def initUI(self):
        self.setMinimumSize(QtCore.QSize(700, 200))
        self.setMaximumSize(QtCore.QSize(700, 200))
        self.password = LineEdit(self)
        self.password.setGeometry(QtCore.QRect(40, 10, 300, 30))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password = LineEdit(self)
        self.confirm_password.setGeometry(QtCore.QRect(40, 50, 300, 30))
        self.confirm_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.set_password = QtWidgets.QPushButton(self)
        self.set_password.setGeometry(QtCore.QRect(40, 100, 300, 30))
        self.set_password.clicked.connect(self.new_password)
        self.not_match = QtWidgets.QLabel(self)
        self.not_match.setGeometry(QtCore.QRect(350, 50, 300, 30))
        self.not_match.setVisible(False)
        self.not_match.setStyleSheet('QLabel { color: #BC1C1C; }')
        self.warning = QtWidgets.QLabel(self)
        self.warning.setGeometry(QtCore.QRect(40, 160, 500, 30))
        self.warning.setStyleSheet('QLabel { color: #BC1C1C; }')

    def retranslateUi(self):
        self.setWindowTitle(QtWidgets.QApplication.translate("PasswordScreen", "Profile password"))
        self.password.setPlaceholderText(
            QtWidgets.QApplication.translate("PasswordScreen", "Password (at least 8 symbols)"))
        self.confirm_password.setPlaceholderText(
            QtWidgets.QApplication.translate("PasswordScreen", "Confirm password"))
        self.set_password.setText(
            QtWidgets.QApplication.translate("PasswordScreen", "Set password"))
        self.not_match.setText(QtWidgets.QApplication.translate("PasswordScreen", "Passwords do not match"))
        self.warning.setText(
            QtWidgets.QApplication.translate("PasswordScreen", "There is no way to recover lost passwords"))

    def new_password(self):
        if self.password.text() == self.confirm_password.text():
            if len(self.password.text()) >= 8:
                self._encrypt.set_password(self.password.text())
                self.close()
            else:
                self.not_match.setText(
                    QtWidgets.QApplication.translate("PasswordScreen", "Password must be at least 8 symbols"))
            self.not_match.setVisible(True)
        else:
            self.not_match.setText(QtWidgets.QApplication.translate("PasswordScreen", "Passwords do not match"))
            self.not_match.setVisible(True)
