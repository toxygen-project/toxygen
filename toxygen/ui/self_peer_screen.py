from ui.widgets import CenteredWidget, LineEdit
from PyQt5 import QtCore, QtWidgets, uic
import utils.util as util
import utils.ui as util_ui
from ui.contact_items import *


class SelfPeerScreen(CenteredWidget):

    def __init__(self, contacts_manager, groups_service, group):
        super().__init__()
        self._contacts_manager = contacts_manager
        self._groups_service = groups_service
        self._group = group
        self._peer = group.get_self_peer()
        self._roles = {
            TOX_GROUP_ROLE['FOUNDER']: util_ui.tr('Administrator'),
            TOX_GROUP_ROLE['MODERATOR']: util_ui.tr('Moderator'),
            TOX_GROUP_ROLE['USER']: util_ui.tr('User'),
            TOX_GROUP_ROLE['OBSERVER']: util_ui.tr('Observer')
        }

        uic.loadUi(util.get_views_path('self_peer_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self.lineEdit = LineEdit(self)
        self.lineEdit.setGeometry(140, 40, 400, 30)
        self.lineEdit.setText(self._peer.name)
        self.lineEdit.textChanged.connect(self._nick_changed)

        self.savePushButton.clicked.connect(self._save)
        self.copyPublicKeyPushButton.clicked.connect(self._copy_public_key)

        self._retranslate_ui()

        self.statusComboBox.setCurrentIndex(self._peer.status)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Change credentials in group'))
        self.lineEdit.setPlaceholderText(util_ui.tr('Your nickname in group'))
        self.nameLabel.setText(util_ui.tr('Name:'))
        self.roleLabel.setText(util_ui.tr('Role:'))
        self.statusLabel.setText(util_ui.tr('Status:'))
        self.copyPublicKeyPushButton.setText(util_ui.tr('Copy public key'))
        self.savePushButton.setText(util_ui.tr('Save'))
        self.roleNameLabel.setText(self._get_role_name())
        self.statusComboBox.addItem(util_ui.tr('Online'))
        self.statusComboBox.addItem(util_ui.tr('Away'))
        self.statusComboBox.addItem(util_ui.tr('Busy'))

    def _get_role_name(self):
        return self._roles[self._peer.role]

    def _nick_changed(self):
        nick = self.lineEdit.text()
        self.savePushButton.setEnabled(bool(nick))

    def _save(self):
        nick = self.lineEdit.text()
        status = self.statusComboBox.currentIndex()
        self._groups_service.set_self_info(self._group, nick, status)
        self.close()

    def _copy_public_key(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self._peer.public_key)
