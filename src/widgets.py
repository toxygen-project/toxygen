from PySide import QtGui, QtCore


class DataLabel(QtGui.QLabel):

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        text = metrics.elidedText(self.text(), QtCore.Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), text)


class CenteredWidget(QtGui.QWidget):

    def __init__(self):
        super(CenteredWidget, self).__init__()
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class QRightClickButton(QtGui.QPushButton):
    def __init__(self, parent):
        super(QRightClickButton, self).__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.emit(QtCore.SIGNAL("rightClicked()"))
        else:
            super(QRightClickButton, self).mousePressEvent(event)
