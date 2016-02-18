# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import sys
import os


class LoginScreen(QtGui.QWidget):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 200)
        Form.setMinimumSize(QtCore.QSize(400, 200))
        Form.setMaximumSize(QtCore.QSize(400, 200))
        Form.setBaseSize(QtCore.QSize(400, 200))
        self.new_profile = QtGui.QPushButton(Form)
        self.new_profile.setGeometry(QtCore.QRect(20, 150, 171, 27))
        self.new_profile.setObjectName("new_profile")
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 70, 101, 17))
        self.label.setObjectName("label")
        self.new_name = QtGui.QPlainTextEdit(Form)
        self.new_name.setGeometry(QtCore.QRect(20, 100, 171, 31))
        self.new_name.setObjectName("new_name")
        self.load_profile = QtGui.QPushButton(Form)
        self.load_profile.setGeometry(QtCore.QRect(220, 150, 161, 27))
        self.load_profile.setObjectName("load_profile")
        self.default = QtGui.QCheckBox(Form)
        self.default.setGeometry(QtCore.QRect(220, 110, 131, 22))
        self.default.setObjectName("default")
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(210, 40, 181, 151))
        self.groupBox.setObjectName("groupBox")
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(10, 30, 161, 27))
        self.comboBox.setObjectName("comboBox")
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 40, 191, 151))
        self.groupBox_2.setObjectName("groupBox_2")
        self.toxygen = QtGui.QLabel(Form)
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.comboBox.raise_()
        self.default.raise_()
        self.load_profile.raise_()
        self.new_name.raise_()
        self.new_profile.raise_()
        self.toxygen.setGeometry(QtCore.QRect(160, 10, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Impact")
        font.setPointSize(16)
        self.toxygen.setFont(font)
        self.toxygen.setObjectName("toxygen")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Log in", None, QtGui.QApplication.UnicodeUTF8))
        self.new_profile.setText(QtGui.QApplication.translate("Form", "Create", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Profile name:", None, QtGui.QApplication.UnicodeUTF8))
        self.load_profile.setText(QtGui.QApplication.translate("Form", "Load profile", None, QtGui.QApplication.UnicodeUTF8))
        self.default.setText(QtGui.QApplication.translate("Form", "Use as default", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Load existing profile", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Create new profile", None, QtGui.QApplication.UnicodeUTF8))
        self.toxygen.setText(QtGui.QApplication.translate("Form", "toxygen", None, QtGui.QApplication.UnicodeUTF8))

    def update_select(self, data):
        list_of_profiles = []
        for elem in data:
            list_of_profiles.append(self.tr(elem))
        self.comboBox.addItems(list_of_profiles)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ls = LoginScreen()
    win = QtGui.QMainWindow()
    ls.setupUi(win)
    win.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()
