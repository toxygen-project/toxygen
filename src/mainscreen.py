# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore


class MainWindow(QtGui.QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    def setup_left_top(self, Form):
        Form.setObjectName("Form")
        Form.resize(500, 300)
        Form.setMinimumSize(QtCore.QSize(250, 100))
        Form.setMaximumSize(QtCore.QSize(250, 100))
        Form.setBaseSize(QtCore.QSize(2500, 100))
        self.graphicsView = QtGui.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(10, 20, 64, 64))
        self.graphicsView.setMinimumSize(QtCore.QSize(64, 64))
        self.graphicsView.setMaximumSize(QtCore.QSize(64, 64))
        self.graphicsView.setBaseSize(QtCore.QSize(64, 64))
        self.graphicsView.setObjectName("graphicsView")
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(80, 30, 191, 17))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(80, 60, 191, 17))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setWeight(50)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.graphicsView_2 = QtGui.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(200, 34, 64, 64))
        self.graphicsView_2.setMinimumSize(QtCore.QSize(32, 32))
        self.graphicsView_2.setMaximumSize(QtCore.QSize(32, 32))
        self.graphicsView_2.setBaseSize(QtCore.QSize(32, 32))
        self.graphicsView_2.setObjectName("graphicsView_2")

    def initUI(self):

        grid = QtGui.QGridLayout()
        name = QtGui.QWidget()
        self.setup_left_top(name)
        grid.addWidget(name, 0, 0)

        self.setLayout(grid)
        self.setMinimumSize(200, 200)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Toxygen')
        self.show()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
