from PyQt5 import QtCore, QtGui, QtWidgets
from ui.widgets import RubberBandWindow, create_menu, QRightClickButton, CenteredWidget, LineEdit
from contacts.profile import Profile
import urllib
import utils.util as util
import utils.ui as util_ui
from stickers.stickers import load_stickers


class MessageArea(QtWidgets.QPlainTextEdit):
    """User types messages here"""

    def __init__(self, parent, form):
        super().__init__(parent)
        self._messenger = None
        self.parent = form
        self.setAcceptDrops(True)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(lambda: self._messenger.send_typing(False))

    def set_messenger(self, messenger):
        self._messenger = messenger

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            mimeData = QtWidgets.QApplication.clipboard().mimeData()
            if mimeData.hasUrls():
                for url in mimeData.urls():
                    self.pasteEvent(url.toString())
            else:
                self.pasteEvent()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            modifiers = event.modifiers()
            if modifiers & QtCore.Qt.ControlModifier or modifiers & QtCore.Qt.ShiftModifier:
                self.insertPlainText('\n')
            else:
                if self._timer.isActive():
                    self._timer.stop()
                self._messenger.send_typing(False)
                self._messenger.send_message()
        elif event.key() == QtCore.Qt.Key_Up and not self.toPlainText():
            self.appendPlainText(self._messenger.get_last_message())
        elif event.key() == QtCore.Qt.Key_Tab and not self._messenger.is_active_a_friend():
            text = self.toPlainText()
            pos = self.textCursor().position()
            self.insertPlainText(self._messenger.get_gc_peer_name(text[:pos]))
        else:
            self._messenger.send_typing(True)
            if self._timer.isActive():
                self._timer.stop()
            self._timer.start(5000)
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = create_menu(self.createStandardContextMenu())
        menu.exec_(event.globalPos())
        del menu

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        if e.mimeData().hasFormat('text/plain') or e.mimeData().hasFormat('text/html'):
            e.accept()
            self.pasteEvent(e.mimeData().text())
        elif e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                self.pasteEvent(url.toString())
            e.accept()
        else:
            e.ignore()

    def pasteEvent(self, text=None):
        text = text or QtWidgets.QApplication.clipboard().text()
        if text.startswith('file://'):
            file_name = self.parse_file_name(text)
            self.parent.profile.send_file(file_name)
        else:
            self.insertPlainText(text)

    @staticmethod
    def parse_file_name(file_name):
        if file_name.endswith('\r\n'):
            file_name = file_name[:-2]
        file_name = urllib.parse.unquote(file_name)
        return file_name[8 if util.get_platform() == 'Windows' else 7:]


class ScreenShotWindow(RubberBandWindow):

    def __init__(self, file_transfer_handler, contacts_manager, *args):
        super().__init__(*args)
        self._file_transfer_handler = file_transfer_handler
        self._contacts_manager = contacts_manager

    def closeEvent(self, *args):
        if self.parent.isHidden():
            self.parent.show()

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            if rect.width() and rect.height():
                screen = QtWidgets.QApplication.primaryScreen()
                p = screen.grabWindow(0,
                                      rect.x() + 4,
                                      rect.y() + 4,
                                      rect.width() - 8,
                                      rect.height() - 8)
                byte_array = QtCore.QByteArray()
                buffer = QtCore.QBuffer(byte_array)
                buffer.open(QtCore.QIODevice.WriteOnly)
                p.save(buffer, 'PNG')
                friend = self._contacts_manager.get_curr_contact()
                self._file_transfer_handler.send_screenshot(bytes(byte_array.data()), friend.number)
            self.close()


