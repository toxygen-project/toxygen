import contact


class GroupChat(contact.Contact):

    def __init__(self, group_id, tox,  *args):
        super().__init__(*args)
        self._id = group_id
        self._tox = tox

    def load_avatar(self, default_path='group.png'):
        super().load_avatar(default_path)
