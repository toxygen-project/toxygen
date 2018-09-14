from ui.widgets import CenteredWidget
import utils.ui as util_ui
from utils.util import join_path, get_images_directory, get_views_path
from user_data.settings import Settings
from PyQt5 import QtGui, QtCore, uic


class ProfileSettings(CenteredWidget):
    """Form with profile settings such as name, status, TOX ID"""
    def __init__(self, profile, profile_manager, settings, toxes):
        super().__init__()
        self._profile = profile
        self._profile_manager = profile_manager
        self._settings = settings
        self._toxes = toxes
        self._auto = False

        uic.loadUi(get_views_path('profile_settings_screen'), self)

        self._init_ui()
        self.center()

    def closeEvent(self, event):
        self._profile.set_name(self.nameLineEdit.text())
        self._profile.set_status_message(self.statusMessageLineEdit.text())
        self._profile.set_status(self.statusComboBox.currentIndex())

    def _init_ui(self):
        self._auto = Settings.get_auto_profile() == self._profile_manager.get_path()
        self.toxIdLabel.setText(self._profile.tox_id)
        self.nameLineEdit.setText(self._profile.name)
        self.statusMessageLineEdit.setText(self._profile.status_message)
        self.defaultProfilePushButton.clicked.connect(self._toggle_auto_profile)
        self.copyToxIdPushButton.clicked.connect(self._copy_tox_id)
        self.copyPublicKeyPushButton.clicked.connect(self._copy_public_key)
        self.changePasswordPushButton.clicked.connect(self._save_password)
        self.exportProfilePushButton.clicked.connect(self._export_profile)
        self.newNoSpamPushButton.clicked.connect(self._set_new_no_spam)
        self.newAvatarPushButton.clicked.connect(self._set_avatar)
        self.resetAvatarPushButton.clicked.connect(self._reset_avatar)

        self.invalidPasswordsLabel.setVisible(False)

        self._retranslate_ui()

        if self._profile.status is not None:
            self.statusComboBox.setCurrentIndex(self._profile.status)
        else:
            self.statusComboBox.setVisible(False)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr("Profile settings"))

        self.exportProfilePushButton.setText(util_ui.tr("Export profile"))
        self.nameLabel.setText(util_ui.tr("Name:"))
        self.statusLabel.setText(util_ui.tr("Status:"))
        self.toxIdTitleLabel.setText(util_ui.tr("TOX ID:"))
        self.copyToxIdPushButton.setText(util_ui.tr("Copy TOX ID"))
        self.newAvatarPushButton.setText(util_ui.tr("New avatar"))
        self.resetAvatarPushButton.setText(util_ui.tr("Reset avatar"))
        self.newNoSpamPushButton.setText(util_ui.tr("New NoSpam"))
        self.profilePasswordLabel.setText(util_ui.tr("Profile password"))
        self.passwordLineEdit.setPlaceholderText(util_ui.tr("Password (at least 8 symbols)"))
        self.confirmPasswordLineEdit.setPlaceholderText(util_ui.tr("Confirm password"))
        self.changePasswordPushButton.setText(util_ui.tr("Set password"))
        self.invalidPasswordsLabel.setText(util_ui.tr("Passwords do not match"))
        self.emptyPasswordLabel.setText(util_ui.tr("Leaving blank will reset current password"))
        self.warningLabel.setText(util_ui.tr("There is no way to recover lost passwords"))
        self.statusComboBox.addItem(util_ui.tr("Online"))
        self.statusComboBox.addItem(util_ui.tr("Away"))
        self.statusComboBox.addItem(util_ui.tr("Busy"))
        self.copyPublicKeyPushButton.setText(util_ui.tr("Copy public key"))

        self._set_default_profile_button_text()

    def _toggle_auto_profile(self):
        if self._auto:
            Settings.reset_auto_profile()
        else:
            Settings.set_auto_profile(self._profile_manager.get_path())
        self._auto = not self._auto
        self._set_default_profile_button_text()

    def _set_default_profile_button_text(self):
        if self._auto:
            self.defaultProfilePushButton.setText(util_ui.tr("Mark as not default profile"))
        else:
            self.defaultProfilePushButton.setText(util_ui.tr("Mark as default profile"))

    def _save_password(self):
        password = self.passwordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()
        if password == confirm_password:
            if not len(password) or len(password) >= 8:
                self._toxes.set_password(password)
                self.close()
            else:
                self.invalidPasswordsLabel.setText(
                    util_ui.tr("Password must be at least 8 symbols"))
            self.invalidPasswordsLabel.setVisible(True)
        else:
            self.invalidPasswordsLabel.setText(util_ui.tr("Passwords do not match"))
            self.invalidPasswordsLabel.setVisible(True)

    def _copy_tox_id(self):
        util_ui.copy_to_clipboard(self._profile.tox_id)

        icon = self._get_accept_icon()
        self.copyToxIdPushButton.setIcon(icon)
        self.copyToxIdPushButton.setIconSize(QtCore.QSize(10, 10))

    def _copy_public_key(self):
        util_ui.copy_to_clipboard(self._profile.tox_id[:64])

        icon = self._get_accept_icon()
        self.copyPublicKeyPushButton.setIcon(icon)
        self.copyPublicKeyPushButton.setIconSize(QtCore.QSize(10, 10))

    def _set_new_no_spam(self):
        self.toxIdLabel.setText(self._profile.set_new_nospam())

    def _reset_avatar(self):
        self._profile.reset_avatar(self._settings['identicons'])

    def _set_avatar(self):
        choose = util_ui.tr("Choose avatar")
        name = util_ui.file_dialog(choose, 'Images (*.png)')
        if not name[0]:
            return
        bitmap = QtGui.QPixmap(name[0])
        bitmap.scaled(QtCore.QSize(128, 128), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        byte_array = QtCore.QByteArray()
        buffer = QtCore.QBuffer(byte_array)
        buffer.open(QtCore.QIODevice.WriteOnly)
        bitmap.save(buffer, 'PNG')

        self._profile.set_avatar(bytes(byte_array.data()))

    def _export_profile(self):
        directory = util_ui.directory_dialog()
        if not directory:
            return

        reply = util_ui.question(util_ui.tr('Do you want to move your profile to this location?'),
                                 util_ui.tr('Use new path'))
        
        self._settings.export(directory)
        self._profile.export_db(directory)
        self._profile_manager.export_profile(self._settings, directory, reply)

    @staticmethod
    def _get_accept_icon():
        pixmap = QtGui.QPixmap(join_path(get_images_directory(), 'accept.png'))

        return QtGui.QIcon(pixmap)

