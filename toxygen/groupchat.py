import contact


class GroupChat(contact.Contact):

    def __init__(self, tox, *args):
        super().__init__(*args)
        self._tox = tox

    def load_avatar(self, default_path='group.png'):
        super().load_avatar(default_path)

    def set_status(self, value):
        print('In gc set_status')
        super().set_status(value)
        self.name = bytes(self._tox.group_get_name(self._number), 'utf-8')
        self._tox_id = self._tox.group_get_chat_id(self._number)
        self.status_message = bytes(self._tox.group_get_topic(self._number), 'utf-8')

    def add_peer(self, peer_id):
        print(peer_id)
        print(self._tox.group_peer_get_name(self._number, peer_id))

    # TODO: get peers list and add other methods

    def get_peers_list(self):
        return []


class Peer:

    def __init__(self, peer_id, name, status, role):
        self._data = (peer_id, name, status, role)

    def get_data(self):
        return self._data
