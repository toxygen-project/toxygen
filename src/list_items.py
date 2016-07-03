from toxcore_enums_and_consts import *
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
import profile
from file_transfers import TOX_FILE_TRANSFER_STATE, PAUSED_FILE_TRANSFERS, DO_NOT_SHOW_ACCEPT_BUTTON, ACTIVE_FILE_TRANSFERS, SHOW_PROGRESS_BAR
from util import curr_directory, convert_time, curr_time
from widgets import DataLabel, create_menu
import html as h
import smileys
import settings


class MessageEdit(QtGui.QTextBrowser):

    def __init__(self, text, width, message_type, parent=None):
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
        self.document().setDefaultStyleSheet('a { color: #306EFF; }')
        text = self.decoratedText(text)
        if message_type != TOX_MESSAGE_TYPE['NORMAL']:
            self.setHtml('<p style="color: #5CB3FF; font: italic; font-size: 20px;" >' + text + '</p>')
        else:
            self.setHtml(text)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPixelSize(settings.Settings.get_instance()['message_font_size'])
        font.setBold(False)
        self.setFont(font)
        self.resize(width, self.document().size().height())
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

    def decoratedText(self, text):
        text = h.escape(text)  # replace < and >
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
                arr[i] = '<font color="green"><b>' + arr[i][4:] + '</b></font>'
        text = '<br>'.join(arr)
        text = smileys.SmileyLoader.get_instance().add_smileys_to_text(text, self)  # smileys
        return text


class MessageItem(QtGui.QWidget):
    """
    Message in messages list
    """
    def __init__(self, text, time, user='', sent=True, message_type=TOX_MESSAGE_TYPE['NORMAL'], parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(2, 2, 95, 20))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setText(user)

        self.time = QtGui.QLabel(self)
        self.time.setGeometry(QtCore.QRect(parent.width() - 50, 0, 50, 20))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self._time = time
        if not sent:
            movie = QtGui.QMovie(curr_directory() + '/images/spinner.gif')
            self.time.setMovie(movie)
            movie.start()
            self.t = True
        else:
            self.time.setText(convert_time(time))
            self.t = False

        self.message = MessageEdit(text, parent.width() - 150, message_type, self)
        if message_type != TOX_MESSAGE_TYPE['NORMAL']:
            self.name.setStyleSheet("QLabel { color: #5CB3FF; }")
            self.message.setAlignment(QtCore.Qt.AlignCenter)
            self.time.setStyleSheet("QLabel { color: #5CB3FF; }")
        self.message.setGeometry(QtCore.QRect(100, 0, parent.width() - 150, self.message.height()))
        self.setFixedHeight(self.message.height())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and event.x() > self.time.x():
            self.listMenu = QtGui.QMenu()
            delete_item = self.listMenu.addAction(QtGui.QApplication.translate("MainWindow", 'Delete message', None, QtGui.QApplication.UnicodeUTF8))
            self.connect(delete_item, QtCore.SIGNAL("triggered()"), self.delete)
            parent_position = self.time.mapToGlobal(QtCore.QPoint(0, 0))
            self.listMenu.move(parent_position)
            self.listMenu.show()

    def delete(self):
        pr = profile.Profile.get_instance()
        pr.delete_message(self._time)

    def mark_as_sent(self):
        if self.t:
            self.time.setText(convert_time(self._time))
            self.t = False
            return True
        return False


