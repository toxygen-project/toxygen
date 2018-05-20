from PyQt5 import QtWidgets, QtCore
from ui.group_peers_list import PeerItem, PeerTypeItem
import utils.ui as util_ui
from wrapper.toxcore_enums_and_consts import *

# -----------------------------------------------------------------------------------------------------------------
# Builder
# -----------------------------------------------------------------------------------------------------------------


class PeerListBuilder:

    def __init__(self):
        self._peers = {}
        self._titles = {}
        self._index = 0
        self._handler = None

    def with_click_handler(self, handler):
        self._handler = handler

        return self

    def with_title(self, title):
        self._titles[self._index] = title
        self._index += 1

        return self

    def with_peers(self, peers):
        for peer in peers:
            self._add_peer(peer)

        return self

    def build(self, parent):
        parent.clear()

        for i in range(self._index):
            if i in self._peers:
                peer = self._peers[i]
                self._add_peer_item(peer, parent)
            else:
                title = self._titles[i]
                self._add_peer_type_item(title, parent)

        return parent

    def _add_peer_item(self, peer, parent):
        item = PeerItem(peer, self._handler, parent.width())
        self._add_item(parent, item)

    def _add_peer_type_item(self, text, parent):
        item = PeerTypeItem(text, parent.width())
        self._add_item(parent, item)

    @staticmethod
    def _add_item(parent, item):
        elem = QtWidgets.QListWidgetItem()
        elem.setSizeHint(QtCore.QSize(parent.width(), item.height()))
        parent.addItem(elem)
        parent.setItemWidget(elem, item)

    def _add_peer(self, peer):
        self._peers[self._index] = peer
        self._index += 1

# -----------------------------------------------------------------------------------------------------------------
# Generators
# -----------------------------------------------------------------------------------------------------------------


class PeersListGenerator:

    @staticmethod
    def generate(peers_list, groups_service, parent, chat_id):
        admin_title = util_ui.tr('Administrator')
        moderators_title = util_ui.tr('Moderators')
        users_title = util_ui.tr('Users')
        observers_title = util_ui.tr('Observers')

        admins = list(filter(lambda p: p.role == TOX_GROUP_ROLE['FOUNDER'], peers_list))
        moderators = list(filter(lambda p: p.role == TOX_GROUP_ROLE['MODERATOR'], peers_list))
        users = list(filter(lambda p: p.role == TOX_GROUP_ROLE['USER'], peers_list))
        observers = list(filter(lambda p: p.role == TOX_GROUP_ROLE['OBSERVER'], peers_list))

        builder = (PeerListBuilder()
                   .with_click_handler(lambda peer_id: groups_service.peer_selected(chat_id, peer_id))
                   .with_title(admin_title)
                   .with_peers(admins)
                   .with_title(moderators_title)
                   .with_peers(moderators)
                   .with_title(users_title)
                   .with_peers(users)
                   .with_title(observers_title)
                   .with_peers(observers)
                   )

        return builder.build(parent)
