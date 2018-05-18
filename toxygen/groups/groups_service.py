import common.tox_save as tox_save


class GroupsService(tox_save.ToxSave):

    def __init__(self, tox, contacts_manager, contacts_provider):
        super().__init__(tox)
        self._contacts_manager = contacts_manager
        self._contacts_provider = contacts_provider

    # -----------------------------------------------------------------------------------------------------------------
    # Groups creation
    # -----------------------------------------------------------------------------------------------------------------

    def create_new_gc(self, name, privacy_state):
        group_number = self._tox.group_new(privacy_state, name)
        self._add_new_group_by_number(group_number)

    def join_gc_by_id(self, chat_id, password):
        group_number = self._tox.group_join(chat_id, password)
        self._add_new_group_by_number(group_number)

    def join_gc_via_invite(self, invite_data, friend_number, password):
        group_number = self._tox.group_invite_accept(invite_data, friend_number, password)
        self._add_new_group_by_number(group_number)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _add_new_group_by_number(self, group_number):
        self._contacts_manager.add_group(group_number)