class SmileyWindow(QtWidgets.QWidget):
    """
    Smiley selection window
    """

    def __init__(self, parent, smiley_loader):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.data = smiley_loader.get_smileys()
        count = len(self.data)
        if not count:
            self.close()
        self.page_size = int(pow(count / 8, 0.5) + 1) * 8  # smileys per page
        if count % self.page_size == 0:
            self.page_count = count // self.page_size
        else:
            self.page_count = round(count / self.page_size + 0.5)
        self.page = -1
        self.radio = []
        self.parent = parent
        for i in range(self.page_count):  # buttons with smileys
            elem = QtWidgets.QRadioButton(self)
            elem.setGeometry(QtCore.QRect(i * 20 + 5, 180, 20, 20))
            elem.clicked.connect(lambda c, t=i: self.checked(t))
            self.radio.append(elem)
        width = max(self.page_count * 20 + 30, (self.page_size + 5) * 8 // 10)
        self.setMaximumSize(width, 200)
        self.setMinimumSize(width, 200)
        self.buttons = []
        for i in range(self.page_size):  # pages - radio buttons
            b = QtWidgets.QPushButton(self)
            b.setGeometry(QtCore.QRect((i // 8) * 20 + 5, (i % 8) * 20, 20, 20))
            b.clicked.connect(lambda c, t=i: self.clicked(t))
            self.buttons.append(b)
        self.checked(0)

    def checked(self, pos):  # new page opened
        self.radio[self.page].setChecked(False)
        self.radio[pos].setChecked(True)
        self.page = pos
        start = self.page * self.page_size
        for i in range(self.page_size):
            try:
                self.buttons[i].setVisible(True)
                pixmap = QtGui.QPixmap(self.data[start + i][1])
                icon = QtGui.QIcon(pixmap)
                self.buttons[i].setIcon(icon)
            except:
                self.buttons[i].setVisible(False)

    def clicked(self, pos):  # smiley selected
        pos += self.page * self.page_size
        smiley = self.data[pos][0]
        self.parent.messageEdit.insertPlainText(smiley)
        self.close()

    def leaveEvent(self, event):
        self.close()


class MenuButton(QtWidgets.QPushButton):

    def __init__(self, parent, enter):
        super().__init__(parent)
        self.enter = enter

    def enterEvent(self, event):
        self.enter()
        super().enterEvent(event)


class DropdownMenu(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.installEventFilter(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setMaximumSize(120, 120)
        self.setMinimumSize(120, 120)
        self.screenshotButton = QRightClickButton(self)
        self.screenshotButton.setGeometry(QtCore.QRect(0, 60, 60, 60))
        self.screenshotButton.setObjectName("screenshotButton")

        self.fileTransferButton = QtWidgets.QPushButton(self)
        self.fileTransferButton.setGeometry(QtCore.QRect(60, 60, 60, 60))
        self.fileTransferButton.setObjectName("fileTransferButton")

        self.smileyButton = QtWidgets.QPushButton(self)
        self.smileyButton.setGeometry(QtCore.QRect(0, 0, 60, 60))

        self.stickerButton = QtWidgets.QPushButton(self)
        self.stickerButton.setGeometry(QtCore.QRect(60, 0, 60, 60))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'file.png'))
        icon = QtGui.QIcon(pixmap)
        self.fileTransferButton.setIcon(icon)
        self.fileTransferButton.setIconSize(QtCore.QSize(50, 50))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'screenshot.png'))
        icon = QtGui.QIcon(pixmap)
        self.screenshotButton.setIcon(icon)
        self.screenshotButton.setIconSize(QtCore.QSize(50, 60))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'smiley.png'))
        icon = QtGui.QIcon(pixmap)
        self.smileyButton.setIcon(icon)
        self.smileyButton.setIconSize(QtCore.QSize(50, 50))

        pixmap = QtGui.QPixmap(util.join_path(util.get_images_directory(), 'sticker.png'))
        icon = QtGui.QIcon(pixmap)
        self.stickerButton.setIcon(icon)
        self.stickerButton.setIconSize(QtCore.QSize(55, 55))

        self.screenshotButton.setToolTip(util_ui.tr("Send screenshot"))
        self.fileTransferButton.setToolTip(util_ui.tr("Send file"))
        self.smileyButton.setToolTip(util_ui.tr("Add smiley"))
        self.stickerButton.setToolTip(util_ui.tr("Send sticker"))

        self.fileTransferButton.clicked.connect(parent.send_file)
        self.screenshotButton.clicked.connect(parent.send_screenshot)
        self.screenshotButton.rightClicked.connect(lambda: parent.send_screenshot(True))
        self.smileyButton.clicked.connect(parent.send_smiley)
        self.stickerButton.clicked.connect(parent.send_sticker)

    def leaveEvent(self, event):
        self.close()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.WindowDeactivate:
            self.close()
        return False


