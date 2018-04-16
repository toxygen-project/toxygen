from ui.widgets import *
import os.path


class NickEdit(LineEdit):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.parent.create_profile()
        else:
            super(NickEdit, self).keyPressEvent(event)


class LoginScreenResult:

    def __init__(self, profile_path, load_as_default, password=None):
        self._profile_path = profile_path
        self._load_as_default = load_as_default
        self._password = password

    def get_profile_path(self):
        return self._profile_path

    profile_path = property(get_profile_path)

    def get_load_as_default(self):
        return self._load_as_default

    load_as_default = property(get_load_as_default)

    def get_password(self):
        return self._password

    password = property(get_password)

    def is_new_profile(self):
        return not os.path.isfile(self._profile_path)


class LoginScreen(CenteredWidget, DialogWithResult):

    def __init__(self):
        CenteredWidget.__init__(self)
        DialogWithResult.__init__(self)
        self.initUI()
        self.center()
        self._profiles = []

    def initUI(self):
        self.resize(400, 200)
        self.setMinimumSize(QtCore.QSize(400, 200))
        self.setMaximumSize(QtCore.QSize(400, 200))
        self.new_profile = QtWidgets.QPushButton(self)
        self.new_profile.setGeometry(QtCore.QRect(20, 150, 171, 27))
        self.new_profile.clicked.connect(self.create_profile)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(20, 70, 101, 17))
        self.new_name = NickEdit(self)
        self.new_name.setGeometry(QtCore.QRect(20, 100, 171, 31))
        self.load_profile = QtWidgets.QPushButton(self)
        self.load_profile.setGeometry(QtCore.QRect(220, 150, 161, 27))
        self.load_profile.clicked.connect(self.load_existing_profile)
        self.default = QtWidgets.QCheckBox(self)
        self.default.setGeometry(QtCore.QRect(220, 110, 131, 22))
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(210, 40, 181, 151))
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(10, 30, 161, 27))
        self.groupBox_2 = QtWidgets.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 40, 191, 151))
        self.toxygen = QtWidgets.QLabel(self)
        self.toxygen.setGeometry(QtCore.QRect(160, 8, 90, 25))
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.comboBox.raise_()
        self.default.raise_()
        self.load_profile.raise_()
        self.new_name.raise_()
        self.new_profile.raise_()
        font = QtGui.QFont()
        font.setFamily("Impact")
        font.setPointSize(16)
        self.toxygen.setFont(font)
        self.toxygen.setObjectName("toxygen")
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.new_name.setPlaceholderText(QtWidgets.QApplication.translate("login", "Profile name"))
        self.setWindowTitle(QtWidgets.QApplication.translate("login", "Log in"))
        self.new_profile.setText(QtWidgets.QApplication.translate("login", "Create"))
        self.label.setText(QtWidgets.QApplication.translate("login", "Profile name:"))
        self.load_profile.setText(QtWidgets.QApplication.translate("login", "Load profile"))
        self.default.setText(QtWidgets.QApplication.translate("login", "Use as default"))
        self.groupBox.setTitle(QtWidgets.QApplication.translate("login", "Load existing profile"))
        self.groupBox_2.setTitle(QtWidgets.QApplication.translate("login", "Create new profile"))
        self.toxygen.setText(QtWidgets.QApplication.translate("login", "toxygen"))

    def create_profile(self):
        self.type = 1
        self.name = self.new_name.text()
        self.close()

    def load_existing_profile(self):
        index = self.comboBox.currentIndex()
        load_as_default = self.default.isChecked()
        path = os.path.join(self._profiles[index][0], self._profiles[index][1] + '.tox')
        result = LoginScreenResult(path, load_as_default)
        self.close_with_result(result)

    def update_select(self, profiles):
        profiles = sorted(profiles, key=lambda p: p[1])
        self._profiles = list(profiles)
        self.comboBox.addItems(list(map(lambda p: p[1], profiles)))
        self.load_profile.setEnabled(len(profiles) > 0)

