from PySide import QtCore, QtGui


class AddContact(QtGui.QWidget):
    """Add contact form """

    def __init__(self):
        super(AddContact, self).__init__()
        self.initUI()

    def initUI(self):
        self.setObjectName('AddContact')
        self.resize(568, 306)
        self.sendRequestButton = QtGui.QPushButton(self)
        self.sendRequestButton.setGeometry(QtCore.QRect(50, 270, 471, 31))
        self.sendRequestButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setBaseSize(QtCore.QSize(0, 0))
        self.sendRequestButton.setObjectName("sendRequestButton")
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(50, 40, 471, 27))
        self.lineEdit.setObjectName("lineEdit")
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(70, 10, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.textEdit = QtGui.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(50, 110, 471, 151))
        self.textEdit.setObjectName("textEdit")
        self.label_2 = QtGui.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(60, 70, 101, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate('AddContact', "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.sendRequestButton.setText(QtGui.QApplication.translate("Form", "Send request", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate('AddContact', "TOX ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate('AddContact', "Message:", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ex = AddContact()
    ex.show()
    app.connect(app, QtCore.SIGNAL("lastWindowClosed()"), app, QtCore.SLOT("quit()"))
    app.exec_()
