try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui
from widgets import RubberBand, create_menu
from profile import Profile


class MessageArea(QtGui.QPlainTextEdit):
    """User enters messages here"""

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
            print rect
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
                Profile.get_instance().send_screenshot(str(byte_array.data()))
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.rubberband.setHidden(True)
            self.close()
        else:
            super(ScreenShotWindow, self).keyPressEvent(event)
