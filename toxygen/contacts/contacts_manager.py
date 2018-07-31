from contacts.friend import Friend
from contacts.group_chat import GroupChat
from messenger.messages import *
from common.tox_save import ToxSave
from contacts.group_peer_contact import GroupPeerContact


class ContactsManager(ToxSave):
    """
    Represents contacts list.
    """

    def __init__(self, tox, settings, screen, profile_manager, contact_provider, history, tox_dns,
                 messages_items_factory):
        super().__init__(tox)
        self._settings = settings
        self._screen = screen
        self._profile_manager = profile_manager
        self._contact_provider = contact_provider
        self._tox_dns = tox_dns
        self._messages_items_factory = messages_items_factory
        self._messages = screen.messages
        self._contacts, self._active_contact = [], -1
        self._active_contact_changed = Event()
        self._sorting = settings['sorting']
        self._filter_string = ''
        self._friend_item_height = 40 if settings['compact_mode'] else 70
        screen.contacts_filter.setCurrentIndex(int(self._sorting))
        self._history = history
        self._load_contacts()

    def get_contact(self, num):
        if num < 0 or num >= len(self._contacts):
            return None
        return self._contacts[num]

    def get_curr_contact(self):
        return self._contacts[self._active_contact] if self._active_contact + 1 else None

    def save_profile(self):
        data = self._tox.get_savedata()
        self._profile_manager.save_profile(data)

    def is_friend_active(self, friend_number):
        if not self.is_active_a_friend():
            return False

        return self.get_curr_contact().number == friend_number

    def is_group_active(self, group_number):
        if self.is_active_a_friend():
            return False

        return self.get_curr_contact().number == group_number

    def is_contact_active(self, contact):
        return self._contacts[self._active_contact].tox_id == contact.tox_id

    # -----------------------------------------------------------------------------------------------------------------
    # Reconnection support
    # -----------------------------------------------------------------------------------------------------------------

    def reset_contacts_statuses(self):
        for contact in self._contacts:
            contact.status = None

    # -----------------------------------------------------------------------------------------------------------------
    # Work with active friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_active(self):
        return self._active_contact

    def set_active(self, value):
        """
        Change current active friend or update info
        :param value: number of new active friend in friend's list
        """
        if value is None and self._active_contact == -1:  # nothing to update
            return
        if value == -1:  # all friends were deleted
            self._screen.account_name.setText('')
            self._screen.account_status.setText('')
            self._screen.account_status.setToolTip('')
            self._active_contact = -1
            self._screen.account_avatar.setHidden(True)
            self._messages.clear()
            self._screen.messageEdit.clear()
            return
        try:
            self._screen.typing.setVisible(False)
            current_contact = self.get_curr_contact()
            if current_contact is not None:
                current_contact.typing_notification_handler.send(self._tox, False)
                current_contact.remove_messages_widgets()  # TODO: if required
                self._unsubscribe_from_events(current_contact)

            if self._active_contact + 1 and self._active_contact != value:
                try:
                    current_contact.curr_text = self._screen.messageEdit.toPlainText()
                except:
                    pass
            contact = self._contacts[value]
            self._subscribe_to_events(contact)
            contact.remove_invalid_unsent_files()
            if self._active_contact != value:
                self._screen.messageEdit.setPlainText(contact.curr_text)
            self._active_contact = value
            contact.reset_messages()
            if not self._settings['save_history']:
                contact.delete_old_messages()
            self._messages.clear()
            contact.load_corr()
            corr = contact.get_corr()[-PAGE_SIZE:]
            for message in corr:
                if message.type == MESSAGE_TYPE['FILE_TRANSFER']:
                    self._messages_items_factory.create_file_transfer_item(message)
                elif message.type == MESSAGE_TYPE['INLINE']:
                    self._messages_items_factory.create_inline_item(message.data)
                else:
                    self._messages_items_factory.create_message_item(message)
            # if value in self._call:
            #     self._screen.active_call()
            # elif value in self._incoming_calls:
            #     self._screen.incoming_call()
            # else:
            #     self._screen.call_finished()
            self._set_current_contact_data(contact)
            self._active_contact_changed(contact)
        except Exception as ex:  # no friend found. ignore
            util.log('Friend value: ' + str(value))
            util.log('Error in set active: ' + str(ex))
            raise

    active_contact = property(get_active, set_active)

    def get_active_contact_changed(self):
        return self._active_contact_changed

    active_contact_changed = property(get_active_contact_changed)

    def update(self):
        if self._active_contact + 1:
            self.set_active(self._active_contact)

    def is_active_a_friend(self):
        return type(self.get_curr_contact()) is Friend

    def is_active_a_group(self):
        return type(self.get_curr_contact()) is GroupChat

    # -----------------------------------------------------------------------------------------------------------------
    # Filtration
    # -----------------------------------------------------------------------------------------------------------------

    def filtration_and_sorting(self, sorting=0, filter_str=''):
        """
        Filtration of friends list
        :param sorting: 0 - no sorting, 1 - online only, 2 - online first, 3 - by name,
        4 - online and by name, 5 - online first and by name
        :param filter_str: show contacts which name contains this substring
        """
        filter_str = filter_str.lower()
        contact = self.get_curr_contact()

        if sorting > 5 or sorting < 0:
            sorting = 0

        if sorting in (1, 2, 4, 5):  # online first
            self._contacts = sorted(self._contacts, key=lambda x: int(x.status is not None), reverse=True)
            sort_by_name = sorting in (4, 5)
            # save results of previous sorting
            online_friends = filter(lambda x: x.status is not None, self._contacts)
            online_friends_count = len(list(online_friends))
            part1 = self._contacts[:online_friends_count]
            part2 = self._contacts[online_friends_count:]
            key_lambda = lambda x: x.name.lower() if sort_by_name else x.number
            part1 = sorted(part1, key=key_lambda)
            part2 = sorted(part2, key=key_lambda)
            self._contacts = part1 + part2
        elif sorting == 0:
            self._contacts = sorted(self._contacts, key=lambda x: x.number)
        else:
            self._contacts = sorted(self._contacts, key=lambda x: x.name.lower())

            # change item widgets
        for index, contact in enumerate(self._contacts):
            list_item = self._screen.friends_list.item(index)
            item_widget = self._screen.friends_list.itemWidget(list_item)
            contact.set_widget(item_widget)

        for index, friend in enumerate(self._contacts):
            filtered_by_name = filter_str in friend.name.lower()
            friend.visibility = (friend.status is not None or sorting not in (1, 4)) and filtered_by_name
            # show friend even if it's hidden when there any unread messages/actions
            friend.visibility = friend.visibility or friend.messages or friend.actions
            if friend.visibility:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, self._friend_item_height))
            else:
                self._screen.friends_list.item(index).setSizeHint(QtCore.QSize(250, 0))
        # save soring results
        self._sorting, self._filter_string = sorting, filter_str
        self._settings['sorting'] = self._sorting
        self._settings.save()
        # update active contact
        if contact is not None:
            index = self._contacts.index(contact)
            self.set_active(index)

    def update_filtration(self):
        """
        Update list of contacts when 1 of friends change connection status
        """
        self.filtration_and_sorting(self._sorting, self._filter_string)

    # -----------------------------------------------------------------------------------------------------------------
    # Contact getters
    # -----------------------------------------------------------------------------------------------------------------

    def get_friend_by_number(self, number):
        return list(filter(lambda c: c.number == number and type(c) is Friend, self._contacts))[0]

    def get_group_by_number(self, number):
        return list(filter(lambda c: c.number == number and type(c) is GroupChat, self._contacts))[0]

    def get_or_create_group_peer_contact(self, group_number, peer_id):
        group = self.get_group_by_number(group_number)
        peer = group.get_peer_by_id(peer_id)
        if not self.check_if_contact_exists(peer.public_key):
            self.add_group_peer(group, peer)

        return self.get_contact_by_tox_id(peer.public_key)

    def check_if_contact_exists(self, tox_id):
        return any(filter(lambda c: c.tox_id == tox_id, self._contacts))

    def get_contact_by_tox_id(self, tox_id):
        return list(filter(lambda c: c.tox_id == tox_id, self._contacts))[0]

    def get_active_number(self):
        return self.get_curr_contact().number if self._active_contact + 1 else -1

    def get_active_name(self):
        return self.get_curr_contact().name if self._active_contact + 1 else ''

    def is_active_online(self):
        return self._active_contact + 1 and self.get_curr_contact().status is not None

    # -----------------------------------------------------------------------------------------------------------------
    # Work with friends (remove, block, set alias, get public key)
    # -----------------------------------------------------------------------------------------------------------------

    def set_alias(self, num):
        """
        Set new alias for friend
        """
        friend = self._contacts[num]
        name = friend.name
        text = util_ui.tr("Enter new alias for friend {} or leave empty to use friend's name:").format(name)
        title = util_ui.tr('Set alias')
        text, ok = util_ui.text_dialog(text, title, name)
        if not ok:
            return
        aliases = self._settings['friends_aliases']
        if text:
            friend.name = text
            try:
                index = list(map(lambda x: x[0], aliases)).index(friend.tox_id)
                aliases[index] = (friend.tox_id, text)
            except:
                aliases.append((friend.tox_id, text))
            friend.set_alias(text)
        else:  # use default name
            friend.name = self._tox.friend_get_name(friend.number)
            friend.set_alias('')
            try:
                index = list(map(lambda x: x[0], aliases)).index(friend.tox_id)
                del aliases[index]
            except:
                pass
        self._settings.save()

    def friend_public_key(self, num):
        return self._contacts[num].tox_id

    def export_history(self, num, as_text):
        contact = self._contacts[num]
        return self._history.export_history(contact, as_text)

    def delete_friend(self, num):
        """
        Removes friend from contact list
        :param num: number of friend in list
        """
        friend = self._contacts[num]
        self._cleanup_contact_data(friend)
        self._tox.friend_delete(friend.number)
        self._delete_contact(num)

    def add_friend(self, tox_id):
        """
        Adds friend to list
        """
        self._tox.friend_add_norequest(tox_id)
        self._add_friend(tox_id)
        self.update_filtration()

    def block_user(self, tox_id):
        """
        Block user with specified tox id (or public key) - delete from friends list and ignore friend requests
        """
        tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
        if tox_id == self._tox.self_get_address[:TOX_PUBLIC_KEY_SIZE * 2]:
            return
        if tox_id not in self._settings['blocked']:
            self._settings['blocked'].append(tox_id)
            self._settings.save()
        try:
            num = self._tox.friend_by_public_key(tox_id)
            self.delete_friend(num)
            self.save_profile()
        except:  # not in friend list
            pass

    def unblock_user(self, tox_id, add_to_friend_list):
        """
        Unblock user
        :param tox_id: tox id of contact
        :param add_to_friend_list: add this contact to friend list or not
        """
        self._settings['blocked'].remove(tox_id)
        self._settings.save()
        if add_to_friend_list:
            self.add_friend(tox_id)
            self.save_profile()

    # -----------------------------------------------------------------------------------------------------------------
    # Groups support
    # -----------------------------------------------------------------------------------------------------------------

    def get_group_chats(self):
        return list(filter(lambda c: type(c) is GroupChat, self._contacts))

    def add_group(self, group_number):
        group = self._contact_provider.get_group_by_number(group_number)
        index = len(self._contacts)
        self._contacts.append(group)
        group.reset_avatar(self._settings['identicons'])
        self._save_profile()
        self.set_active(index)
        self.update_filtration()

    def delete_group(self, group_number):
        group = self.get_group_by_number(group_number)
        self._cleanup_contact_data(group)
        num = self._contacts.index(group)
        self._delete_contact(num)

    # -----------------------------------------------------------------------------------------------------------------
    # Groups private messaging
    # -----------------------------------------------------------------------------------------------------------------

    def add_group_peer(self, group, peer):
        contact = self._contact_provider.get_group_peer_by_id(group, peer.id)
        self._contacts.append(contact)
        contact.reset_avatar(self._settings['identicons'])
        self._save_profile()

    def remove_group_peer_by_id(self, group, peer_id):
        peer = group.get_peer_by_id(peer_id)
        if not self.check_if_contact_exists(peer.public_key):
            return
        contact = self.get_contact_by_tox_id(peer.public_key)
        self.remove_group_peer(contact)

    def remove_group_peer(self, group_peer_contact):
        contact = self.get_contact_by_tox_id(group_peer_contact.tox_id)
        self._cleanup_contact_data(contact)
        num = self._contacts.index(contact)
        self._delete_contact(num)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend requests
    # -----------------------------------------------------------------------------------------------------------------

    def send_friend_request(self, tox_id, message):
        """
        Function tries to send request to contact with specified id
        :param tox_id: id of new contact or tox dns 4 value
        :param message: additional message
        :return: True on success else error string
        """
        try:
            message = message or 'Hello! Add me to your contact list please'
            if '@' in tox_id:  # value like groupbot@toxme.io
                tox_id = self._tox_dns.lookup(tox_id)
                if tox_id is None:
                    raise Exception('TOX DNS lookup failed')
            if len(tox_id) == TOX_PUBLIC_KEY_SIZE * 2:  # public key
                self.add_friend(tox_id)
                title = util_ui.tr('Friend added')
                text = util_ui.tr('Friend added without sending friend request')
                util_ui.message_box(text, title)
            else:
                self._tox.friend_add(tox_id, message.encode('utf-8'))
                tox_id = tox_id[:TOX_PUBLIC_KEY_SIZE * 2]
                self._add_friend(tox_id)
                self.update_filtration()
            self.save_profile()
            return True
        except Exception as ex:  # wrong data
            util.log('Friend request failed with ' + str(ex))
            return str(ex)

    def process_friend_request(self, tox_id, message):
        """
        Accept or ignore friend request
        :param tox_id: tox id of contact
        :param message: message
        """
        if tox_id in self._settings['blocked']:
            return
        try:
            text = util_ui.tr('User {} wants to add you to contact list. Message:\n{}')
            reply = util_ui.question(text.format(tox_id, message), util_ui.tr('Friend request'))
            if reply:  # accepted
                self.add_friend(tox_id)
                data = self._tox.get_savedata()
                self._profile_manager.save_profile(data)
        except Exception as ex:  # something is wrong
            util.log('Accept friend request failed! ' + str(ex))

    def can_send_typing_notification(self):
        return self._settings['typing_notifications'] and self._active_contact + 1

    # -----------------------------------------------------------------------------------------------------------------
    # Contacts numbers update
    # -----------------------------------------------------------------------------------------------------------------

    def update_friends_numbers(self):
        for friend in self._contact_provider.get_all_friends():
            friend.number = self._tox.friend_by_public_key(friend.tox_id)
        self.update_filtration()

    def update_groups_numbers(self):
        groups = self._contact_provider.get_all_groups()
        for i in range(len(groups)):
            chat_id = self._tox.group_get_chat_id(i)
            group = self.get_contact_by_tox_id(chat_id)
            group.number = i
        self.update_filtration()

    def update_groups_lists(self):
        groups = self._contact_provider.get_all_groups()
        for group in groups:
            group.remove_all_peers_except_self()

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _load_contacts(self):
        self._load_friends()
        self._load_groups()
        if len(self._contacts):
            self.set_active(0)
        for contact in filter(lambda c: not c.has_avatar(), self._contacts):
            contact.reset_avatar(self._settings['identicons'])
        self.update_filtration()

    def _load_friends(self):
        self._contacts.extend(self._contact_provider.get_all_friends())

    def _load_groups(self):
        self._contacts.extend(self._contact_provider.get_all_groups())

    # -----------------------------------------------------------------------------------------------------------------
    # Current contact subscriptions
    # -----------------------------------------------------------------------------------------------------------------

    def _subscribe_to_events(self, contact):
        contact.name_changed_event.add_callback(self._current_contact_name_changed)
        contact.status_changed_event.add_callback(self._current_contact_status_changed)
        contact.status_message_changed_event.add_callback(self._current_contact_status_message_changed)
        contact.avatar_changed_event.add_callback(self._current_contact_avatar_changed)

    def _unsubscribe_from_events(self, contact):
        contact.name_changed_event.remove_callback(self._current_contact_name_changed)
        contact.status_changed_event.remove_callback(self._current_contact_status_changed)
        contact.status_message_changed_event.remove_callback(self._current_contact_status_message_changed)
        contact.avatar_changed_event.remove_callback(self._current_contact_avatar_changed)

    def _current_contact_name_changed(self, name):
        self._screen.account_name.setText(name)

    def _current_contact_status_changed(self, status):
        pass

    def _current_contact_status_message_changed(self, status_message):
        self._screen.account_status.setText(status_message)

    def _current_contact_avatar_changed(self, avatar_path):
        self._set_current_contact_avatar(avatar_path)

    def _set_current_contact_data(self, contact):
        self._screen.account_name.setText(contact.name)
        self._screen.account_status.setText(contact.status_message)
        self._set_current_contact_avatar(contact.get_avatar_path())

    def _set_current_contact_avatar(self, avatar_path):
        width = self._screen.account_avatar.width()
        pixmap = QtGui.QPixmap(avatar_path)
        self._screen.account_avatar.setPixmap(pixmap.scaled(width, width,
                                                            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def _add_friend(self, tox_id):
        self._history.add_friend_to_db(tox_id)
        friend = self._contact_provider.get_friend_by_public_key(tox_id)
        index = len(self._contacts)
        self._contacts.append(friend)
        if not friend.has_avatar():
            friend.reset_avatar(self._settings['identicons'])
        self._save_profile()
        self.set_active(index)

    def _save_profile(self):
        data = self._tox.get_savedata()
        self._profile_manager.save_profile(data)

    def _cleanup_contact_data(self, contact):
        try:
            index = list(map(lambda x: x[0], self._settings['friends_aliases'])).index(contact.tox_id)
            del self._settings['friends_aliases'][index]
        except:
            pass
        if contact.tox_id in self._settings['notes']:
            del self._settings['notes'][contact.tox_id]
        self._settings.save()
        self._history.delete_history(contact)
        if contact.has_avatar():
            avatar_path = contact.get_contact_avatar_path()
            remove(avatar_path)

    def _delete_contact(self, num):
        if len(self._contacts) == 1:
            self.set_active(-1)
        else:
            self.set_active(0)

        self._contact_provider.remove_contact_from_cache(self._contacts[num].tox_id)
        del self._contacts[num]
        self._screen.friends_list.takeItem(num)
        self._save_profile()

        self.update_filtration()
