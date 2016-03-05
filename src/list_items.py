from toxcore_enums_and_consts import *
from PySide import QtGui, QtCore
# TODO: remove some hardcoded values


class MessageEdit(QtGui.QPlainTextEdit):
    def __init__(self, text, width, parent=None):
        super(MessageEdit, self).__init__(parent)

        self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.setPlainText(text)
        self.document().setTextWidth(parent.width() - 100)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPixelSize(12)
        font.setBold(False)
        self.setFont(font)
        lines = 0
        fm = QtGui.QFontMetrics(font)
        try:
            for elem in xrange(self.document().blockCount()):
                block = self.document().findBlockByLineNumber(elem)
                l = block.length()
                line_width = fm.width(block.text())
                print 'Width: ', line_width
                print 'Parent width', parent.width()
                lines += line_width // width + 1
        except:
            print 'updateSize failed'
        print 'lines ', lines
        if self.document().blockCount() == 1:
            lines += 1
        self.setFixedHeight(max(lines * 15, 30))
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)


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
        self.time.setGeometry(QtCore.QRect(450, 0, 50, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setObjectName("time")
        self.time.setText(time)

        self.message = MessageEdit(text, parent.width() - 100, self)
        self.message.setGeometry(QtCore.QRect(50, 0, parent.width() - 100, self.message.height()))
        self.h = self.message.height()
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
    # TODO: rewrite with showing unread messages
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
