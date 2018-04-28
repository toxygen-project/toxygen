import util.util as util


class ContactProvider(util.ToxSave):

    def __init__(self, tox, friend_factory):
        super().__init__(tox)
        self._friend_factory = friend_factory
        self._cache = {}  # key - contact's public key, value - contact instance

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _get_contact_from_cache(self, public_key):
        return self._cache[public_key] if public_key in self._cache else None

    def _add_to_cache(self, public_key, contact):
        self._cache[public_key] = contact

    # -----------------------------------------------------------------------------------------------------------------
    # Friends
    # -----------------------------------------------------------------------------------------------------------------

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

    def get_all_friends(self):
        friend_numbers = self._tox.self_get_friend_list()
        friends = map(lambda n: self.get_friend_by_number(n), friend_numbers)

        return list(friends)

    # -----------------------------------------------------------------------------------------------------------------
    # GC
    # -----------------------------------------------------------------------------------------------------------------

    def get_all_gc(self):
        return []

    def get_gc_by_number(self):
        pass

    def get_gc_by_public_key(self):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # All contacts
    # -----------------------------------------------------------------------------------------------------------------

    def get_all(self):
        return self.get_all_friends() + self.get_all_gc()

    # -----------------------------------------------------------------------------------------------------------------
    # Caching
    # -----------------------------------------------------------------------------------------------------------------

    def clear_cache(self):
        self._cache.clear()

    def remove_friend_from_cache(self, friend_public_key):
        if friend_public_key in self._cache:
            del self._cache[friend_public_key]
