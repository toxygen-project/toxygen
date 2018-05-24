from ui.widgets import *
from PyQt5 import uic
import utils.util as util
import utils.ui as util_ui


class CreateProfileScreenResult:

    def __init__(self, save_into_default_folder, password):
        self._save_into_default_folder = save_into_default_folder
        self._password = password

    def get_save_into_default_folder(self):
        return self._save_into_default_folder

    save_into_default_folder = property(get_save_into_default_folder)

    def get_password(self):
        return self._password

    password = property(get_password)


class CreateProfileScreen(CenteredWidget, DialogWithResult):

    def __init__(self):
        CenteredWidget.__init__(self)
        DialogWithResult.__init__(self)
        uic.loadUi(util.get_views_path('create_profile_screen'), self)
        self.center()
        self.createProfile.clicked.connect(self._create_profile)
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('New profile settings'))
        self.defaultFolder.setText(util_ui.tr('Save in default folder'))
        self.programFolder.setText(util_ui.tr('Save in program folder'))
        self.password.setPlaceholderText(util_ui.tr('Password'))
        self.confirmPassword.setPlaceholderText(util_ui.tr('Confirm password'))
        self.createProfile.setText(util_ui.tr('Create profile'))
        self.passwordLabel.setText(util_ui.tr('Password (at least 8 symbols):'))

    def _create_profile(self):
        password = self.password.text()
        if password != self.confirmPassword.text():
            self.errorLabel.setText(util_ui.tr('Passwords do not match'))
            return
        if 0 < len(password) < 8:
            self.errorLabel.setText(util_ui.tr('Password must be at least 8 symbols'))
            return
        result = CreateProfileScreenResult(self.defaultFolder.isChecked(), password)
        self.close_with_result(result)
