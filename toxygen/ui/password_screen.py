from ui.widgets import CenteredWidget, LineEdit, DialogWithResult
from PyQt5 import QtCore, QtWidgets
import utils.ui as util_ui


class PasswordArea(LineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
        self.setEchoMode(QtWidgets.QLineEdit.Password)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self._parent.button_click()
        else:
            super().keyPressEvent(event)


class PasswordScreenBase(CenteredWidget, DialogWithResult):

    def __init__(self, encrypt):
        CenteredWidget.__init__(self)
        DialogWithResult.__init__(self)
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
        self.button.setText(util_ui.tr('OK'))
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
        self.setWindowTitle(util_ui.tr('Enter password'))
        self.enter_pass.setText(util_ui.tr('Password:'))
        self.warning.setText(util_ui.tr('Incorrect password'))


class PasswordScreen(PasswordScreenBase):

    def __init__(self, encrypt, data):
        super().__init__(encrypt)
        self._data = data

    def button_click(self):
        if self.password.text():
            try:
                self._encrypt.set_password(self.password.text())
                new_data = self._encrypt.pass_decrypt(self._data)
            except Exception as ex:
                self.warning.setVisible(True)
                print('Decryption error:', ex)
            else:
                self.close_with_result(new_data)


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
        self.setWindowTitle(util_ui.tr('Profile password'))
        self.password.setPlaceholderText(
            util_ui.tr('Password (at least 8 symbols)'))
        self.confirm_password.setPlaceholderText(
            util_ui.tr('Confirm password'))
        self.set_password.setText(
            util_ui.tr('Set password'))
        self.not_match.setText(util_ui.tr('Passwords do not match'))
        self.warning.setText(util_ui.tr('There is no way to recover lost passwords'))

    def new_password(self):
        if self.password.text() == self.confirm_password.text():
            if len(self.password.text()) >= 8:
                self._encrypt.set_password(self.password.text())
                self.close()
            else:
                self.not_match.setText(util_ui.tr('Password must be at least 8 symbols'))
            self.not_match.setVisible(True)
        else:
            self.not_match.setText(util_ui.tr('Passwords do not match'))
            self.not_match.setVisible(True)
