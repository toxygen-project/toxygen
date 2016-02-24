# -*- coding: utf-8 -*-

import sys
from PySide import QtGui, QtCore
from menu import *
from toxcore_enums_and_consts import *


class StatusCircle(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setGeometry(0, 0, 32, 32)
        self.status = TOX_USER_CONNECTION_STATUS['OFFLINE']
        self.tox = parent.tox

    def mouseReleaseEvent(self, event):
        if self.status != TOX_USER_CONNECTION_STATUS['OFFLINE']:
            self.status += 1
            self.status %= TOX_USER_CONNECTION_STATUS['OFFLINE']
            self.tox.self_set_status(self.status)
            self.repaint()

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        paint.setRenderHint(QtGui.QPainter.Antialiasing)
        paint.setBrush(QtCore.Qt.white)
        paint.drawRect(event.rect())
        k = 16
        rad_x = rad_y = 10
        if self.status == TOX_USER_CONNECTION_STATUS['OFFLINE']:
            color = QtCore.Qt.black
        elif self.status == TOX_USER_CONNECTION_STATUS['ONLINE']:
            color = QtCore.Qt.green
        elif self.status == TOX_USER_CONNECTION_STATUS['AWAY']:
            color = QtCore.Qt.yellow
        else:  # self.status == TOX_USER_CONNECTION_STATUS['BUSY']:
            color = QtCore.Qt.red

        paint.setPen(color)
        center = QtCore.QPoint(k, k)
        paint.setBrush(color)
        paint.drawEllipse(center, rad_x, rad_y)
        paint.end()


class MainWindow(QtGui.QMainWindow):

    def __init__(self, tox):
        super(MainWindow, self).__init__()
        self.tox = tox
        self.initUI()

    def setup_menu(self, MainWindow):
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setNativeMenuBar(False)
        self.menubar.setMinimumSize(self.width(), 25)
        self.menubar.setMaximumSize(self.width(), 25)
        self.menubar.setBaseSize(self.width(), 25)
        self.menuProfile = QtGui.QMenu(self.menubar)
        self.menuProfile.setObjectName("menuProfile")
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.actionAdd_friend = QtGui.QAction(MainWindow)
        self.actionAdd_friend.setObjectName("actionAdd_friend")
        self.actionProfile_settings = QtGui.QAction(MainWindow)
        self.actionProfile_settings.setObjectName("actionProfile_settings")
        self.actionPrivacy_settings = QtGui.QAction(MainWindow)
        self.actionPrivacy_settings.setObjectName("actionPrivacy_settings")
        self.actionInterface_settings = QtGui.QAction(MainWindow)
        self.actionInterface_settings.setObjectName("actionInterface_settings")
        self.actionNotifications = QtGui.QAction(MainWindow)
        self.actionNotifications.setObjectName("actionNotifications")
        self.actionNetwork = QtGui.QAction(MainWindow)
        self.actionNetwork.setObjectName("actionNetwork")
        self.actionAbout_program = QtGui.QAction(MainWindow)
        self.actionAbout_program.setObjectName("actionAbout_program")
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.menuProfile.addAction(self.actionAdd_friend)
        self.menuProfile.addAction(self.actionSettings)
        self.menuSettings.addAction(self.actionPrivacy_settings)
        self.menuSettings.addAction(self.actionInterface_settings)
        self.menuSettings.addAction(self.actionNotifications)
        self.menuSettings.addAction(self.actionNetwork)
        self.menuAbout.addAction(self.actionAbout_program)
        self.menubar.addAction(self.menuProfile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.actionAbout_program.triggered.connect(self.about_program)
        self.actionNetwork.triggered.connect(self.network_settings)
        self.actionAdd_friend.triggered.connect(self.add_contact)
        self.actionSettings.triggered.connect(self.profile_settings)
        self.actionPrivacy_settings.triggered.connect(self.privacy_settings)
        self.actionInterface_settings.triggered.connect(self.interface_settings)
        self.actionNotifications.triggered.connect(self.notification_settings)

        self.menuProfile.setTitle(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.menuSettings.setTitle(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAbout.setTitle(QtGui.QApplication.translate("MainWindow", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAdd_friend.setText(QtGui.QApplication.translate("MainWindow", "Add contact", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProfile_settings.setText(QtGui.QApplication.translate("MainWindow", "Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPrivacy_settings.setText(QtGui.QApplication.translate("MainWindow", "Privacy", None, QtGui.QApplication.UnicodeUTF8))
        self.actionInterface_settings.setText(QtGui.QApplication.translate("MainWindow", "Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNotifications.setText(QtGui.QApplication.translate("MainWindow", "Notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNetwork.setText(QtGui.QApplication.translate("MainWindow", "Network", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_program.setText(QtGui.QApplication.translate("MainWindow", "About program", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSettings.setText(QtGui.QApplication.translate("MainWindow", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setup_right_bottom(self, Form):
        Form.setObjectName("right_bottom")
        Form.resize(500, 150)
        Form.setMinimumSize(QtCore.QSize(100, 50))
        self.messageEdit = QtGui.QTextEdit(Form)
        self.messageEdit.setGeometry(QtCore.QRect(20, 20, 311, 111))
        self.messageEdit.setObjectName("messageEdit")
        self.screenshotButton = QtGui.QPushButton(Form)
        self.screenshotButton.setGeometry(QtCore.QRect(340, 10, 98, 61))
        self.screenshotButton.setObjectName("screenshotButton")
        self.fileTransferButton = QtGui.QPushButton(Form)
        self.fileTransferButton.setGeometry(QtCore.QRect(340, 80, 98, 61))
        self.fileTransferButton.setObjectName("fileTransferButton")
        self.sendMessageButton = QtGui.QPushButton(Form)
        self.sendMessageButton.setGeometry(QtCore.QRect(440, 10, 51, 131))
        self.sendMessageButton.setObjectName("sendMessageButton")
        self.screenshotButton.setText(QtGui.QApplication.translate("Form", "Screenshot", None, QtGui.QApplication.UnicodeUTF8))
        self.fileTransferButton.setText(QtGui.QApplication.translate("Form", "File transfer", None, QtGui.QApplication.UnicodeUTF8))
        self.sendMessageButton.setText(QtGui.QApplication.translate("Form", "Send", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_center(self, Form):
        Form.setObjectName("left_center")
        Form.resize(500, 80)
        self.online_contacts = QtGui.QCheckBox(Form)
        self.online_contacts.setGeometry(QtCore.QRect(0, 20, 141, 22))
        self.online_contacts.setObjectName("online_contacts")
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(0, 40, 140, 28))
        self.lineEdit.setObjectName("lineEdit")
        self.online_contacts.setText(QtGui.QApplication.translate("Form", "Online contacts", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QMetaObject.connectSlotsByName(Form)

    def setup_left_top(self, Form):
        Form.setObjectName("left_top")
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
        self.name = QtGui.QLabel(Form)
        self.name.setGeometry(QtCore.QRect(80, 30, 191, 25))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(True)
        self.name.setFont(font)
        self.name.setObjectName("name")
        self.status_message = QtGui.QLabel(Form)
        self.status_message.setGeometry(QtCore.QRect(80, 60, 191, 17))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        font.setBold(False)
        self.status_message.setFont(font)
        self.status_message.setObjectName("status_message")
        self.connection_status = StatusCircle(self)
        self.connection_status.setGeometry(QtCore.QRect(200, 34, 64, 64))
        self.connection_status.setMinimumSize(QtCore.QSize(32, 32))
        self.connection_status.setMaximumSize(QtCore.QSize(32, 32))
        self.connection_status.setBaseSize(QtCore.QSize(32, 32))
        self.connection_status.setObjectName("connection_status")

    def setup_right_top(self, Form):
        Form.setObjectName("Form")
        Form.resize(495, 111)
        self.graphicsView = QtGui.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(10, 20, 64, 64))
        self.graphicsView.setObjectName("graphicsView")
        self.account_name = QtGui.QLabel(Form)
        self.account_name.setGeometry(QtCore.QRect(100, 20, 211, 17))
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.account_name.setFont(font)
        self.account_name.setObjectName("account_name")
        self.account_status = QtGui.QLabel(Form)
        self.account_status.setGeometry(QtCore.QRect(100, 50, 211, 17))
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.account_status.setFont(font)
        self.account_status.setObjectName("account_status")
        self.callButton = QtGui.QPushButton(Form)
        self.callButton.setGeometry(QtCore.QRect(380, 30, 98, 27))
        self.callButton.setObjectName("callButton")
        self.account_name.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.account_status.setText(QtGui.QApplication.translate("Form", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.callButton.setText(QtGui.QApplication.translate("Form", "Start call", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QMetaObject.connectSlotsByName(Form)

    def initUI(self):
        main = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        search = QtGui.QWidget()
        grid.setColumnStretch(1, 1)
        self.setup_left_center(search)
        grid.addWidget(search, 1, 0)
        name = QtGui.QWidget()
        self.setup_left_top(name)
        grid.addWidget(name, 0, 0)
        info = QtGui.QWidget()
        self.setup_right_top(info)
        grid.addWidget(info, 0, 1)
        message = QtGui.QWidget()
        self.setup_right_bottom(message)
        grid.addWidget(message, 2, 1)
        main.setLayout(grid)
        self.setCentralWidget(main)
        self.setup_menu(self)
        self.setMinimumSize(800, 400)
        self.setGeometry(400, 400, 800, 400)
        self.setWindowTitle('Toxygen')

    def mouseReleaseEvent(self, event):
        pass
        # if self.connection_status.status != TOX_USER_CONNECTION_STATUS['OFFLINE']:
        #     self.connection_status.status += 1
        #     self.connection_status.status %= TOX_USER_CONNECTION_STATUS['OFFLINE']
        #     self.tox.self_set_status(self.connection_status.status)
        #     self.connection_status.repaint()

    def setup_info_from_tox(self):
        self.name.setText(self.tox.self_get_name())
        self.status_message.setText(self.tox.self_get_status_message())

    # -----------------------------------------------------------------------------------------------------------------
    # Functions which called when user click in menu
    # -----------------------------------------------------------------------------------------------------------------

    def about_program(self):
        import util
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle("About")
        msgBox.setText("Toxygen is pythonic Tox client. Version: " + util.program_version)
        msgBox.exec_()

    def network_settings(self):
        self.n_s = NetworkSettings()
        self.n_s.show()

    def add_contact(self):
        self.a_c = AddContact()
        self.a_c.show()

    def profile_settings(self):
        self.p_s = ProfileSettings()
        self.p_s.show()

    def privacy_settings(self):
        self.priv_s = PrivacySettings()
        self.priv_s.show()

    def notification_settings(self):
        self.notif_s = NotificationsSettings()
        self.notif_s.show()

    def interface_settings(self):
        self.int_s = InterfaceSettings()
        self.int_s.show()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
