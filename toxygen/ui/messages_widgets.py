from PyQt5 import QtWidgets, QtGui, QtCore
from wrapper.toxcore_enums_and_consts import *
import ui.widgets as widgets
import util.ui as util_ui
import util.util as util
import ui.menu as menu
import html as h
import re
from messenger.messages import MESSAGE_AUTHOR


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
        text = self._smileys_loader.add_smileys_to_text(text, self)  # smileys
        return text


class MessageItem(QtWidgets.QWidget):
    """
    Message in messages list
    """
    def __init__(self, settings, message_browser_factory_method, text_message, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.name = widgets.DataLabel(self)
        self.name.setGeometry(QtCore.QRect(2, 2, 95, 23))
        self.name.setTextFormat(QtCore.Qt.PlainText)
        font = QtGui.QFont()
        font.setFamily(settings['font'])
        font.setPointSize(11)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setText(text_message.author.name)

        self.time = QtWidgets.QLabel(self)
        self.time.setGeometry(QtCore.QRect(parent.width() - 60, 0, 50, 25))
        font.setPointSize(10)
        font.setBold(False)
        self.time.setFont(font)
        self._time = text_message.time
        if text_message.author.type == MESSAGE_AUTHOR['NOT_SENT']:
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
        pr = profile.Profile.get_instance()
        pr.delete_message(self._time)

    def mark_as_sent(self):
        if self.t:
            self.time.setText(convert_time(self._time))
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

