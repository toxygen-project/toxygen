from ui.widgets import CenteredWidget
from PyQt5 import uic
import utils.util as util
import utils.ui as util_ui
from ui.contact_items import *
import wrapper.toxcore_enums_and_consts as consts


class PeerScreen(CenteredWidget):

    def __init__(self, contacts_manager, groups_service, group, peer_id):
        super().__init__()
        self._contacts_manager = contacts_manager
        self._groups_service = groups_service
        self._group = group
        self._peer = group.get_peer_by_id(peer_id)

        self._roles = {
            TOX_GROUP_ROLE['FOUNDER']: util_ui.tr('Administrator'),
            TOX_GROUP_ROLE['MODERATOR']: util_ui.tr('Moderator'),
            TOX_GROUP_ROLE['USER']: util_ui.tr('User'),
            TOX_GROUP_ROLE['OBSERVER']: util_ui.tr('Observer')
        }

        uic.loadUi(util.get_views_path('peer_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self.statusCircle = StatusCircle(self)
        self.statusCircle.setGeometry(50, 15, 30, 30)

        self.statusCircle.update(self._peer.status)
        self.peerNameLabel.setText(self._peer.name)
        self.ignorePeerCheckBox.setChecked(self._peer.is_muted)
        self.ignorePeerCheckBox.clicked.connect(self._toggle_ignore)
        self.sendPrivateMessagePushButton.clicked.connect(self._send_private_message)
        self.copyPublicKeyPushButton.clicked.connect(self._copy_public_key)
        self.roleNameLabel.setText(self._get_role_name())
        can_change_role_or_ban = self._can_change_role_or_ban()
        self.rolesComboBox.setVisible(can_change_role_or_ban)
        self.roleNameLabel.setVisible(not can_change_role_or_ban)
        self.banGroupBox.setEnabled(can_change_role_or_ban)
        self.banPushButton.clicked.connect(self._ban_peer)
        self.kickPushButton.clicked.connect(self._kick_peer)

        self._retranslate_ui()

        self.rolesComboBox.currentIndexChanged.connect(self._role_set)

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Peer details'))
        self.ignorePeerCheckBox.setText(util_ui.tr('Ignore peer'))
        self.roleLabel.setText(util_ui.tr('Role:'))
        self.copyPublicKeyPushButton.setText(util_ui.tr('Copy public key'))
        self.sendPrivateMessagePushButton.setText(util_ui.tr('Send private message'))
        self.banPushButton.setText(util_ui.tr('Ban peer'))
        self.kickPushButton.setText(util_ui.tr('Kick peer'))
        self.banGroupBox.setTitle(util_ui.tr('Ban peer'))
        self.ipBanRadioButton.setText(util_ui.tr('IP'))
        self.nickBanRadioButton.setText(util_ui.tr('Nickname'))
        self.pkBanRadioButton.setText(util_ui.tr('Public key'))

        self.rolesComboBox.clear()
        index = self._group.get_self_peer().role
        roles = list(self._roles.values())
        for role in roles[index + 1:]:
            self.rolesComboBox.addItem(role)
        self.rolesComboBox.setCurrentIndex(self._peer.role - index - 1)

    def _can_change_role_or_ban(self):
        self_peer = self._group.get_self_peer()
        if self_peer.role > TOX_GROUP_ROLE['MODERATOR']:
            return False

        return self_peer.role < self._peer.role

    def _role_set(self):
        index = self.rolesComboBox.currentIndex()
        all_roles_count = len(self._roles)
        diff = all_roles_count - self.rolesComboBox.count()
        self._groups_service.set_new_peer_role(self._group, self._peer, index + diff)

    def _get_role_name(self):
        return self._roles[self._peer.role]

    def _toggle_ignore(self):
        ignore = self.ignorePeerCheckBox.isChecked()
        self._groups_service.toggle_ignore_peer(self._group, self._peer, ignore)

    def _send_private_message(self):
        self._contacts_manager.add_group_peer(self._group, self._peer)
        self.close()

    def _copy_public_key(self):
        util_ui.copy_to_clipboard(self._peer.public_key)

    def _ban_peer(self):
        ban_type = self._get_ban_type()
        self._groups_service.ban_peer(self._group, self._peer.id, ban_type)
        self.close()

    def _kick_peer(self):
        self._groups_service.kick_peer(self._group, self._peer.id)
        self.close()

    def _get_ban_type(self):
        if self.ipBanRadioButton.isChecked():
            return consts.TOX_GROUP_BAN_TYPE['IP_PORT']
        elif self.nickBanRadioButton.isChecked():
            return consts.TOX_GROUP_BAN_TYPE['NICK']
        return consts.TOX_GROUP_BAN_TYPE['PUBLIC_KEY']
