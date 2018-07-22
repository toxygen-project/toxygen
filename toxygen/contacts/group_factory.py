from contacts.group_chat import GroupChat
from common.tox_save import ToxSave
import wrapper.toxcore_enums_and_consts as constants


class GroupFactory(ToxSave):

    def __init__(self, profile_manager, settings, tox, db, items_factory):
        super().__init__(tox)
        self._profile_manager = profile_manager
        self._settings = settings
        self._db = db
        self._items_factory = items_factory

    def create_group_by_public_key(self, public_key):
        group_number = self._get_group_number_by_chat_id(public_key)

        return self.create_group_by_number(group_number)

    def create_group_by_number(self, group_number):
        aliases = self._settings['friends_aliases']
        tox_id = self._tox.group_get_chat_id(group_number)
        try:
            alias = list(filter(lambda x: x[0] == tox_id, aliases))[0][1]
        except:
            alias = ''
        item = self._create_group_item()
        name = alias or self._tox.group_get_name(group_number) or tox_id
        status_message = self._tox.group_get_topic(group_number)
        message_getter = self._db.messages_getter(tox_id)
        is_private = self._tox.group_get_privacy_state() == constants.TOX_GROUP_PRIVACY_STATE['PRIVATE']
        group = GroupChat(self._tox, self._profile_manager, message_getter, group_number, name, status_message,
                          item, tox_id, is_private)
        group.set_alias(alias)

        return group

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _create_group_item(self):
        """
        Method-factory
        :return: new widget for group instance
        """
        return self._items_factory.create_contact_item()

    def _get_group_number_by_chat_id(self, chat_id):
        for i in range(self._tox.group_get_number_groups()):
            if self._tox.group_get_chat_id(i) == chat_id:
                return i
        return -1
