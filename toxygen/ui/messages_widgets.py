from wrapper.toxcore_enums_and_consts import *
import ui.widgets as widgets
import utils.util as util
import ui.menu as menu
import html as h
import re
from ui.widgets import *
from messenger.messages import MESSAGE_AUTHOR
from file_transfers.file_transfers import *


class MessageBrowser(QtWidgets.QTextBrowser):

    def __init__(self, settings, message_edit, smileys_loader, plugin_loader, text, width, message_type, parent=None):
        super().__init__(parent)
        self.urls = {}
        self._message_edit = message_edit
        self._smileys_loader = smileys_loader
        self._plugin_loader = plugin_loader
        self._add_contact = None
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setTextWidth(width)
        self.setOpenExternalLinks(True)
        self.setAcceptRichText(True)
        self.setOpenLinks(False)
        path = smileys_loader.get_smileys_path()
        if path is not None:
            self.setSearchPaths([path])
        self.document().setDefaultStyleSheet('a { color: #306EFF; }')
        text = self.decoratedText(text)
        if message_type != TOX_MESSAGE_TYPE['NORMAL']:
            self.setHtml('<p style="color: #5CB3FF; font: italic; font-size: 20px;" >' + text + '</p>')
        else:
            self.setHtml(text)
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPixelSize(settings['message_font_size'])
        font.setBold(False)
        self.setFont(font)
        self.resize(width, self.document().size().height())
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.LinksAccessibleByMouse)
        self.anchorClicked.connect(self.on_anchor_clicked)

    def contextMenuEvent(self, event):
        menu = widgets.create_menu(self.createStandardContextMenu(event.pos()))
        quote = menu.addAction(util_ui.tr('Quote selected text'))
        quote.triggered.connect(self.quote_text)
        text = self.textCursor().selection().toPlainText()
        if not text:
            quote.setEnabled(False)
        else:
            sub_menu = self._plugin_loader.get_message_menu(menu, text)
            if len(sub_menu):
                plugins_menu = menu.addMenu(util_ui.tr('Plugins'))
                plugins_menu.addActions(sub_menu)
        menu.popup(event.globalPos())
        menu.exec_(event.globalPos())
        del menu

    def quote_text(self):
        text = self.textCursor().selection().toPlainText()
        if not text:
            return
        text = '>' + '\n>'.join(text.split('\n'))
        if self._message_edit.toPlainText():
            text = '\n' + text
        self._message_edit.appendPlainText(text)

    def on_anchor_clicked(self, url):
        text = str(url.toString())
        if text.startswith('tox:'):
            self._add_contact = menu.AddContact(text[4:])
            self._add_contact.show()
        else:
            QtGui.QDesktopServices.openUrl(url)
        self.clearFocus()

    def addAnimation(self, url, file_name):
        movie = QtGui.QMovie(self)
        movie.setFileName(file_name)
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
        text = self._smileys_loader.add_smileys_to_text(text, self)
        return text


