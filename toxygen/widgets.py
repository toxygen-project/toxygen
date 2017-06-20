from PyQt5 import QtCore, QtGui, QtWidgets


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
        super(CenteredWidget, self).__init__()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


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

    def __init__(self, parent):
        super(QRightClickButton, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(QRightClickButton, self).mousePressEvent(event)


class RubberBand(QtWidgets.QRubberBand):

    def __init__(self):
        super(RubberBand, self).__init__(QtWidgets.QRubberBand.Rectangle, None)
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
                                QtWidgets.QApplication.translate("MainWindow", "Copy link location"))
        elif '&Copy' in text:
            text = text.replace('&Copy', QtWidgets.QApplication.translate("MainWindow", "Copy"))
        elif 'All' in text:
            text = text.replace('Select All', QtWidgets.QApplication.translate("MainWindow", "Select all"))
        elif 'Delete' in text:
            text = text.replace('Delete', QtWidgets.QApplication.translate("MainWindow", "Delete"))
        elif '&Paste' in text:
            text = text.replace('&Paste', QtWidgets.QApplication.translate("MainWindow", "Paste"))
        elif 'Cu&t' in text:
            text = text.replace('Cu&t', QtWidgets.QApplication.translate("MainWindow", "Cut"))
        elif '&Undo' in text:
            text = text.replace('&Undo', QtWidgets.QApplication.translate("MainWindow", "Undo"))
        elif '&Redo' in text:
            text = text.replace('&Redo', QtWidgets.QApplication.translate("MainWindow", "Redo"))
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
        self.button.setText(QtWidgets.QApplication.translate("MainWindow", "Save"))
        self.button.clicked.connect(self.button_click)
        self.center()
        self.save = save

    def button_click(self):
        self.save(self.edit.toPlainText())
        self.close()
