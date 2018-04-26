import util.util as util


class ContactProvider(util.ToxSave):

    def __init__(self, tox, friend_factory):
        super().__init__(tox)
        self._friend_factory = friend_factory
        self._cache = {}  # key - contact's public key, value - contact instance

    def get_friend_by_number(self, friend_number):
        public_key = self._tox.friend_get_public_key(friend_number)

        return self.get_friend_by_public_key(public_key)

    def get_friend_by_public_key(self, public_key):
        friend = self._get_contact_from_cache(public_key)
        if friend is not None:
            return friend
        friend = self._friend_factory.create_friend_by_public_key(public_key)
        self._add_to_cache(public_key, friend)

        return friend

    def get_gc_by_number(self):
        pass

    def get_gc_by_public_key(self):
        pass

    def clear_cache(self):
        self._cache.clear()

    def _get_contact_from_cache(self, public_key):
        return self._cache[public_key] if public_key in self._cache else None

    def _add_to_cache(self, public_key, contact):
        self._cache[public_key] = contact
