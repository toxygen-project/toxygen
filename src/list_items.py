from toxcore_enums_and_consts import *
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
import profile
from file_transfers import TOX_FILE_TRANSFER_STATE
from util import curr_directory, convert_time
from messages import FILE_TRANSFER_MESSAGE_STATUS
from widgets import DataLabel, create_menu
import cgi
import smileys


class MessageEdit(QtGui.QTextBrowser):

    def __init__(self, text, width, parent=None):
        super(MessageEdit, self).__init__(parent)
        self.urls = {}
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setTextWidth(width)
        self.setOpenExternalLinks(True)
        self.setAcceptRichText(True)
        self.setOpenLinks(False)
        self.setSearchPaths([smileys.SmileyLoader.get_instance().get_smileys_path()])
        self.setDecoratedText(text)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPixelSize(14)
        font.setBold(False)
        self.setFont(font)
        self.setFixedHeight(self.document().size().height())
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        self.anchorClicked.connect(self.on_anchor_clicked)

    def contextMenuEvent(self, event):
        menu = create_menu(self.createStandardContextMenu(event.pos()))
        menu.popup(event.globalPos())
        menu.exec_(event.globalPos())
        del menu

    def on_anchor_clicked(self, url):
        text = str(url.toString())
        if text.startswith('tox:'):
            import menu
            self.add_contact = menu.AddContact(text[4:])
            self.add_contact.show()
        else:
            QtGui.QDesktopServices.openUrl(url)
        self.clearFocus()

    def addAnimation(self, url, fileName):
        movie = QtGui.QMovie(self)
        movie.setFileName(fileName)
        self.urls[movie] = url
        movie.frameChanged[int].connect(lambda x: self.animate(movie))
        movie.start()

    def animate(self, movie):
        self.document().addResource(QtGui.QTextDocument.ImageResource,
                                    self.urls[movie],
                                    movie.currentPixmap())
        self.setLineWrapColumnOrWidth(self.lineWrapColumnOrWidth())

    def setDecoratedText(self, text):
        text = cgi.escape(text)  # replace < and >
        exp = QtCore.QRegExp(
            '('
            '(?:\\b)((www\\.)|(http[s]?|ftp)://)'
            '\\w+\\S+)'
            '|(?:\\b)(file:///)([\\S| ]*)'
            '|(?:\\b)(tox:[a-zA-Z\\d]{76}$)'
            '|(?:\\b)(mailto:\\S+@\\S+\\.\\S+)'
            '|(?:\\b)(tox:\\S+@\\S+)')
        offset = exp.indexIn(text, 0)
        while offset != -1:  # add links
            url = exp.cap()
            if exp.cap(2) == 'www.':
                html = '<a href="http://{0}">{0}</a>'.format(url)
            else:
                html = '<a href="{0}">{0}</a>'.format(url)
            text = text[:offset] + html + text[offset + len(exp.cap()):]
            offset += len(html)
            offset = exp.indexIn(text, offset)
        arr = text.split('\n')
        for i in range(len(arr)):  # quotes
            if arr[i].startswith('&gt;'):
                arr[i] = '<font color="green">' + arr[i][4:] + '</font>'
        text = '<br>'.join(arr)
        text = smileys.SmileyLoader.get_instance().add_smileys_to_text(text, self)  # smileys
        self.setHtml(text)


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

        if message_type != TOX_MESSAGE_TYPE['NORMAL']:
            self.name.setStyleSheet("QLabel { color: #4169E1; }")
            self.name.setAlignment(QtCore.Qt.AlignCenter)
            self.message.setStyleSheet("QTextEdit { color: #4169E1; }")
            self.message.setAlignment(QtCore.Qt.AlignCenter)
            self.time.setStyleSheet("QLabel { color: #4169E1; }")


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

    def __init__(self, file_name, size, time, user, friend_number, file_number, state, width, parent=None):

        QtGui.QListWidget.__init__(self, parent)
        self.resize(QtCore.QSize(width, 34))
        if state == FILE_TRANSFER_MESSAGE_STATUS['CANCELLED']:
            self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
        elif state in (FILE_TRANSFER_MESSAGE_STATUS['INCOMING_NOT_STARTED'], FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_FRIEND']):
            self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
        else:
            self.setStyleSheet('QListWidget { border: 1px solid green; }')

        self.state = state

        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(3, 7, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setText(user)

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(width - 53, 7, 50, 20))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setText(convert_time(time))

        self.cancel = QtGui.QPushButton(self)
        self.cancel.setGeometry(QtCore.QRect(width - 120, 2, 30, 30))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/decline.png')
        icon = QtGui.QIcon(pixmap)
        self.cancel.setIcon(icon)
        self.cancel.setIconSize(QtCore.QSize(30, 30))
        self.cancel.setVisible(state > 1)
        self.cancel.clicked.connect(lambda: self.cancel_transfer(friend_number, file_number))
        self.cancel.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; background-color: none;}')

        self.accept_or_pause = QtGui.QPushButton(self)
        self.accept_or_pause.setGeometry(QtCore.QRect(width - 170, 2, 30, 30))
        if state == FILE_TRANSFER_MESSAGE_STATUS['INCOMING_NOT_STARTED']:
            self.accept_or_pause.setVisible(True)
            self.button_update('accept')
        elif state in (0, 1, 5):
            self.accept_or_pause.setVisible(False)
        elif state == FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_USER']:  # setup for continue
            self.accept_or_pause.setVisible(True)
            self.button_update('resume')
        else:  # pause
            self.accept_or_pause.setVisible(True)
            self.button_update('pause')
        self.accept_or_pause.clicked.connect(lambda: self.accept_or_pause_transfer(friend_number, file_number, size))

        self.accept_or_pause.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; background-color: none}')

        self.pb = QtGui.QProgressBar(self)
        self.pb.setGeometry(QtCore.QRect(100, 7, 100, 20))
        self.pb.setValue(0)
        self.pb.setStyleSheet('QProgressBar { background-color: #302F2F; }')
        if state < 2:
            self.pb.setVisible(False)

        self.file_name = DataLabel(self)
        self.file_name.setGeometry(QtCore.QRect(210, 7, width - 400, 20))
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
        self.saved_name = file_name
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.paused = False

    def cancel_transfer(self, friend_number, file_number):
        pr = profile.Profile.get_instance()
        pr.cancel_transfer(friend_number, file_number)
        self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
        self.cancel.setVisible(False)
        self.accept_or_pause.setVisible(False)
        self.pb.setVisible(False)

    def accept_or_pause_transfer(self, friend_number, file_number, size):
        if self.state == FILE_TRANSFER_MESSAGE_STATUS['INCOMING_NOT_STARTED']:
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                               QtGui.QApplication.translate("MainWindow", 'Choose folder', None, QtGui.QApplication.UnicodeUTF8),
                                                               curr_directory(),
                                                               QtGui.QFileDialog.ShowDirsOnly)
            if directory:
                pr = profile.Profile.get_instance()
                pr.accept_transfer(self, directory + '/' + self.saved_name, friend_number, file_number, size)
                self.button_update('pause')
        elif self.state == FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_USER']:  # resume
            self.paused = False
            profile.Profile.get_instance().resume_transfer(friend_number, file_number)
            self.button_update('pause')
            self.state = FILE_TRANSFER_MESSAGE_STATUS['OUTGOING']
        else:  # pause
            self.paused = True
            self.state = FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_USER']
            profile.Profile.get_instance().pause_transfer(friend_number, file_number)
            self.button_update('resume')
        self.accept_or_pause.clearFocus()

    def button_update(self, path):
        pixmap = QtGui.QPixmap(curr_directory() + '/images/{}.png'.format(path))
        icon = QtGui.QIcon(pixmap)
        self.accept_or_pause.setIcon(icon)
        self.accept_or_pause.setIconSize(QtCore.QSize(30, 30))

    def convert(self, state):
        # convert TOX_FILE_TRANSFER_STATE to FILE_TRANSFER_MESSAGE_STATUS
        d = {0: 2, 1: 6, 2: 1, 3: 0, 4: 5}
        return d[state]

    @QtCore.Slot(int, float)
    def update(self, state, progress):
        self.pb.setValue(int(progress * 100))
        state = self.convert(state)
        if self.state != state:
            if state == FILE_TRANSFER_MESSAGE_STATUS['CANCELLED']:
                self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
                self.cancel.setVisible(False)
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.state = state
            elif state == FILE_TRANSFER_MESSAGE_STATUS['FINISHED']:
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.cancel.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
            elif state == FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_FRIEND']:
                self.accept_or_pause.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
                self.state = state
            elif state == FILE_TRANSFER_MESSAGE_STATUS['PAUSED_BY_USER']:
                self.button_update('resume')  # setup button continue
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
            elif not self.paused:  # active
                self.accept_or_pause.setVisible(True)  # setup to pause
                self.button_update('pause')
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state


class InlineImageItem(QtGui.QWidget):

    def __init__(self, data, width, parent=None):

        QtGui.QWidget.__init__(self, parent)
        self.resize(QtCore.QSize(width, 500))
        self._image_label = QtGui.QLabel(self)
        self._image_label.raise_()
        self._image_label.setAutoFillBackground(True)
        self._image_label.setScaledContents(False)
        self.pixmap = QtGui.QPixmap()
        self.pixmap.loadFromData(QtCore.QByteArray(data), "PNG")
        max_size = width - 40
        if self.pixmap.width() <= max_size:
            self._image_label.setPixmap(self.pixmap)
            self.resize(QtCore.QSize(max_size, self.pixmap.height()))
        else:
            pixmap = self.pixmap.scaled(max_size, max_size, QtCore.Qt.KeepAspectRatio)
            self._image_label.setPixmap(pixmap)
            self.resize(QtCore.QSize(max_size, pixmap.height()))




