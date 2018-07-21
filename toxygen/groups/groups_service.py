import common.tox_save as tox_save
import utils.ui as util_ui
from groups.peers_list import PeersListGenerator
import wrapper.toxcore_enums_and_consts as constants


class GroupsService(tox_save.ToxSave):

    def __init__(self, tox, contacts_manager, contacts_provider, main_screen):
        super().__init__(tox)
        self._contacts_manager = contacts_manager
        self._contacts_provider = contacts_provider
        self._peers_list_widget = main_screen.peers_list

    def set_tox(self, tox):
        super().set_tox(tox)
        for group in self._get_all_groups():
            group.set_tox(tox)

    # -----------------------------------------------------------------------------------------------------------------
    # Groups creation
    # -----------------------------------------------------------------------------------------------------------------

    def create_new_gc(self, name, privacy_state):
        group_number = self._tox.group_new(privacy_state, name.encode('utf-8'))
        if group_number != -1:
            self._add_new_group_by_number(group_number)

    def join_gc_by_id(self, chat_id, password):
        group_number = self._tox.group_join(chat_id, password)
        self._add_new_group_by_number(group_number)

    def join_gc_via_invite(self, invite_data, friend_number, password):
        group_number = self._tox.group_invite_accept(invite_data, friend_number, password)
        self._add_new_group_by_number(group_number)

    # -----------------------------------------------------------------------------------------------------------------
    # Groups reconnect and leaving
    # -----------------------------------------------------------------------------------------------------------------

    def leave_group(self, group_number):
        self._tox.group_leave(group_number)
        self._contacts_manager.delete_group(group_number)
        self._contacts_manager.update_groups_numbers()

    def disconnect_from_group(self, group_number):
        self._tox.group_disconnect(group_number)
        group = self._get_group(group_number)
        group.status = None
        self._clear_peers_list(group)

    def reconnect_to_group(self, group_number):
        self._tox.group_reconnect(group_number)
        group = self._get_group(group_number)
        group.status = constants.TOX_USER_STATUS['NONE']
        self._clear_peers_list(group)

    # -----------------------------------------------------------------------------------------------------------------
    # Group invites
    # -----------------------------------------------------------------------------------------------------------------

    def invite_friend(self, friend_number, group_number):
        self._tox.group_invite_friend(group_number, friend_number)

    def process_group_invite(self, friend_number, group_name, invite_data):
        friend = self._get_friend(friend_number)
        text = util_ui.tr('Friend {} invites you to group "{}". Accept?')
        if util_ui.question(text.format(friend.name, group_name), util_ui.tr('Group invite')):
            self.join_gc_via_invite(invite_data, friend_number, None)

    # -----------------------------------------------------------------------------------------------------------------
    # Group info methods
    # -----------------------------------------------------------------------------------------------------------------

    def update_group_info(self, group):
        group.name = self._tox.group_get_name(group.number)
        group.status_message = self._tox.group_get_topic(group.number)

    def set_group_topic(self, group):
        if not group.is_moderator_or_founder():
            return
        text = util_ui.tr('New topic for group {}:'.format(group.name))
        title = util_ui.tr('Set group topic')
        topic, ok = util_ui.text_dialog(text, title, group.status_message)
        if not ok or not topic:
            return
        self._tox.group_set_topic(group.number, topic)
        group.status_message = topic

    # -----------------------------------------------------------------------------------------------------------------
    # Peers list
    # -----------------------------------------------------------------------------------------------------------------

    def generate_peers_list(self):
        if not self._contacts_manager.is_active_a_group():
            return
        group = self._contacts_manager.get_curr_contact()
        PeersListGenerator().generate(group.peers, self, self._peers_list_widget, group.tox_id)

    def peer_selected(self, chat_id, peer_id):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _add_new_group_by_number(self, group_number):
        self._contacts_manager.add_group(group_number)

    def _get_group(self, group_number):
        return self._contacts_provider.get_group_by_number(group_number)

    def _get_friend(self, friend_number):
        return self._contacts_provider.get_friend_by_number(friend_number)

    def _get_all_groups(self):
        return self._contacts_provider.get_all_groups()

    def _clear_peers_list(self, group):
        group.remove_all_peers_except_self()
        self.generate_peers_list()