class StickerItem(QtWidgets.QWidget):

    def __init__(self, fl):
        super().__init__()
        self._image_label = QtWidgets.QLabel(self)
        self.path = fl
        self.pixmap = QtGui.QPixmap()
        self.pixmap.load(fl)
        if self.pixmap.width() > 150:
            self.pixmap = self.pixmap.scaled(150, 200, QtCore.Qt.KeepAspectRatio)
        self.setFixedSize(150, self.pixmap.height())
        self._image_label.setPixmap(self.pixmap)


class StickerWindow(QtWidgets.QWidget):
    """Sticker selection window"""

    def __init__(self, file_transfer_handler, contacts_manager):
        super().__init__()
        self._file_transfer_handler = file_transfer_handler
        self._contacts_manager = contacts_manager
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setMaximumSize(250, 200)
        self.setMinimumSize(250, 200)
        self.list = QtWidgets.QListWidget(self)
        self.list.setGeometry(QtCore.QRect(0, 0, 250, 200))
        self._stickers = load_stickers()
        for sticker in self._stickers:
            item = StickerItem(sticker)
            elem = QtWidgets.QListWidgetItem()
            elem.setSizeHint(QtCore.QSize(250, item.height()))
            self.list.addItem(elem)
            self.list.setItemWidget(elem, item)
        self.list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.list.setSpacing(3)
        self.list.clicked.connect(self.click)

    def click(self, index):
        num = index.row()
        friend = self._contacts_manager.get_curr_contact()
        self._file_transfer_handler.send_sticker(self._stickers[num], friend.number)
        self.close()

    def leaveEvent(self, event):
        self.close()


class WelcomeScreen(CenteredWidget):

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        self.setMaximumSize(250, 200)
        self.setMinimumSize(250, 200)
        self.center()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.text = QtWidgets.QTextBrowser(self)
        self.text.setGeometry(QtCore.QRect(0, 0, 250, 170))
        self.text.setOpenExternalLinks(True)
        self.checkbox = QtWidgets.QCheckBox(self)
        self.checkbox.setGeometry(QtCore.QRect(5, 170, 240, 30))
        self.checkbox.setText(util_ui.tr( "Don't show again"))
        self.setWindowTitle(util_ui.tr( 'Tip of the day'))
        import random
        num = random.randint(0, 10)
        if num == 0:
            text = util_ui.tr('Press Esc if you want hide app to tray.')
        elif num == 1:
            text = util_ui.tr('Right click on screenshot button hides app to tray during screenshot.')
        elif num == 2:
            text = util_ui.tr('You can use Tox over Tor. For more info read <a href="https://wiki.tox.chat/users/tox_over_tor_tot">this post</a>')
        elif num == 3:
            text = util_ui.tr('Use Settings -> Interface to customize interface.')
        elif num == 4:
            text = util_ui.tr('Set profile password via Profile -> Settings. Password allows Toxygen encrypt your history and settings.')
        elif num == 5:
            text = util_ui.tr('Since v0.1.3 Toxygen supports plugins. <a href="https://github.com/toxygen-project/toxygen/blob/master/docs/plugins.md">Read more</a>')
        elif num == 6:
            text = util_ui.tr('Toxygen supports faux offline messages and file transfers. Send message or file to offline friend and he will get it later.')
        elif num == 7:
            text = util_ui.tr('New in Toxygen 0.4.1:<br>Downloading nodes from tox.chat<br>Bug fixes')
        elif num == 8:
            text = util_ui.tr('Delete single message in chat: make right click on spinner or message time and choose "Delete" in menu')
        elif num == 9:
            text = util_ui.tr( 'Use right click on inline image to save it')
        else:
            text = util_ui.tr('Set new NoSpam to avoid spam friend requests: Profile -> Settings -> Set new NoSpam.')
        self.text.setHtml(text)
        self.checkbox.stateChanged.connect(self.not_show)
        QtCore.QTimer.singleShot(1000, self.show)

    def not_show(self):
        self._settings['show_welcome_screen'] = False
        self._settings.save()


