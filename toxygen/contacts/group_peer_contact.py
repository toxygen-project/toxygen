import contacts.contact


class GroupPeerContact(contacts.contact.Contact):

    def __init__(self, message_getter, peer_number, name, status_messsage, widget, tox_id, group_pk):
        super().__init__(message_getter, peer_number, name, status_messsage, widget, tox_id)
        self._group_pk = group_pk

    def get_group_pk(self):
        return self._group_pk

    group_pk = property(get_group_pk)
