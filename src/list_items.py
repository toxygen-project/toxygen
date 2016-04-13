from toxcore_enums_and_consts import *
from PySide import QtGui, QtCore
import profile
from file_transfers import TOX_FILE_TRANSFER_STATE
from util import curr_directory, convert_time
from messages import FILE_TRANSFER_MESSAGE_STATUS


class MessageEdit(QtGui.QTextEdit):

    def __init__(self, text, width, parent=None):
        super(MessageEdit, self).__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setTextWidth(width)
        self.setPlainText(text)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPixelSize(14)
        font.setBold(False)
        self.setFont(font)
        self.setFixedHeight(self.document().size().height())
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)


class MessageItem(QtGui.QWidget):
    """
    Message in messages list
    """
    def __init__(self, text, time, user='', message_type=TOX_MESSAGE_TYPE['NORMAL'], parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(0, 2, 95, 20))
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
        self.setFixedHeight(self.message.height())

        if message_type == TOX_MESSAGE_TYPE['ACTION']:
            self.name.setStyleSheet("QLabel { color: #4169E1; }")
            self.message.setStyleSheet("QTextEdit { color: #4169E1; }")
        else:
            if text[0] == '>':
                self.message.setStyleSheet("QTextEdit { color: green; }")
            if text[-1] == '<':
                self.message.setStyleSheet("QTextEdit { color: red; }")


class DataLabel(QtGui.QLabel):

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        text = metrics.elidedText(self.text(), QtCore.Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), text)


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
        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(70, 10, 160, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.status_message = DataLabel(self)
        self.status_message.setGeometry(QtCore.QRect(70, 30, 180, 20))
        font.setPointSize(10)
        font.setBold(False)
        self.status_message.setFont(font)
        self.status_message.setObjectName("status_message")
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(220, 5, 32, 32))
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


class FileTransferItem(QtGui.QListWidget):

    def __init__(self, file_name, size, time, user, friend_number, file_number, state, parent=None):

        QtGui.QListWidget.__init__(self, parent)
        self.resize(QtCore.QSize(620, 50))
        if state != FILE_TRANSFER_MESSAGE_STATUS['CANCELLED']:
            self.setStyleSheet('QWidget { background-color: green; }')
        else:
            self.setStyleSheet('QWidget { background-color: #B40404; }')

        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(1, 15, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setText(user)
        self.name.setStyleSheet('QLabel { color: black; }')

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(570, 2, 50, 46))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setText(convert_time(time))
        self.time.setStyleSheet('QLabel { color: black; }')

        self.cancel = QtGui.QPushButton(self)
        self.cancel.setGeometry(QtCore.QRect(500, 2, 46, 46))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/decline.png')
        icon = QtGui.QIcon(pixmap)
        self.cancel.setIcon(icon)
        self.cancel.setIconSize(QtCore.QSize(30, 30))
        self.cancel.setVisible(state > 1)
        self.cancel.clicked.connect(lambda: self.cancel_transfer(friend_number, file_number))
        self.cancel.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; }')

        self.accept = QtGui.QPushButton(self)
        self.accept.setGeometry(QtCore.QRect(450, 2, 46, 46))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/accept.png')
        icon = QtGui.QIcon(pixmap)
        self.accept.setIcon(icon)
        self.accept.setIconSize(QtCore.QSize(30, 30))
        self.accept.clicked.connect(lambda: self.accept_transfer(friend_number, file_number, size))
        self.accept.setVisible(state == FILE_TRANSFER_MESSAGE_STATUS['INCOMING_NOT_STARTED'])
        self.accept.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; }')

        self.pb = QtGui.QProgressBar(self)
        self.pb.setGeometry(QtCore.QRect(100, 15, 100, 20))
        self.pb.setValue(0)
        self.pb.setStyleSheet('QProgressBar { background-color: #302F2F; }')
        if state < 2:
            self.pb.setVisible(False)

        self.file_name = DataLabel(self)
        self.file_name.setGeometry(QtCore.QRect(210, 2, 230, 46))
        font.setPointSize(12)
        self.file_name.setFont(font)
        file_size = size / 1024
        if not file_size:
            file_size = '{}B'.format(size)
        elif file_size >= 1024:
            file_size = '{}MB'.format(file_size / 1024)
        else:
            file_size = '{}KB'.format(file_size)
        file_data = u'{} {}'.format(file_size, file_name)
        self.file_name.setText(file_data)
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


class InlineImageItem(QtGui.QWidget):

    def __init__(self, data, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.resize(QtCore.QSize(620, 500))
        self._image_label = QtGui.QLabel(self)
        self._image_label.raise_()
        self._image_label.setAutoFillBackground(True)
        self._image_label.setScaledContents(False)
        self.pixmap = QtGui.QPixmap()
        self.pixmap.loadFromData(QtCore.QByteArray(data), "PNG")
        if self.pixmap.width() <= 600:
            self._image_label.setPixmap(self.pixmap)
            self.resize(QtCore.QSize(600, self.pixmap.height()))
        else:
            pixmap = self.pixmap.scaled(600, 600, QtCore.Qt.KeepAspectRatio)
            self._image_label.setPixmap(pixmap)
            self.resize(QtCore.QSize(600, pixmap.height()))




