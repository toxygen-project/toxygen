from ui.widgets import *
from PyQt5 import uic
import util.util as util
import util.ui as util_ui


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
        uic.loadUi(util.get_views_path('create_profile_screen'))
        self.center()
        self.createProfile.clicked.connect(self.create_profile)

    def retranslateUi(self):
        self.defaultFolder.setPlaceholderText(util_ui.tr('Save in default folder'))
        self.programFolder.setPlaceholderText(util_ui.tr('Save in program folder'))
        self.createProfile.setText(util_ui.tr('Create profile'))
        self.passwordLabel.setText(util_ui.tr('Password:'))

    def create_profile(self):
        if self.password.text() != self.confirmPassword.text():
            return  # TODO : error
        result = CreateProfileScreenResult(self.defaultFolder.isChecked(), self.password.text())
        self.close_with_result(result)
