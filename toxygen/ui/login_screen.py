from ui.widgets import *
from PyQt5 import uic
import utils.util as util
import utils.ui as util_ui
import os.path


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
        uic.loadUi(util.get_views_path('login_screen'), self)
        self.center()
        self._profiles = []
        self._update_ui()

    def update_select(self, profiles):
        profiles = sorted(profiles, key=lambda p: p[1])
        self._profiles = list(profiles)
        self.profilesComboBox.addItems(list(map(lambda p: p[1], profiles)))
        self.loadProfilePushButton.setEnabled(len(profiles) > 0)

    def _update_ui(self):
        self.profileNameLineEdit = LineEditWithEnterSupport(self._create_profile, self)
        self.profileNameLineEdit.setGeometry(QtCore.QRect(20, 100, 170, 30))
        self._retranslate_ui()
        self.createProfilePushButton.clicked.connect(self._create_profile)
        self.loadProfilePushButton.clicked.connect(self._load_existing_profile)

    def _create_profile(self):
        path = self.profileNameLineEdit.text()
        load_as_default = self.defaultProfileCheckBox.isChecked()
        result = LoginScreenResult(path, load_as_default)
        self.close_with_result(result)

    def _load_existing_profile(self):
        index = self.profilesComboBox.currentIndex()
        load_as_default = self.defaultProfileCheckBox.isChecked()
        path = util.join_path(self._profiles[index][0], self._profiles[index][1] + '.tox')
        result = LoginScreenResult(path, load_as_default)
        self.close_with_result(result)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Log in'))
        self.profileNameLineEdit.setPlaceholderText(util_ui.tr('Profile name'))
        self.createProfilePushButton.setText(util_ui.tr('Create'))
        self.loadProfilePushButton.setText(util_ui.tr('Load profile'))
        self.defaultProfileCheckBox.setText(util_ui.tr('Use as default'))
        self.existingProfileGroupBox.setTitle(util_ui.tr('Load existing profile'))
        self.newProfileGroupBox.setTitle(util_ui.tr('Create new profile'))
