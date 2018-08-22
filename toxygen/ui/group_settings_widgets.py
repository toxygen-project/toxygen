from ui.widgets import CenteredWidget
from PyQt5 import uic
import utils.util as util
import utils.ui as util_ui


class GroupManagementScreen(CenteredWidget):

    def __init__(self, groups_service, group):
        super().__init__()
        self._groups_service = groups_service
        self._group = group

        uic.loadUi(util.get_views_path('group_management_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self.passwordLineEdit.setText(self._group.password)
        self.privacyStateComboBox.setCurrentIndex(1 if self._group.is_private else 0)
        self.peersLimitSpinBox.setValue(self._group.peers_limit)

        self.savePushButton.clicked.connect(self._save)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Group "{}"').format(self._group.name))
        self.passwordLabel.setText(util_ui.tr('Password:'))
        self.peerLimitLabel.setText(util_ui.tr('Peer limit:'))
        self.privacyStateLabel.setText(util_ui.tr('Privacy state:'))
        self.savePushButton.setText(util_ui.tr('Save'))

        self.privacyStateComboBox.clear()
        self.privacyStateComboBox.addItem(util_ui.tr('Public'))
        self.privacyStateComboBox.addItem(util_ui.tr('Private'))

    def _save(self):
        password = self.passwordLineEdit.text()
        privacy_state = self.privacyStateComboBox.currentIndex()
        peers_limit = self.peersLimitSpinBox.value()

        self._groups_service.set_group_password(self._group, password)
        self._groups_service.set_group_privacy_state(self._group, privacy_state)
        self._groups_service.set_group_peers_limit(self._group, peers_limit)

        self.close()


class GroupSettingsScreen(CenteredWidget):

    def __init__(self, group):
        super().__init__()
        self._group = group

        uic.loadUi(util.get_views_path('gc_settings_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self._retranslate_ui()

        self.copyPasswordPushButton.clicked.connect(self._copy_password)
        self.copyPasswordPushButton.setEnabled(bool(self._group.password))

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Group "{}"').format(self._group.name))
        if self._group.password:
            password_label_text = '{} {}'.format(util_ui.tr('Password:'), self._group.password)
        else:
            password_label_text = util_ui.tr('Password is not set')
        self.passwordLabel.setText(password_label_text)
        self.peerLimitLabel.setText('{} {}'.format(util_ui.tr('Peer limit:'), self._group.peers_limit))
        privacy_state = util_ui.tr('Private') if self._group.is_private else util_ui.tr('Public')
        self.privacyStateLabel.setText('{} {}'.format(util_ui.tr('Privacy state:'), privacy_state))
        self.copyPasswordPushButton.setText(util_ui.tr('Copy password'))

    def _copy_password(self):
        util_ui.copy_to_clipboard(self._group.password)
