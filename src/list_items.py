from toxcore_enums_and_consts import *
from PySide import QtGui, QtCore


class MessageEdit(QtGui.QPlainTextEdit):
    def __init__(self, text, width, parent=None):
        super(MessageEdit, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setPlainText(text)
        self.document().setTextWidth(parent.width() - 100)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPixelSize(14)
        font.setBold(False)
        self.setFont(font)
        lines = 0
        fm = QtGui.QFontMetrics(font)
        try:
            for elem in xrange(self.document().blockCount()):
                block = self.document().findBlockByLineNumber(elem)
                line_width = fm.width(block.text())
                print 'Width: ', line_width
                print 'Parent width', parent.width()
                lines += line_width // width + 1
        except:
            print 'updateSize failed'
        print 'lines ', lines
        if self.document().blockCount() == 1:
            lines += 1
        size = lines * 21
        self.setFixedHeight(max(size, 30))
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)


class MessageItem(QtGui.QListWidget):
    """
    Message in messages list
    """
    def __init__(self, text, time, user='', message_type=TOX_MESSAGE_TYPE['NORMAL'], parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(0, 0, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.name.setText(user)

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(parent.width() - 50, 0, 50, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setObjectName("time")
        self.time.setText(time)

        self.message = MessageEdit(text, parent.width() - 150, self)
        self.message.setGeometry(QtCore.QRect(100, 0, parent.width() - 150, self.message.height()))
        self.h = self.message.height()
        print 'self.h ', self.h
        self.setFixedHeight(self.getHeight())

        self.message.setFrameShape(QtGui.QFrame.NoFrame)
        self.time.setFrameShape(QtGui.QFrame.NoFrame)
        self.name.setFrameShape(QtGui.QFrame.NoFrame)
        self.setFrameShape(QtGui.QFrame.NoFrame)

        if message_type == TOX_MESSAGE_TYPE['ACTION']:
            self.name.setStyleSheet("QLabel { color: blue; }")
            self.message.setStyleSheet("QPlainTextEdit { color: blue; }")
        else:
            if text[0] == '>':
                self.message.setStyleSheet("QPlainTextEdit { color: green; }")
            if text[-1] == '<':
                self.message.setStyleSheet("QPlainTextEdit { color: red; }")

    def getHeight(self):
        return max(self.h, 30)


class ContactItem(QtGui.QListWidget):
    """
    Contact in friends list
    """
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.setBaseSize(QtCore.QSize(250, 70))
        self.avatar_label = QtGui.QLabel(self)
        self.avatar_label.setGeometry(QtCore.QRect(3, 3, 64, 64))
        self.avatar_label.setScaledContents(True)
        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(70, 10, 170, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.status_message = QtGui.QLabel(self)
        self.status_message.setGeometry(QtCore.QRect(70, 30, 180, 20))
        font.setPointSize(10)
        font.setBold(False)
        self.status_message.setFont(font)
        self.status_message.setObjectName("status_message")
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(218, 5, 32, 32))
        # self.connection_status.setMinimumSize(QtCore.QSize(32, 32))
        # self.connection_status.setMaximumSize(QtCore.QSize(32, 32))
        # self.connection_status.setBaseSize(QtCore.QSize(32, 32))
        self.connection_status.setObjectName("connection_status")


class StatusCircle(QtGui.QWidget):
    """
    Connection status
    """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(0, 0, 32, 32)
        self.data = None
        self.messages = False

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
                color = QtGui.QColor(50, 205, 50)
            elif self.data == TOX_USER_STATUS['AWAY']:
                color = QtGui.QColor(255, 200, 50)
            else:  # self.data == TOX_USER_STATUS['BUSY']:
                color = QtGui.QColor(255, 50, 0)

        paint.setPen(color)
        center = QtCore.QPoint(k, k)
        paint.setBrush(color)
        paint.drawEllipse(center, rad_x, rad_y)
        if self.messages:
            if color == QtCore.Qt.transparent:
                color = QtCore.Qt.darkRed
            paint.setBrush(QtCore.Qt.transparent)
            paint.setPen(color)
            paint.drawEllipse(center, rad_x + 3, rad_y + 3)
        paint.end()
