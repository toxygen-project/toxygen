from common.tox_save import ToxSave
from contacts.group_peer_contact import GroupPeerContact


class GroupPeerFactory(ToxSave):

    def __init__(self, tox, profile_manager, db, items_factory):
        super().__init__(tox)
        self._profile_manager = profile_manager
        self._db = db
        self._items_factory = items_factory

    def create_group_peer(self, group, peer):
        item = self._create_group_peer_item()
        message_getter = self._db.messages_getter(peer.public_key)
        group_peer_contact = GroupPeerContact(self._profile_manager, message_getter, peer.id, peer.name,
                                              item, peer.public_key, group.tox_id)
        group_peer_contact.status = peer.status

        return group_peer_contact

    def _create_group_peer_item(self):
        return self._items_factory.create_contact_item()
