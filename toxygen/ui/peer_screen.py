from ui.widgets import CenteredWidget
from PyQt5 import QtCore, QtWidgets, uic
import utils.util as util
import utils.ui as util_ui
from ui.contact_items import *


class PeerScreen(CenteredWidget):

    def __init__(self, contacts_manager, groups_service, group, peer_id):
        super().__init__()
        self._contacts_manager = contacts_manager
        self._groups_service = groups_service
        self._group = group
        self._peer = group.get_peer_by_id(peer_id)

        uic.loadUi(util.get_views_path('peer_screen'), self)
        self._update_ui()

    def _update_ui(self):
        self.statusCircle = StatusCircle(self)
        self.statusCircle.setGeometry(50, 20, 20, 20)
        self.statusCircle.update(self._peer.status)
        self.peerNameLabel.setText(self._peer.name)
        self.ignorePeerCheckBox.setChecked(self._peer.is_muted)
        self.sendPrivateMessagePushButton.clicked.connect(self._send_private_message)
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(util_ui.tr('Peer details'))
        self.ignorePeerCheckBox.setText(util_ui.tr('Ignore peer'))
        self.sendPrivateMessagePushButton.setText(util_ui.tr('Send private message'))

    def _send_private_message(self):
        self._contacts_manager.add_group_peer(self._group, self._peer)
        self.close()
