import contact


class Groupchat(contact.Contact):

    def __init__(self, group_id, *args):
        super().__init__(args)
        self._id = group_id

    def load_avatar(self):
        super().load_avatar('group.png')
