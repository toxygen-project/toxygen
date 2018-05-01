

class BaseTypingNotificationHandler:

    DEFAULT_HANDLER = None

    def __init__(self):
        pass

    def send(self, tox, is_typing):
        pass


class FriendTypingNotificationHandler(BaseTypingNotificationHandler):

    def __init__(self, friend_number):
        super().__init__()
        self._friend_number = friend_number

    def send(self, tox, is_typing):
        tox.self_set_typing(self._friend_number, is_typing)


BaseTypingNotificationHandler.DEFAULT_HANDLER = BaseTypingNotificationHandler()