class MainMenuButton(QtWidgets.QPushButton):

    def __init__(self, *args):
        super().__init__(*args)
        self.setObjectName("mainmenubutton")

    def setText(self, text):
        metrics = QtGui.QFontMetrics(self.font())
        self.setFixedWidth(metrics.size(QtCore.Qt.TextSingleLine, text).width() + 20)
        super().setText(text)


class ClickableLabel(QtWidgets.QLabel):

    clicked = QtCore.pyqtSignal()

    def __init__(self, *args):
        super().__init__(*args)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()


class SearchScreen(QtWidgets.QWidget):

    def __init__(self, messages, width, *args):
        super().__init__(*args)
        self.setMaximumSize(width, 40)
        self.setMinimumSize(width, 40)
        self._messages = messages

        self.search_text = LineEdit(self)
        self.search_text.setGeometry(0, 0, width - 160, 40)

        self.search_button = ClickableLabel(self)
        self.search_button.setGeometry(width - 160, 0, 40, 40)
        pixmap = QtGui.QPixmap()
        pixmap.load(util.join_path(util.get_images_directory(), 'search.png'))
        self.search_button.setScaledContents(False)
        self.search_button.setAlignment(QtCore.Qt.AlignCenter)
        self.search_button.setPixmap(pixmap)
        self.search_button.clicked.connect(self.search)

        font = QtGui.QFont()
        font.setPointSize(32)
        font.setBold(True)

        self.prev_button = QtWidgets.QPushButton(self)
        self.prev_button.setGeometry(width - 120, 0, 40, 40)
        self.prev_button.clicked.connect(self.prev)
        self.prev_button.setText('\u25B2')

        self.next_button = QtWidgets.QPushButton(self)
        self.next_button.setGeometry(width - 80, 0, 40, 40)
        self.next_button.clicked.connect(self.next)
        self.next_button.setText('\u25BC')

        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setGeometry(width - 40, 0, 40, 40)
        self.close_button.clicked.connect(self.close)
        self.close_button.setText('×')
        self.close_button.setFont(font)

        font.setPointSize(18)
        self.next_button.setFont(font)
        self.prev_button.setFont(font)

        self.retranslateUi()

    def retranslateUi(self):
        self.search_text.setPlaceholderText(util_ui.tr('Search'))

    def show(self):
        super().show()
        self.search_text.setFocus()

    def search(self):
        Profile.get_instance().update()
        text = self.search_text.text()
        friend = Profile.get_instance().get_curr_friend()
        if text and friend and util.is_re_valid(text):
            index = friend.search_string(text)
            self.load_messages(index)

    def prev(self):
        friend = Profile.get_instance().get_curr_friend()
        if friend is not None:
            index = friend.search_prev()
            self.load_messages(index)

    def next(self):
        friend = Profile.get_instance().get_curr_friend()
        text = self.search_text.text()
        if friend is not None:
            index = friend.search_next()
            if index is not None:
                count = self._messages.count()
                index += count
                item = self._messages.item(index)
                self._messages.scrollToItem(item)
                self._messages.itemWidget(item).select_text(text)
            else:
                self.not_found(text)

    def load_messages(self, index):
        text = self.search_text.text()
        if index is not None:
            profile = Profile.get_instance()
            count = self._messages.count()
            while count + index < 0:
                profile.load_history()
                count = self._messages.count()
            index += count
            item = self._messages.item(index)
            self._messages.scrollToItem(item)
            self._messages.itemWidget(item).select_text(text)
        else:
            self.not_found(text)

    def closeEvent(self, *args):
        self._messages.setGeometry(0, 0, self._messages.width(), self._messages.height() + 40)
        super().closeEvent(*args)

    @staticmethod
    def not_found(text):
        util_ui.message_box(util_ui.tr('Text "{}" was not found').format(text), util_ui.tr('Not found'))
