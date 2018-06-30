from contacts.friend import Friend
from common.tox_save import ToxSave


class FriendFactory(ToxSave):

    def __init__(self, settings, tox, db, items_factory):
        super().__init__(tox)
        self._settings = settings
        self._db = db
        self._items_factory = items_factory

    def create_friend_by_public_key(self, public_key):
        friend_number = self._tox.friend_by_public_key(public_key)

        return self.create_friend_by_number(friend_number)

    def create_friend_by_number(self, friend_number):
        aliases = self._settings['friends_aliases']
        tox_id = self._tox.friend_get_public_key(friend_number)
        try:
            alias = list(filter(lambda x: x[0] == tox_id, aliases))[0][1]
        except:
            alias = ''
        item = self._create_friend_item()
        name = alias or self._tox.friend_get_name(friend_number) or tox_id
        status_message = self._tox.friend_get_status_message(friend_number)
        message_getter = self._db.messages_getter(tox_id)
        friend = Friend(message_getter, friend_number, name, status_message, item, tox_id)
        friend.set_alias(alias)

        return friend

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _create_friend_item(self):
        """
        Method-factory
        :return: new widget for friend instance
        """
        return self._items_factory.create_contact_item()
