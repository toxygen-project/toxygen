from contacts import contact
import utils.util as util
from wrapper.toxcore_enums_and_consts import *
from wrapper import toxcore_enums_and_consts as constants


class GroupChat(contact.Contact):

    def __init__(self, profile_manager, name, status_message, widget, tox, group_number):
        super().__init__(None, group_number, profile_manager, name, status_message, widget, None)
        self._tox = tox
        self.set_status(constants.TOX_USER_STATUS['NONE'])
        self._peers = []
        self._add_self_to_gc()

    def set_topic(self, topic):
        self._tox.group_set_topic(self._number, topic.encode('utf-8'))
        super().set_status_message(topic)

    def remove_invalid_unsent_files(self):
        pass

    def get_names(self):
        peers_count = self._tox.group_number_peers(self._number)
        names = []
        for i in range(peers_count):
            name = self._tox.group_peername(self._number, i)
            names.append(name)
        names = sorted(names, key=lambda n: n.lower())
        return names

    def get_full_status(self):
        names = self.get_names()
        return '\n'.join(names)

    def get_peer_name(self, peer_number):
        return self._tox.group_peername(self._number, peer_number)

    def get_self_name(self):
        return self._peers[0].name

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _get_default_avatar_path():
        return util.join_path(util.get_images_directory(), 'group.png')

    def _add_self_to_gc(self):
        pass
