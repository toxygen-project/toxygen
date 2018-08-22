import common.tox_save as tox_save
import utils.ui as util_ui
from groups.peers_list import PeersListGenerator
from groups.group_invite import GroupInvite
import wrapper.toxcore_enums_and_consts as constants


class GroupsService(tox_save.ToxSave):

    def __init__(self, tox, contacts_manager, contacts_provider, main_screen, widgets_factory_provider):
        super().__init__(tox)
        self._contacts_manager = contacts_manager
        self._contacts_provider = contacts_provider
        self._main_screen = main_screen
        self._peers_list_widget = main_screen.peers_list
        self._widgets_factory_provider = widgets_factory_provider
        self._group_invites = []
        self._screen = None

    def set_tox(self, tox):
        super().set_tox(tox)
        for group in self._get_all_groups():
            group.set_tox(tox)

    # -----------------------------------------------------------------------------------------------------------------
    # Groups creation
    # -----------------------------------------------------------------------------------------------------------------

    def create_new_gc(self, name, privacy_state, nick, status):
        group_number = self._tox.group_new(privacy_state, name, nick, status)
        if group_number == -1:
            return

        self._add_new_group_by_number(group_number)
        group = self._get_group_by_number(group_number)
        group.status = constants.TOX_USER_STATUS['NONE']
        self._contacts_manager.update_filtration()

    def join_gc_by_id(self, chat_id, password, nick, status):
        group_number = self._tox.group_join(chat_id, password, nick, status)
        self._add_new_group_by_number(group_number)

    # -----------------------------------------------------------------------------------------------------------------
    # Groups reconnect and leaving
    # -----------------------------------------------------------------------------------------------------------------

    def leave_group(self, group_number):
        self._tox.group_leave(group_number)
        self._contacts_manager.delete_group(group_number)

    def disconnect_from_group(self, group_number):
        self._tox.group_disconnect(group_number)
        group = self._get_group_by_number(group_number)
        group.status = None
        self._clear_peers_list(group)

    def reconnect_to_group(self, group_number):
        self._tox.group_reconnect(group_number)
        group = self._get_group_by_number(group_number)
        group.status = constants.TOX_USER_STATUS['NONE']
        self._clear_peers_list(group)

    # -----------------------------------------------------------------------------------------------------------------
    # Group invites
    # -----------------------------------------------------------------------------------------------------------------

    def invite_friend(self, friend_number, group_number):
        self._tox.group_invite_friend(group_number, friend_number)

    def process_group_invite(self, friend_number, group_name, invite_data):
        friend = self._get_friend_by_number(friend_number)
        invite = GroupInvite(friend.tox_id, group_name, invite_data)
        self._group_invites.append(invite)
        self._update_invites_button_state()

    def accept_group_invite(self, invite, name, status, password):
        pk = invite.friend_public_key
        friend = self._get_friend_by_public_key(pk)
        self._join_gc_via_invite(invite.invite_data, friend.number, name, status, password)
        self._delete_group_invite(invite)
        self._update_invites_button_state()

    def decline_group_invite(self, invite):
        self._delete_group_invite(invite)
        self._main_screen.update_gc_invites_button_state()

    def get_group_invites(self):
        return self._group_invites[:]

    group_invites = property(get_group_invites)

    def get_group_invites_count(self):
        return len(self._group_invites)

    group_invites_count = property(get_group_invites_count)

    # -----------------------------------------------------------------------------------------------------------------
    # Group info methods
    # -----------------------------------------------------------------------------------------------------------------

    def update_group_info(self, group):
        group.name = self._tox.group_get_name(group.number)
        group.status_message = self._tox.group_get_topic(group.number)

    def set_group_topic(self, group):
        if not group.is_self_moderator_or_founder():
            return
        text = util_ui.tr('New topic for group "{}":'.format(group.name))
        title = util_ui.tr('Set group topic')
        topic, ok = util_ui.text_dialog(text, title, group.status_message)
        if not ok or not topic:
            return
        self._tox.group_set_topic(group.number, topic)
        group.status_message = topic

    def show_group_management_screen(self, group):
        widgets_factory = self._get_widgets_factory()
        self._screen = widgets_factory.create_group_management_screen(group)
        self._screen.show()

    def show_group_settings_screen(self, group):
        widgets_factory = self._get_widgets_factory()
        self._screen = widgets_factory.create_group_settings_screen(group)
        self._screen.show()

    def set_group_password(self, group, password):
        if group.password == password:
            return
        self._tox.group_founder_set_password(group.number, password)
        group.password = password

    def set_group_peers_limit(self, group, peers_limit):
        if group.peers_limit == peers_limit:
            return
        self._tox.group_founder_set_peer_limit(group.number, peers_limit)
        group.peers_limit = peers_limit

    def set_group_privacy_state(self, group, privacy_state):
        is_private = privacy_state == constants.TOX_GROUP_PRIVACY_STATE['PRIVATE']
        if group.is_private == is_private:
            return
        self._tox.group_founder_set_privacy_state(group.number, privacy_state)
        group.is_private = is_private

    # -----------------------------------------------------------------------------------------------------------------
    # Peers list
    # -----------------------------------------------------------------------------------------------------------------

    def generate_peers_list(self):
        if not self._contacts_manager.is_active_a_group():
            return
        group = self._contacts_manager.get_curr_contact()
        PeersListGenerator().generate(group.peers, self, self._peers_list_widget, group.tox_id)

    def peer_selected(self, chat_id, peer_id):
        widgets_factory = self._get_widgets_factory()
        group = self._get_group_by_public_key(chat_id)
        self_peer = group.get_self_peer()
        if self_peer.id != peer_id:
            self._screen = widgets_factory.create_peer_screen_window(group, peer_id)
        else:
            self._screen = widgets_factory.create_self_peer_screen_window(group)
        self._screen.show()

    # -----------------------------------------------------------------------------------------------------------------
    # Peers actions
    # -----------------------------------------------------------------------------------------------------------------

    def set_new_peer_role(self, group, peer, role):
        self._tox.group_mod_set_role(group.number, peer.id, role)
        peer.role = role
        self.generate_peers_list()

    def toggle_ignore_peer(self, group, peer, ignore):
        self._tox.group_toggle_ignore(group.number, peer.id, ignore)
        peer.is_muted = ignore

    def set_self_info(self, group, name, status):
        self._tox.group_self_set_name(group.number, name)
        self._tox.group_self_set_status(group.number, status)
        self_peer = group.get_self_peer()
        self_peer.name = name
        self_peer.status = status
        self.generate_peers_list()

    # -----------------------------------------------------------------------------------------------------------------
    # Bans support
    # -----------------------------------------------------------------------------------------------------------------

    def show_bans_list(self, group):
        widgets_factory = self._get_widgets_factory()
        self._screen = widgets_factory.create_groups_bans_screen(group)
        self._screen.show()

    def ban_peer(self, group, peer_id, ban_type):
        self._tox.group_mod_ban_peer(group.number, peer_id, ban_type)
        group.remove_peer(peer_id)

    def kick_peer(self, group, peer_id):
        self._tox.group_mod_remove_peer(group.number, peer_id)
        group.remove_peer(peer_id)

    def cancel_ban(self, group_number, ban_id):
        self._tox.group_mod_remove_ban(group_number, ban_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _add_new_group_by_number(self, group_number):
        self._contacts_manager.add_group(group_number)

    def _get_group_by_number(self, group_number):
        return self._contacts_provider.get_group_by_number(group_number)

    def _get_group_by_public_key(self, public_key):
        return self._contacts_provider.get_group_by_public_key(public_key)

    def _get_all_groups(self):
        return self._contacts_provider.get_all_groups()

    def _get_friend_by_number(self, friend_number):
        return self._contacts_provider.get_friend_by_number(friend_number)

    def _get_friend_by_public_key(self, public_key):
        return self._contacts_provider.get_friend_by_public_key(public_key)

    def _clear_peers_list(self, group):
        group.remove_all_peers_except_self()
        self.generate_peers_list()

    def _delete_group_invite(self, invite):
        if invite in self._group_invites:
            self._group_invites.remove(invite)

    def _join_gc_via_invite(self, invite_data, friend_number, nick, status, password):
        group_number = self._tox.group_invite_accept(invite_data, friend_number, nick, status, password)
        self._add_new_group_by_number(group_number)

    def _update_invites_button_state(self):
        self._main_screen.update_gc_invites_button_state()

    def _get_widgets_factory(self):
        return self._widgets_factory_provider.get_item()
