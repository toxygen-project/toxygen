try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from widgets import RubberBand, create_menu, QRightClickButton, CenteredWidget
from profile import Profile
import smileys
import util


class MessageArea(QtGui.QPlainTextEdit):
    """User types messages here"""

    def __init__(self, parent, form):
        super(MessageArea, self).__init__(parent)
        self.parent = form
        self.setAcceptDrops(True)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.parent.profile.send_typing(False))

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Paste):
            self.pasteEvent()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            modifiers = event.modifiers()
            if modifiers & QtCore.Qt.ControlModifier or modifiers & QtCore.Qt.ShiftModifier:
                self.insertPlainText('\n')
            else:
                if self.timer.isActive():
                    self.timer.stop()
                self.parent.profile.send_typing(False)
                self.parent.send_message()
        elif event.key() == QtCore.Qt.Key_Up and not self.toPlainText():
            self.appendPlainText(Profile.get_instance().get_last_message())
        else:
            self.parent.profile.send_typing(True)
            if self.timer.isActive():
                self.timer.stop()
            self.timer.start(5000)
            super(MessageArea, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        menu = create_menu(self.createStandardContextMenu())
        menu.exec_(event.globalPos())
        del menu

    def dragEnterEvent(self, e):
        e.accept()

    def dragMoveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
            self.pasteEvent(e.mimeData().text())
        else:
            e.ignore()

    def pasteEvent(self, text=None):
        text = text or QtGui.QApplication.clipboard().text()
        if text.startswith('file://'):
            self.parent.profile.send_file(text[7:])
        else:
            self.insertPlainText(text)


class ScreenShotWindow(QtGui.QWidget):

    def __init__(self, parent):
        super(ScreenShotWindow, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setWindowOpacity(0.5)
        self.rubberband = RubberBand()

    def closeEvent(self, *args):
        if self.parent.isHidden():
            self.parent.show()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            left = QtGui.QRegion(QtCore.QRect(0, 0, self.rubberband.x(), self.height()))
            right = QtGui.QRegion(QtCore.QRect(self.rubberband.x() + self.rubberband.width(), 0, self.width(), self.height()))
            top = QtGui.QRegion(0, 0, self.width(), self.rubberband.y())
            bottom = QtGui.QRegion(0, self.rubberband.y() + self.rubberband.height(), self.width(), self.height())
            self.setMask(left + right + top + bottom)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            if rect.width() and rect.height():
                p = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId(),
                                             rect.x() + 4,
                                             rect.y() + 4,
                                             rect.width() - 8,
                                             rect.height() - 8)
                byte_array = QtCore.QByteArray()
                buffer = QtCore.QBuffer(byte_array)
                buffer.open(QtCore.QIODevice.WriteOnly)
                p.save(buffer, 'PNG')
                Profile.get_instance().send_screenshot(bytes(byte_array.data()))
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.rubberband.setHidden(True)
            self.close()
        else:
            super(ScreenShotWindow, self).keyPressEvent(event)


class SmileyWindow(QtGui.QWidget):
    """
    Smiley selection window
    """

    def __init__(self, parent):
        super(SmileyWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        inst = smileys.SmileyLoader.get_instance()
        self.data = inst.get_smileys()
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
            elem = QtGui.QRadioButton(self)
            elem.setGeometry(QtCore.QRect(i * 20 + 5, 180, 20, 20))
            elem.clicked.connect(lambda i=i: self.checked(i))
            self.radio.append(elem)
        width = max(self.page_count * 20 + 30, (self.page_size + 5) * 8 // 10)
        self.setMaximumSize(width, 200)
        self.setMinimumSize(width, 200)
        self.buttons = []
        for i in range(self.page_size):  # pages - radio buttons
            b = QtGui.QPushButton(self)
            b.setGeometry(QtCore.QRect((i // 8) * 20 + 5, (i % 8) * 20, 20, 20))
            b.clicked.connect(lambda i=i: self.clicked(i))
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


class MenuButton(QtGui.QPushButton):

    def __init__(self, parent, enter):
        super(MenuButton, self).__init__(parent)
        self.enter = enter

    def enterEvent(self, event):
        self.enter()
        super(MenuButton, self).enterEvent(event)


class DropdownMenu(QtGui.QWidget):

    def __init__(self, parent):
        super(DropdownMenu, self).__init__(parent)
        self.installEventFilter(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setMaximumSize(180, 120)
        self.setMinimumSize(180, 120)
        self.screenshotButton = QRightClickButton(self)
        self.screenshotButton.setGeometry(QtCore.QRect(0, 60, 60, 60))
        self.screenshotButton.setObjectName("screenshotButton")

        self.fileTransferButton = QtGui.QPushButton(self)
        self.fileTransferButton.setGeometry(QtCore.QRect(60, 60, 60, 60))
        self.fileTransferButton.setObjectName("fileTransferButton")

        self.audioMessageButton = QtGui.QPushButton(self)
        self.audioMessageButton.setGeometry(QtCore.QRect(120, 60, 60, 60))

        self.smileyButton = QtGui.QPushButton(self)
        self.smileyButton.setGeometry(QtCore.QRect(0, 0, 60, 60))

        self.videoMessageButton = QtGui.QPushButton(self)
        self.videoMessageButton.setGeometry(QtCore.QRect(120, 0, 60, 60))

        self.stickerButton = QtGui.QPushButton(self)
        self.stickerButton.setGeometry(QtCore.QRect(60, 0, 60, 60))

        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/file.png')
        icon = QtGui.QIcon(pixmap)
        self.fileTransferButton.setIcon(icon)
        self.fileTransferButton.setIconSize(QtCore.QSize(50, 50))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/screenshot.png')
        icon = QtGui.QIcon(pixmap)
        self.screenshotButton.setIcon(icon)
        self.screenshotButton.setIconSize(QtCore.QSize(50, 60))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/audio_message.png')
        icon = QtGui.QIcon(pixmap)
        self.audioMessageButton.setIcon(icon)
        self.audioMessageButton.setIconSize(QtCore.QSize(50, 50))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/smiley.png')
        icon = QtGui.QIcon(pixmap)
        self.smileyButton.setIcon(icon)
        self.smileyButton.setIconSize(QtCore.QSize(50, 50))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/video_message.png')
        icon = QtGui.QIcon(pixmap)
        self.videoMessageButton.setIcon(icon)
        self.videoMessageButton.setIconSize(QtCore.QSize(55, 55))
        pixmap = QtGui.QPixmap(util.curr_directory() + '/images/sticker.png')
        icon = QtGui.QIcon(pixmap)
        self.stickerButton.setIcon(icon)
        self.stickerButton.setIconSize(QtCore.QSize(55, 55))

        self.screenshotButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Send screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.fileTransferButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Send file", None, QtGui.QApplication.UnicodeUTF8))
        self.audioMessageButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Send audio message", None, QtGui.QApplication.UnicodeUTF8))
        self.videoMessageButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Send video message", None, QtGui.QApplication.UnicodeUTF8))
        self.smileyButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Add smiley", None, QtGui.QApplication.UnicodeUTF8))
        self.stickerButton.setToolTip(QtGui.QApplication.translate("MenuWindow", "Send sticker", None, QtGui.QApplication.UnicodeUTF8))

        self.fileTransferButton.clicked.connect(parent.send_file)
        self.screenshotButton.clicked.connect(parent.send_screenshot)
        self.connect(self.screenshotButton, QtCore.SIGNAL("rightClicked()"), lambda: parent.send_screenshot(True))
        self.smileyButton.clicked.connect(parent.send_smiley)
        self.stickerButton.clicked.connect(parent.send_sticker)

    def leaveEvent(self, event):
        self.close()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowDeactivate:
            self.close()
        return False


class StickerItem(QtGui.QWidget):

    def __init__(self, fl):
        super(StickerItem, self).__init__()
        self._image_label = QtGui.QLabel(self)
        self.path = fl
        self.pixmap = QtGui.QPixmap()
        self.pixmap.load(fl)
        if self.pixmap.width() > 150:
            self.pixmap = self.pixmap.scaled(150, 200, QtCore.Qt.KeepAspectRatio)
        self.setFixedSize(150, self.pixmap.height())
        self._image_label.setPixmap(self.pixmap)


class StickerWindow(QtGui.QWidget):
    """Sticker selection window"""

    def __init__(self, parent):
        super(StickerWindow, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setMaximumSize(250, 200)
        self.setMinimumSize(250, 200)
        self.list = QtGui.QListWidget(self)
        self.list.setGeometry(QtCore.QRect(0, 0, 250, 200))
        self.arr = smileys.sticker_loader()
        for sticker in self.arr:
            item = StickerItem(sticker)
            elem = QtGui.QListWidgetItem()
            elem.setSizeHint(QtCore.QSize(250, item.height()))
            self.list.addItem(elem)
            self.list.setItemWidget(elem, item)
        self.list.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.list.setSpacing(3)
        self.list.clicked.connect(self.click)
        self.parent = parent

    def click(self, index):
        num = index.row()
        self.parent.profile.send_sticker(self.arr[num])
        self.close()

    def leaveEvent(self, event):
        self.close()


class WelcomeScreen(CenteredWidget):

    def __init__(self):
        super().__init__()
        self.setMaximumSize(250, 200)
        self.setMinimumSize(250, 200)
        self.center()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.text = QtGui.QTextBrowser(self)
        self.text.setGeometry(QtCore.QRect(0, 0, 250, 170))
        self.text.setOpenExternalLinks(True)
        self.checkbox = QtGui.QCheckBox(self)
        self.checkbox.setGeometry(QtCore.QRect(5, 170, 240, 30))
        self.checkbox.setText(QtGui.QApplication.translate('WelcomeScreen', "Don't show again",
                                                           None, QtGui.QApplication.UnicodeUTF8))
        self.setWindowTitle(QtGui.QApplication.translate('WelcomeScreen', 'Tip of the day',
                                                         None, QtGui.QApplication.UnicodeUTF8))
        import random
        num = random.randint(0, 10)
        if num == 0:
            text = QtGui.QApplication.translate('WelcomeScreen', 'Press Esc if you want hide app to tray.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 1:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Right click on screenshot button hides app to tray during screenshot.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 2:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'You can use Tox over Tor. For more info read <a href="https://wiki.tox.chat/users/tox_over_tor_tot">this post</a>',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 3:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Use Settings -> Interface to customize interface.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 4:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Set profile password via Profile -> Settings. Password allows Toxygen encrypt your history and settings.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 5:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Since v0.1.3 Toxygen supports plugins. <a href="https://github.com/xveduk/toxygen/blob/master/docs/plugins.md">Read more</a>',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 6:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'New in Toxygen v0.2.3:<br>TCS compliance<br>Plugins, smileys and stickers import<br>Bug fixes',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 7:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Toxygen supports faux offline messages and file transfers. Send message or file to offline friend and he will get it later.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 8:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Delete single message in chat: make right click on spinner or message time and choose "Delete" in menu',
                                                None, QtGui.QApplication.UnicodeUTF8)
        elif num == 9:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Use right click on inline image to save it',
                                                None, QtGui.QApplication.UnicodeUTF8)
        else:
            text = QtGui.QApplication.translate('WelcomeScreen',
                                                'Set new NoSpam to avoid spam friend requests: Profile -> Settings -> Set new NoSpam.',
                                                None, QtGui.QApplication.UnicodeUTF8)
        self.text.setHtml(text)
        self.checkbox.stateChanged.connect(self.not_show)
        QtCore.QTimer.singleShot(1000, self.show)

    def not_show(self):
        import settings
        s = settings.Settings.get_instance()
        s['show_welcome_screen'] = False
        s.save()

