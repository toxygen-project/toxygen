from toxcore_enums_and_consts import *
from PySide import QtGui, QtCore
import profile
from file_transfers import TOX_FILE_TRANSFER_STATE
from util import curr_directory


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
                lines += line_width / float(width) + 1
        except:
            print 'updateSize failed'
        print 'lines ', lines
        size = int(lines + 0.5) * 21
        self.setFixedHeight(max(size, 25))
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)


class MessageItem(QtGui.QWidget):
    """
    Message in messages list
    """
    def __init__(self, text, time, user='', message_type=TOX_MESSAGE_TYPE['NORMAL'], parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(0, 2, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.name.setText(user if len(user) <= 14 else user[:11] + '...')

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

        if message_type == TOX_MESSAGE_TYPE['ACTION']:
            self.name.setStyleSheet("QLabel { color: #4169E1; }")
            self.message.setStyleSheet("QPlainTextEdit { color: #4169E1; }")
        else:
            if text[0] == '>':
                self.message.setStyleSheet("QPlainTextEdit { color: green; }")
            if text[-1] == '<':
                self.message.setStyleSheet("QPlainTextEdit { color: red; }")

    def getHeight(self):
        return max(self.h, 25)


class ContactItem(QtGui.QWidget):
    """
    Contact in friends list
    """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
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


class FileTransferItem(QtGui.QWidget):

    def __init__(self, file_name, size, time, user, friend_number, file_number, show_accept, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.resize(QtCore.QSize(600, 50))
        self.setStyleSheet('QWidget { background-color: green; }')

        self.name = QtGui.QLabel(self)
        self.name.setGeometry(QtCore.QRect(0, 15, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.name.setText(user if len(user) <= 14 else user[:11] + '...')
        self.name.setStyleSheet('QLabel { color: black; }')

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(550, 0, 50, 50))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setObjectName("time")
        self.time.setText(time)
        self.time.setStyleSheet('QLabel { color: black; }')

        self.cancel = QtGui.QPushButton(self)
        self.cancel.setGeometry(QtCore.QRect(500, 0, 50, 50))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/decline.png')
        icon = QtGui.QIcon(pixmap)
        self.cancel.setIcon(icon)
        self.cancel.setIconSize(QtCore.QSize(30, 30))
        self.cancel.clicked.connect(lambda: self.cancel_transfer(friend_number, file_number))

        self.accept = QtGui.QPushButton(self)
        self.accept.setGeometry(QtCore.QRect(450, 0, 50, 50))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/accept.png')
        icon = QtGui.QIcon(pixmap)
        self.accept.setIcon(icon)
        self.accept.setIconSize(QtCore.QSize(30, 30))
        self.accept.clicked.connect(lambda: self.accept_transfer(friend_number, file_number, size))
        self.accept.setVisible(show_accept)

        self.pb = QtGui.QProgressBar(self)
        self.pb.setGeometry(QtCore.QRect(100, 15, 100, 20))
        self.pb.setValue(0)

        self.file_name = QtGui.QLabel(self)
        self.file_name.setGeometry(QtCore.QRect(210, 0, 230, 50))
        font.setPointSize(12)
        self.file_name.setFont(font)
        self.file_name.setObjectName("time")
        file_size = size / 1024
        if not file_size:
            file_size = '<1KB'
        elif file_size >= 1024:
            file_size = '{}MB'.format(file_size / 1024)
        else:
            file_size = '{}KB'.format(file_size)
        file_data = u'{} {}'.format(file_size, file_name)
        self.file_name.setText(file_data if len(file_data) <= 27 else file_data[:24] + '...')
        self.file_name.setStyleSheet('QLabel { color: black; }')
        self.saved_name = file_name

    def cancel_transfer(self, friend_number, file_number):
        pr = profile.Profile.get_instance()
        pr.cancel_transfer(friend_number, file_number)
        self.setStyleSheet('QListWidget { background-color: #B40404; }')
        self.cancel.setVisible(False)
        self.accept.setVisible(False)
        self.pb.setVisible(False)

    def accept_transfer(self, friend_number, file_number, size):
        directory = QtGui.QFileDialog.getExistingDirectory()
        if directory:
            pr = profile.Profile.get_instance()
            pr.accept_transfer(self, directory + '/' + self.saved_name, friend_number, file_number, size)
            self.accept.setVisible(False)

    @QtCore.Slot(int, float)
    def update(self, state, progress):
        self.pb.setValue(int(progress * 100))
        if state == TOX_FILE_TRANSFER_STATE['CANCELED']:
            self.setStyleSheet('QListWidget { background-color: #B40404; }')
            self.cancel.setVisible(False)
            self.accept.setVisible(False)
            self.pb.setVisible(False)
        elif state == TOX_FILE_TRANSFER_STATE['FINISHED']:
            self.pb.setVisible(False)
            self.cancel.setVisible(False)

