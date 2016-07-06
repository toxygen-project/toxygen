try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


class DataLabel(QtGui.QLabel):
    """
    Label with elided text
    """
    def setText(self, text):
        text = ''.join(c if c <= '\u10FFFF' else '\u25AF' for c in text)
        metrics = QtGui.QFontMetrics(self.font())
        text = metrics.elidedText(text, QtCore.Qt.ElideRight, self.width())
        super().setText(text)


class CenteredWidget(QtGui.QWidget):

    def __init__(self):
        super(CenteredWidget, self).__init__()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class LineEdit(QtGui.QLineEdit):

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def contextMenuEvent(self, event):
        menu = create_menu(self.createStandardContextMenu())
        menu.exec_(event.globalPos())
        del menu


class QRightClickButton(QtGui.QPushButton):
    """
    Button with right click support
    """

    def __init__(self, parent):
        super(QRightClickButton, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.emit(QtCore.SIGNAL("rightClicked()"))
        else:
            super(QRightClickButton, self).mousePressEvent(event)


class RubberBand(QtGui.QRubberBand):

    def __init__(self):
        super(RubberBand, self).__init__(QtGui.QRubberBand.Rectangle, None)
        self.setPalette(QtGui.QPalette(QtCore.Qt.transparent))
        self.pen = QtGui.QPen(QtCore.Qt.blue, 4)
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.painter = QtGui.QPainter()

    def paintEvent(self, event):

        self.painter.begin(self)
        self.painter.setPen(self.pen)
        self.painter.drawRect(event.rect())
        self.painter.end()


def create_menu(menu):
    """
    :return translated menu
    """
    for action in menu.actions():
        text = action.text()
        if 'Link Location' in text:
            text = text.replace('Copy &Link Location',
                                QtGui.QApplication.translate("MainWindow", "Copy link location", None,
                                                             QtGui.QApplication.UnicodeUTF8))
        elif '&Copy' in text:
            text = text.replace('&Copy', QtGui.QApplication.translate("MainWindow", "Copy", None,
                                                                      QtGui.QApplication.UnicodeUTF8))
        elif 'All' in text:
            text = text.replace('Select All', QtGui.QApplication.translate("MainWindow", "Select all", None,
                                                                           QtGui.QApplication.UnicodeUTF8))
        elif 'Delete' in text:
            text = text.replace('Delete', QtGui.QApplication.translate("MainWindow", "Delete", None,
                                                                       QtGui.QApplication.UnicodeUTF8))
        elif '&Paste' in text:
            text = text.replace('&Paste', QtGui.QApplication.translate("MainWindow", "Paste", None,
                                                                       QtGui.QApplication.UnicodeUTF8))
        elif 'Cu&t' in text:
            text = text.replace('Cu&t', QtGui.QApplication.translate("MainWindow", "Cut", None,
                                                                     QtGui.QApplication.UnicodeUTF8))
        elif '&Undo' in text:
            text = text.replace('&Undo', QtGui.QApplication.translate("MainWindow", "Undo", None,
                                                                      QtGui.QApplication.UnicodeUTF8))
        elif '&Redo' in text:
            text = text.replace('&Redo', QtGui.QApplication.translate("MainWindow", "Redo", None,
                                                                      QtGui.QApplication.UnicodeUTF8))
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
        self.edit = QtGui.QTextEdit(self)
        self.edit.setGeometry(QtCore.QRect(0, 0, 350, 150))
        self.edit.setText(text)
        self.button = QtGui.QPushButton(self)
        self.button.setGeometry(QtCore.QRect(0, 150, 350, 50))
        self.button.setText(QtGui.QApplication.translate("MainWindow", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.button.clicked.connect(self.button_click)
        self.center()
        self.save = save

    def button_click(self):
        self.save(self.edit.toPlainText())
        self.close()

