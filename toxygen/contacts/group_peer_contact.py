import contacts.contact
from contacts.contact_menu import GroupPeerMenuGenerator


class GroupPeerContact(contacts.contact.Contact):

    def __init__(self, profile_manager, message_getter, peer_number, name, widget, tox_id, group_pk):
        super().__init__(profile_manager, message_getter, peer_number, name, str(), widget, tox_id)
        self._group_pk = group_pk

    def get_group_pk(self):
        return self._group_pk

    group_pk = property(get_group_pk)

    def remove_invalid_unsent_files(self):
        pass

    def get_context_menu_generator(self):
        return GroupPeerMenuGenerator(self)
