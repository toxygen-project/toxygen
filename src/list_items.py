from toxcore_enums_and_consts import *
from PySide import QtGui, QtCore


class MessageItem(QtGui.QListWidget):
    """
    Message in messages list
    """
    def __init__(self, text, time, user='', message_type=TOX_MESSAGE_TYPE['NORMAL'], parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(0, 0, 50, 25))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.name.setText(user)

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(450, 0, 50, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setObjectName("time")
        self.time.setText(time)

        self.message = QtGui.QPlainTextEdit(self)
        self.message.setGeometry(QtCore.QRect(50, 0, 400, 50))
        self.message.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        self.message.setPlainText(text)

        if message_type == TOX_MESSAGE_TYPE['ACTION']:
            self.name.setStyleSheet("QLabel { color: blue; }")
            self.message.setStyleSheet("QPlainTextEdit { color: blue; }")


class ContactItem(QtGui.QListWidget):
    """
    Contact in friends list
    """
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        # self.setMinimumSize(QtCore.QSize(250, 50))
        # self.setMaximumSize(QtCore.QSize(250, 50))
        self.setBaseSize(QtCore.QSize(250, 50))
        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(80, 10, 191, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.status_message = QtGui.QLabel(self)
        self.status_message.setGeometry(QtCore.QRect(80, 30, 191, 17))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        self.status_message.setFont(font)
        self.status_message.setObjectName("status_message")
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(200, 5, 16, 16))
        self.connection_status.setMinimumSize(QtCore.QSize(32, 32))
        self.connection_status.setMaximumSize(QtCore.QSize(32, 32))
        self.connection_status.setBaseSize(QtCore.QSize(32, 32))
        self.connection_status.setObjectName("connection_status")


class StatusCircle(QtGui.QWidget):
    """
    Connection status
    """

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(0, 0, 32, 32)
        self.data = None

    def mouseReleaseEvent(self, event):
        pass

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        k = 16
        rad_x = rad_y = 5
        if self.data is None:
            color = QtCore.Qt.transparent
        else:
            if self.data == TOX_USER_STATUS['NONE']:
                color = QtCore.Qt.darkGreen
            elif self.data == TOX_USER_STATUS['AWAY']:
                color = QtCore.Qt.yellow
            else:  # self.data == TOX_USER_STATUS['BUSY']:
                color = QtCore.Qt.darkRed

        paint.setPen(color)
        center = QtCore.QPoint(k, k)
        paint.setBrush(color)
        paint.drawEllipse(center, rad_x, rad_y)
        paint.end()