class ContactItem(QtGui.QWidget):
    """
    Contact in friends list
    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        mode = settings.Settings.get_instance()['compact_mode']
        self.setBaseSize(QtCore.QSize(250, 40 if mode else 70))
        self.avatar_label = QtGui.QLabel(self)
        size = 32 if mode else 64
        self.avatar_label.setGeometry(QtCore.QRect(3, 4, size, size))
        self.avatar_label.setScaledContents(True)
        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(50 if mode else 75, 3 if mode else 10, 150, 15 if mode else 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10 if mode else 12)
        font.setBold(True)
        self.name.setFont(font)
        self.status_message = DataLabel(self)
        self.status_message.setGeometry(QtCore.QRect(50 if mode else 75, 20 if mode else 30, 170, 15 if mode else 20))
        font.setPointSize(10)
        font.setBold(False)
        self.status_message.setFont(font)
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(230, -2 if mode else 5, 32, 32))
        self.messages = UnreadMessagesCount(self)
        self.messages.setGeometry(QtCore.QRect(20 if mode else 52, 20 if mode else 50, 30, 20))


class StatusCircle(QtGui.QWidget):
    """
    Connection status
    """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(0, 0, 32, 32)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 32, 32))
        self.unread = False

    def update(self, status, unread_messages=None):
        if unread_messages is None:
            unread_messages = self.unread
        else:
            self.unread = unread_messages
        if status == TOX_USER_STATUS['NONE']:
            name = 'online'
        elif status == TOX_USER_STATUS['AWAY']:
            name = 'idle'
        elif status == TOX_USER_STATUS['BUSY']:
            name = 'busy'
        else:
            name = 'offline'
        if unread_messages:
            name += '_notification'
            self.label.setGeometry(QtCore.QRect(0, 0, 32, 32))
        else:
            self.label.setGeometry(QtCore.QRect(2, 0, 32, 32))
        pixmap = QtGui.QPixmap(curr_directory() + '/images/{}.png'.format(name))
        self.label.setPixmap(pixmap)


class UnreadMessagesCount(QtGui.QWidget):

    def __init__(self, parent=None):
        super(UnreadMessagesCount, self).__init__(parent)
        self.resize(30, 20)
        self.label = QtGui.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 30, 20))
        self.label.setVisible(False)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        color = settings.Settings.get_instance()['unread_color']
        self.label.setStyleSheet('QLabel { color: white; background-color: ' + color + '; border-radius: 10; }')

    def update(self, messages_count):
        color = settings.Settings.get_instance()['unread_color']
        self.label.setStyleSheet('QLabel { color: white; background-color: ' + color + '; border-radius: 10; }')
        if messages_count:
            self.label.setVisible(True)
            self.label.setText(str(messages_count))
        else:
            self.label.setVisible(False)


class FileTransferItem(QtGui.QListWidget):

    def __init__(self, file_name, size, time, user, friend_number, file_number, state, width, parent=None):

        QtGui.QListWidget.__init__(self, parent)
        self.resize(QtCore.QSize(width, 34))
        if state == TOX_FILE_TRANSFER_STATE['CANCELLED']:
            self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
        elif state in PAUSED_FILE_TRANSFERS:
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
        self.cancel.setVisible(state in ACTIVE_FILE_TRANSFERS)
        self.cancel.clicked.connect(lambda: self.cancel_transfer(friend_number, file_number))
        self.cancel.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; background-color: none;}')

        self.accept_or_pause = QtGui.QPushButton(self)
        self.accept_or_pause.setGeometry(QtCore.QRect(width - 170, 2, 30, 30))
        if state == TOX_FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
            self.accept_or_pause.setVisible(True)
            self.button_update('accept')
        elif state in DO_NOT_SHOW_ACCEPT_BUTTON:
            self.accept_or_pause.setVisible(False)
        elif state == TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']:  # setup for continue
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
        self.pb.setVisible(state in SHOW_PROGRESS_BAR)

        self.file_name = DataLabel(self)
        self.file_name.setGeometry(QtCore.QRect(210, 7, width - 420, 20))
        font.setPointSize(12)
        self.file_name.setFont(font)
        file_size = size // 1024
        if not file_size:
            file_size = '{}B'.format(size)
        elif file_size >= 1024:
            file_size = '{}MB'.format(file_size // 1024)
        else:
            file_size = '{}KB'.format(file_size)
        file_data = '{} {}'.format(file_size, file_name)
        self.file_name.setText(file_data)
        self.file_name.setToolTip(file_name)
        self.saved_name = file_name
        self.time_left = QtGui.QLabel(self)
        self.time_left.setGeometry(QtCore.QRect(width - 87, 7, 30, 20))
        font.setPointSize(10)
        self.time_left.setFont(font)
        self.time_left.setVisible(state == TOX_FILE_TRANSFER_STATE['RUNNING'])
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
        if self.state == TOX_FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                               QtGui.QApplication.translate("MainWindow", 'Choose folder', None, QtGui.QApplication.UnicodeUTF8),
                                                               curr_directory(),
                                                               QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)
            self.pb.setVisible(True)
            if directory:
                pr = profile.Profile.get_instance()
                pr.accept_transfer(self, directory + '/' + self.saved_name, friend_number, file_number, size)
                self.button_update('pause')
        elif self.state == TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']:  # resume
            self.paused = False
            profile.Profile.get_instance().resume_transfer(friend_number, file_number)
            self.button_update('pause')
            self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        else:  # pause
            self.paused = True
            self.state = TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']
            profile.Profile.get_instance().pause_transfer(friend_number, file_number)
            self.button_update('resume')
        self.accept_or_pause.clearFocus()

    def button_update(self, path):
        pixmap = QtGui.QPixmap(curr_directory() + '/images/{}.png'.format(path))
        icon = QtGui.QIcon(pixmap)
        self.accept_or_pause.setIcon(icon)
        self.accept_or_pause.setIconSize(QtCore.QSize(30, 30))

    @QtCore.Slot(int, float, int)
    def update(self, state, progress, time):
        self.pb.setValue(int(progress * 100))
        if time + 1:
            m, s = divmod(time, 60)
            self.time_left.setText('{0:02d}:{1:02d}'.format(m, s))
        if self.state != state:
            if state == TOX_FILE_TRANSFER_STATE['CANCELLED']:
                self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
                self.cancel.setVisible(False)
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.state = state
                self.time_left.setVisible(False)
            elif state == TOX_FILE_TRANSFER_STATE['FINISHED']:
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.cancel.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == TOX_FILE_TRANSFER_STATE['PAUSED_BY_FRIEND']:
                self.accept_or_pause.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']:
                self.button_update('resume')  # setup button continue
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED']:
                self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
                self.accept_or_pause.setVisible(False)
                self.time_left.setVisible(False)
                self.pb.setVisible(False)
            elif not self.paused:  # active
                self.pb.setVisible(True)
                self.accept_or_pause.setVisible(True)  # setup to pause
                self.button_update('pause')
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
                self.time_left.setVisible(True)

    def mark_as_sent(self):
        return False


class UnsentFileItem(FileTransferItem):

    def __init__(self, file_name, size, user, time, width, parent=None):
        super(UnsentFileItem, self).__init__(file_name, size, time, user, -1, -1,
                                             TOX_FILE_TRANSFER_STATE['PAUSED_BY_FRIEND'], width, parent)
        self._time = time
        self.pb.setVisible(False)
        movie = QtGui.QMovie(curr_directory() + '/images/spinner.gif')
        self.time.setMovie(movie)
        movie.start()

    def cancel_transfer(self, *args):
        pr = profile.Profile.get_instance()
        pr.cancel_not_started_transfer(self._time)


class InlineImageItem(QtGui.QScrollArea):

    def __init__(self, data, width, elem):

        QtGui.QScrollArea.__init__(self)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self._elem = elem
        self._image_label = QtGui.QLabel(self)
        self._image_label.raise_()
        self.setWidget(self._image_label)
        self._image_label.setScaledContents(False)
        self._pixmap = QtGui.QPixmap()
        self._pixmap.loadFromData(data, 'PNG')
        self._max_size = width - 30
        self._resize_needed = not (self._pixmap.width() <= self._max_size)
        self._full_size = not self._resize_needed
        if not self._resize_needed:
            self._image_label.setPixmap(self._pixmap)
            self.resize(QtCore.QSize(self._max_size + 5, self._pixmap.height() + 5))
            self._image_label.setGeometry(5, 0, self._pixmap.width(), self._pixmap.height())
        else:
            pixmap = self._pixmap.scaled(self._max_size, self._max_size, QtCore.Qt.KeepAspectRatio)
            self._image_label.setPixmap(pixmap)
            self.resize(QtCore.QSize(self._max_size + 5, pixmap.height()))
            self._image_label.setGeometry(5, 0, self._max_size + 5, pixmap.height())
        self._elem.setSizeHint(QtCore.QSize(self.width(), self.height()))

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self._resize_needed:  # scale inline
            if self._full_size:
                pixmap = self._pixmap.scaled(self._max_size, self._max_size, QtCore.Qt.KeepAspectRatio)
                self._image_label.setPixmap(pixmap)
                self.resize(QtCore.QSize(self._max_size, pixmap.height()))
                self._image_label.setGeometry(5, 0, pixmap.width(), pixmap.height())
            else:
                self._image_label.setPixmap(self._pixmap)
                self.resize(QtCore.QSize(self._max_size, self._pixmap.height() + 17))
                self._image_label.setGeometry(5, 0, self._pixmap.width(), self._pixmap.height())
            self._full_size = not self._full_size
            self._elem.setSizeHint(QtCore.QSize(self.width(), self.height()))
        elif event.button() == QtCore.Qt.RightButton:  # save inline
            directory = QtGui.QFileDialog.getExistingDirectory(self,
                                                               QtGui.QApplication.translate("MainWindow",
                                                                                            'Choose folder', None,
                                                                                            QtGui.QApplication.UnicodeUTF8),
                                                               curr_directory(),
                                                               QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontUseNativeDialog)
            if directory:
                fl = QtCore.QFile(directory + '/toxygen_inline_' + curr_time().replace(':', '_') + '.png')
                self._pixmap.save(fl, 'PNG')

        return False

    def mark_as_sent(self):
        return False




