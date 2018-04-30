from PyQt5 import QtCore, QtGui, QtWidgets
import util.ui as util_ui


class DataLabel(QtWidgets.QLabel):
    """
    Label with elided text
    """
    def setText(self, text):
        text = ''.join('\u25AF' if len(bytes(c, 'utf-8')) >= 4 else c for c in text)
        metrics = QtGui.QFontMetrics(self.font())
        text = metrics.elidedText(text, QtCore.Qt.ElideRight, self.width())
        super().setText(text)


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, *args):
        super().__init__(*args)
        self.view().setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)


class CenteredWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class DialogWithResult(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result = None

    def get_result(self):
        return self._result

    result = property(get_result)

    def close_with_result(self, result):
        self._result = result
        self.close()


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def contextMenuEvent(self, event):
        menu = create_menu(self.createStandardContextMenu())
        menu.exec_(event.globalPos())
        del menu


class QRightClickButton(QtWidgets.QPushButton):
    """
    Button with right click support
    """

    rightClicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightClicked.emit()
        else:
            super().mousePressEvent(event)


class RubberBand(QtWidgets.QRubberBand):

    def __init__(self):
        super().__init__(QtWidgets.QRubberBand.Rectangle, None)
        self.setPalette(QtGui.QPalette(QtCore.Qt.transparent))
        self.pen = QtGui.QPen(QtCore.Qt.blue, 4)
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.painter = QtGui.QPainter()

    def paintEvent(self, event):

        self.painter.begin(self)
        self.painter.setPen(self.pen)
        self.painter.drawRect(event.rect())
        self.painter.end()


class RubberBandWindow(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setWindowOpacity(0.5)
        self.rubberband = RubberBand()
        self.rubberband.setWindowFlags(self.rubberband.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.rubberband.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtWidgets.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            left = QtGui.QRegion(QtCore.QRect(0, 0, self.rubberband.x(), self.height()))
            right = QtGui.QRegion(QtCore.QRect(self.rubberband.x() + self.rubberband.width(), 0, self.width(), self.height()))
            top = QtGui.QRegion(0, 0, self.width(), self.rubberband.y())
            bottom = QtGui.QRegion(0, self.rubberband.y() + self.rubberband.height(), self.width(), self.height())
            self.setMask(left + right + top + bottom)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.rubberband.setHidden(True)
            self.close()
        else:
            super().keyPressEvent(event)


def create_menu(menu):
    """
    :return translated menu
    """
    for action in menu.actions():
        text = action.text()
        if 'Link Location' in text:
            text = text.replace('Copy &Link Location',
                                util_ui.tr("Copy link location"))
        elif '&Copy' in text:
            text = text.replace('&Copy', util_ui.tr("Copy"))
        elif 'All' in text:
            text = text.replace('Select All', util_ui.tr("Select all"))
        elif 'Delete' in text:
            text = text.replace('Delete', util_ui.tr("Delete"))
        elif '&Paste' in text:
            text = text.replace('&Paste', util_ui.tr("Paste"))
        elif 'Cu&t' in text:
            text = text.replace('Cu&t', util_ui.tr("Cut"))
        elif '&Undo' in text:
            text = text.replace('&Undo', util_ui.tr("Undo"))
        elif '&Redo' in text:
            text = text.replace('&Redo', util_ui.tr("Redo"))
        else:
            menu.removeAction(action)
            continue
        action.setText(text)
    return menu


class MultilineEdit(CenteredWidget):

    def __init__(self, title, text, save):
        super(MultilineEdit, self).__init__()
        self.resize(350, 200)
        self.setMinimumSize(QtCore.QSize(350, 200))
        self.setMaximumSize(QtCore.QSize(350, 200))
        self.setWindowTitle(title)
        self.edit = QtWidgets.QTextEdit(self)
        self.edit.setGeometry(QtCore.QRect(0, 0, 350, 150))
        self.edit.setText(text)
        self.button = QtWidgets.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(0, 150, 350, 50))
        self.button.setText(util_ui.tr("Save"))
        self.button.clicked.connect(self.button_click)
        self.center()
        self.save = save

    def button_click(self):
        self.save(self.edit.toPlainText())
        self.close()
