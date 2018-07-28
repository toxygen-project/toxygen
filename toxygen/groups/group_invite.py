

class GroupInvite:

    def __init__(self, friend_public_key, chat_name, invite_data):
        self._friend_public_key = friend_public_key
        self._chat_name = chat_name
        self._invite_data = invite_data[:]

    def get_friend_public_key(self):
        return self._friend_public_key

    friend_public_key = property(get_friend_public_key)

    def get_chat_name(self):
        return self._chat_name

    chat_name = property(get_chat_name)

    def get_invite_data(self):
        return self._invite_data[:]

    invite_data = property(get_invite_data)
