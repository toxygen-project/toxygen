try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


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
