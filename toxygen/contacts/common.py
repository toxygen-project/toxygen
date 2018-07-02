from pydenticon import Generator


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


def generate_avatar(public_key):
    foreground = ['rgb(45,79,255)', 'rgb(185, 66, 244)', 'rgb(185, 66, 244)',
                  'rgb(254,180,44)', 'rgb(252, 2, 2)', 'rgb(109, 198, 0)',
                  'rgb(226,121,234)', 'rgb(130, 135, 124)',
                  'rgb(30,179,253)', 'rgb(160, 157, 0)',
                  'rgb(232,77,65)', 'rgb(102, 4, 4)',
                  'rgb(49,203,115)',
                  'rgb(141,69,170)']
    generator = Generator(5, 5, foreground=foreground, background='rgba(42,42,42,0)')
    identicon = generator.generate(public_key, 220, 220, padding=(10, 10, 10, 10))

    return identicon