class MessageItem(QtWidgets.QWidget):
    """
    Message in messages list
    """
    def __init__(self, text_message, settings, message_browser_factory_method, delete_action, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._message = text_message
        self._delete_action = delete_action
        self.name = widgets.DataLabel(self)
        self.name.setGeometry(QtCore.QRect(2, 2, 95, 23))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPointSize(11)
        font.setBold(True)
        if text_message.author is not None:
            self.name.setFont(font)
            self.name.setText(text_message.author.name)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(QtCore.QRect(parent.width() - 60, 0, 50, 25))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self._time = text_message.time
        if text_message.author and text_message.author.type == MESSAGE_AUTHOR['NOT_SENT']:
            movie = QtGui.QMovie(util.join_path(util.get_images_directory(), 'spinner.gif'))
            self.time.setMovie(movie)
            movie.start()
            self.t = True
        else:
            self.time.setText(util.convert_time(text_message.time))
            self.t = False

        self.message = message_browser_factory_method(text_message.text, parent.width() - 160,
                                                      text_message.type, self)
        if text_message.type != TOX_MESSAGE_TYPE['NORMAL']:
            self.name.setStyleSheet("QLabel { color: #5CB3FF; }")
            self.message.setAlignment(QtCore.Qt.AlignCenter)
            self.time.setStyleSheet("QLabel { color: #5CB3FF; }")
        self.message.setGeometry(QtCore.QRect(100, 0, parent.width() - 160, self.message.height()))
        self.setFixedHeight(self.message.height())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton and event.x() > self.time.x():
            self.listMenu = QtWidgets.QMenu()
            delete_item = self.listMenu.addAction(util_ui.tr('Delete message'))
            delete_item.triggered.connect(self.delete)
            parent_position = self.time.mapToGlobal(QtCore.QPoint(0, 0))
            self.listMenu.move(parent_position)
            self.listMenu.show()

    def delete(self):
        self._delete_action(self._message)

    def mark_as_sent(self):
        if self.t:
            self.time.setText(util.convert_time(self._time))
            self.t = False
            return True
        return False

    def set_avatar(self, pixmap):
        self.name.setAlignment(QtCore.Qt.AlignCenter)
        self.message.setAlignment(QtCore.Qt.AlignVCenter)
        self.setFixedHeight(max(self.height(), 36))
        self.name.setFixedHeight(self.height())
        self.message.setFixedHeight(self.height())
        self.name.setPixmap(pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def select_text(self, text):
        tmp = self.message.toHtml()
        text = h.escape(text)
        strings = re.findall(text, tmp, flags=re.IGNORECASE)
        for s in strings:
            tmp = self.replace_all(tmp, s)
        self.message.setHtml(tmp)

    @staticmethod
    def replace_all(text, substring):
        i, l = 0, len(substring)
        while i < len(text) - l + 1:
            index = text[i:].find(substring)
            if index == -1:
                break
            i += index
            lgt, rgt = text[i:].find('<'), text[i:].find('>')
            if rgt < lgt:
                i += rgt + 1
                continue
            sub = '<font color="red"><b>{}</b></font>'.format(substring)
            text = text[:i] + sub + text[i + l:]
            i += len(sub)
        return text


class FileTransferItem(QtWidgets.QListWidget):

    def __init__(self, transfer_message, file_transfer_handler, settings, width, parent=None):

        QtWidgets.QListWidget.__init__(self, parent)
        self._file_transfer_handler = file_transfer_handler
        self.resize(QtCore.QSize(width, 34))
        if transfer_message.state == FILE_TRANSFER_STATE['CANCELLED']:
            self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
        elif transfer_message.state in PAUSED_FILE_TRANSFERS:
            self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
        else:
            self.setStyleSheet('QListWidget { border: 1px solid green; }')
        self.state = transfer_message.state

        self.name = DataLabel(self)
        self.name.setGeometry(QtCore.QRect(3, 7, 95, 25))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setText(transfer_message.author.name)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(QtCore.QRect(width - 60, 7, 50, 25))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setText(util.convert_time(transfer_message.time))

        self.cancel = QtWidgets.QPushButton(self)
        self.cancel.setGeometry(QtCore.QRect(width - 125, 2, 30, 30))
        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'decline.png'))
        icon = QtGui.QIcon(pixmap)
        self.cancel.setIcon(icon)
        self.cancel.setIconSize(QtCore.QSize(30, 30))
        self.cancel.setVisible(transfer_message.state in ACTIVE_FILE_TRANSFERS)
        self.cancel.clicked.connect(
            lambda: self.cancel_transfer(transfer_message.friend_number, transfer_message.file_number))
        self.cancel.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; background-color: none;}')

        self.accept_or_pause = QtWidgets.QPushButton(self)
        self.accept_or_pause.setGeometry(QtCore.QRect(width - 170, 2, 30, 30))
        if transfer_message.state == FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
            self.accept_or_pause.setVisible(True)
            self.button_update('accept')
        elif transfer_message.state in DO_NOT_SHOW_ACCEPT_BUTTON:
            self.accept_or_pause.setVisible(False)
        elif transfer_message.state == FILE_TRANSFER_STATE['PAUSED_BY_USER']:  # setup for continue
            self.accept_or_pause.setVisible(True)
            self.button_update('resume')
        else:  # pause
            self.accept_or_pause.setVisible(True)
            self.button_update('pause')
        self.accept_or_pause.clicked.connect(
            lambda: self.accept_or_pause_transfer(transfer_message.friend_number, transfer_message.file_number,
                                                  transfer_message.size))

        self.accept_or_pause.setStyleSheet('QPushButton:hover { border: 1px solid #3A3939; background-color: none}')

        self.pb = QtWidgets.QProgressBar(self)
        self.pb.setGeometry(QtCore.QRect(100, 7, 100, 20))
        self.pb.setValue(0)
        self.pb.setStyleSheet('QProgressBar { background-color: #302F2F; }')
        self.pb.setVisible(transfer_message.state in SHOW_PROGRESS_BAR)

        self.file_name = DataLabel(self)
        self.file_name.setGeometry(QtCore.QRect(210, 7, width - 420, 20))
        font.setPointSize(12)
        self.file_name.setFont(font)
        file_size = transfer_message.size // 1024
        if not file_size:
            file_size = '{}B'.format(transfer_message.size)
        elif file_size >= 1024:
            file_size = '{}MB'.format(file_size // 1024)
        else:
            file_size = '{}KB'.format(file_size)
        file_data = '{} {}'.format(file_size, transfer_message.file_name)
        self.file_name.setText(file_data)
        self.file_name.setToolTip(transfer_message.file_name)
        self.saved_name = transfer_message.file_name
        self.time_left = QtWidgets.QLabel(self)
        self.time_left.setGeometry(QtCore.QRect(width - 92, 7, 30, 20))
        font.setPointSize(10)
        self.time_left.setFont(font)
        self.time_left.setVisible(transfer_message.state == FILE_TRANSFER_STATE['RUNNING'])
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.paused = False

    def cancel_transfer(self, friend_number, file_number):
        self._file_transfer_handler.cancel_transfer(friend_number, file_number)
        self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
        self.cancel.setVisible(False)
        self.accept_or_pause.setVisible(False)
        self.pb.setVisible(False)

    def accept_or_pause_transfer(self, friend_number, file_number, size):
        if self.state == FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
            directory = util_ui.directory_dialog(util_ui.tr('Choose folder'))
            self.pb.setVisible(True)
            if directory:
                self._file_transfer_handler.accept_transfer(directory + '/' + self.saved_name,
                                                            friend_number, file_number, size)
                self.button_update('pause')
        elif self.state == FILE_TRANSFER_STATE['PAUSED_BY_USER']:  # resume
            self.paused = False
            self._file_transfer_handler.resume_transfer(friend_number, file_number)
            self.button_update('pause')
            self.state = FILE_TRANSFER_STATE['RUNNING']
        else:  # pause
            self.paused = True
            self.state = FILE_TRANSFER_STATE['PAUSED_BY_USER']
            self._file_transfer_handler.pause_transfer(friend_number, file_number)
            self.button_update('resume')
        self.accept_or_pause.clearFocus()

    def button_update(self, path):
        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), '{}.png'.format(path)))
        icon = QtGui.QIcon(pixmap)
        self.accept_or_pause.setIcon(icon)
        self.accept_or_pause.setIconSize(QtCore.QSize(30, 30))

    def update_transfer_state(self, state, progress, time):
        self.pb.setValue(int(progress * 100))
        if time + 1:
            m, s = divmod(time, 60)
            self.time_left.setText('{0:02d}:{1:02d}'.format(m, s))
        if self.state != state and self.state in ACTIVE_FILE_TRANSFERS:
            if state == FILE_TRANSFER_STATE['CANCELLED']:
                self.setStyleSheet('QListWidget { border: 1px solid #B40404; }')
                self.cancel.setVisible(False)
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.state = state
                self.time_left.setVisible(False)
            elif state == FILE_TRANSFER_STATE['FINISHED']:
                self.accept_or_pause.setVisible(False)
                self.pb.setVisible(False)
                self.cancel.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == FILE_TRANSFER_STATE['PAUSED_BY_FRIEND']:
                self.accept_or_pause.setVisible(False)
                self.setStyleSheet('QListWidget { border: 1px solid #FF8000; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == FILE_TRANSFER_STATE['PAUSED_BY_USER']:
                self.button_update('resume')  # setup button continue
                self.setStyleSheet('QListWidget { border: 1px solid green; }')
                self.state = state
                self.time_left.setVisible(False)
            elif state == FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED']:
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

    @staticmethod
    def mark_as_sent():
        return False


class UnsentFileItem(FileTransferItem):

    def __init__(self, transfer_message, file_transfer_handler, settings, width, parent=None):
        super().__init__(transfer_message, file_transfer_handler, settings, width, parent)
        self._time = time
        self.pb.setVisible(False)
        movie = QtGui.QMovie(util.join_path(util.get_images_directory(), 'spinner.gif'))
        self.time.setMovie(movie)
        movie.start()
        self._message_id = transfer_message.message_id
        self._friend_number = transfer_message.friend_number

    def cancel_transfer(self, *args):
        self._file_transfer_handler.cancel_not_started_transfer(self._friend_number, self._message_id)


class InlineImageItem(QtWidgets.QScrollArea):

    def __init__(self, data, width, elem, parent=None):

        QtWidgets.QScrollArea.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self._elem = elem
        self._image_label = QtWidgets.QLabel(self)
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
            directory = util_ui.directory_dialog(util_ui.tr('Choose folder'))
            if directory:
                fl = QtCore.QFile(directory + '/toxygen_inline_' + util.curr_time().replace(':', '_') + '.png')
                self._pixmap.save(fl, 'PNG')

    @staticmethod
    def mark_as_sent():
        return False
