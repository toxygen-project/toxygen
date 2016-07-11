import contact


class GroupChat(contact.Contact):

    def __init__(self, tox, *args):
        super().__init__(*args)
        self._tox = tox

    def load_avatar(self, default_path='group.png'):
        super().load_avatar(default_path)

# TODO: get peers list and add other methods
