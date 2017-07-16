import contact


class GroupChat(contact.Contact):

    def __init__(self, name, status_message, widget, tox, group_number):
        super().__init__(None, group_number, name, status_message, widget, None)
        self._tox = tox

    def set_name(self, name):
        self._tox.group_set_title(self._number, name)
        super().set_name(name)

    def send_message(self, message):
        self._tox.group_message_send(self._number, message.encode('utf-8'))

    def new_title(self, title):
        super().set_name(title)
