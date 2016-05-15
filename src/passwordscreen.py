from widgets import CenteredWidget
from PySide import QtCore, QtGui

# TODO: add onclick


class PasswordScreen(CenteredWidget):

    def __init__(self, encrypt):
        super(PasswordScreen, self).__init__()
        self._encrypt = encrypt
        self.initUI()

    def initUI(self):
        self.resize(360, 200)
        self.setMinimumSize(QtCore.QSize(360, 200))
        self.setMaximumSize(QtCore.QSize(360, 200))

        self.enter_pass = QtGui.QLabel(self)
        self.enter_pass.setGeometry(QtCore.QRect(30, 10, 300, 30))

        self.password = QtGui.QLineEdit(self)
        self.password.setGeometry(QtCore.QRect(30, 80, 300, 30))
        self.password.setEchoMode(QtGui.QLineEdit.EchoMode.Password)

        self.button = QtGui.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(30, 120, 300, 30))
        self.button.setText('OK')

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("pass", "Enter password", None, QtGui.QApplication.UnicodeUTF8))
        self.enter_pass.setText(QtGui.QApplication.translate("pass", "Password:", None, QtGui.QApplication.UnicodeUTF8))

