import common.tox_save as tox_save
from messenger.messages import *


class Messenger(tox_save.ToxSave):

    def __init__(self, tox, plugin_loader, screen, contacts_manager, contacts_provider, items_factory, profile,
                 calls_manager):
        super().__init__(tox)
        self._plugin_loader = plugin_loader
        self._screen = screen
        self._contacts_manager = contacts_manager
        self._contacts_provider = contacts_provider
        self._items_factory = items_factory
        self._profile = profile
        self._profile_name = profile.name

        profile.name_changed_event.add_callback(self._on_profile_name_changed)
        calls_manager.call_started_event.add_callback(self._on_call_started)
        calls_manager.call_finished_event.add_callback(self._on_call_finished)

    def get_last_message(self):
        contact = self._contacts_manager.get_curr_contact()
        if contact is None:
            return str()

        return contact.get_last_message_text()

    # -----------------------------------------------------------------------------------------------------------------
    # Messaging - friends
    # -----------------------------------------------------------------------------------------------------------------

    def new_message(self, friend_number, message_type, message):
        """
        Current user gets new message
        :param friend_number: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        t = util.get_unix_time()
        friend = self._get_friend_by_number(friend_number)
        text_message = TextMessage(message, MessageAuthor(friend.name, MESSAGE_AUTHOR['FRIEND']), t, message_type)
        self._add_message(text_message, friend)

    def send_message(self):
        text = self._screen.messageEdit.toPlainText()

        plugin_command_prefix = '/plugin '
        if text.startswith(plugin_command_prefix):
            self._plugin_loader.command(text[len(plugin_command_prefix):])
            self._screen.messageEdit.clear()
            return

        action_message_prefix = '/me '
        if text.startswith(action_message_prefix):
            message_type = TOX_MESSAGE_TYPE['ACTION']
            text = text[len(action_message_prefix):]
        else:
            message_type = TOX_MESSAGE_TYPE['NORMAL']

        if self._contacts_manager.is_active_a_friend():
            self.send_message_to_friend(text, message_type)
        elif self._contacts_manager.is_active_a_group():
            self.send_message_to_group(text, message_type)
        elif self._contacts_manager.is_active_a_group_chat_peer():
            self.send_message_to_group_peer(text, message_type)

    def send_message_to_friend(self, text, message_type, friend_number=None):
        """
        Send message
        :param text: message text
        :param friend_number: number of friend
        """
        if friend_number is None:
            friend_number = self._contacts_manager.get_active_number()

        if not text or friend_number < 0:
            return

        friend = self._get_friend_by_number(friend_number)
        messages = self._split_message(text.encode('utf-8'))
        t = util.get_unix_time()
        for message in messages:
            if friend.status is not None:
                message_id = self._tox.friend_send_message(friend_number, message_type, message)
            else:
                message_id = 0
            message_author = MessageAuthor(self._profile.name, MESSAGE_AUTHOR['NOT_SENT'])
            message = OutgoingTextMessage(text, message_author, t, message_type, message_id)
            friend.append_message(message)
            if not self._contacts_manager.is_friend_active(friend_number):
                return
            self._create_message_item(message)
            self._screen.messageEdit.clear()
            self._screen.messages.scrollToBottom()

    def send_messages(self, friend_number):
        """
        Send 'offline' messages to friend
        """
        friend = self._get_friend_by_number(friend_number)
        friend.load_corr()
        messages = friend.get_unsent_messages()
        try:
            for message in messages:
                message_id = self._tox.friend_send_message(friend_number, message.type, message.text.encode('utf-8'))
                message.tox_message_id = message_id
        except Exception as ex:
            util.log('Sending pending messages failed with ' + str(ex))

    # -----------------------------------------------------------------------------------------------------------------
    # Messaging - groups
    # -----------------------------------------------------------------------------------------------------------------

    def send_message_to_group(self, text, message_type, group_number=None):
        if group_number is None:
            group_number = self._contacts_manager.get_active_number()

        if not text or group_number < 0:
            return

        group = self._get_group_by_number(group_number)
        messages = self._split_message(text.encode('utf-8'))
        t = util.get_unix_time()
        for message in messages:
            self._tox.group_send_message(group_number, message_type, message)
            message_author = MessageAuthor(group.get_self_name(), MESSAGE_AUTHOR['GC_PEER'])
            message = OutgoingTextMessage(text, message_author, t, message_type)
            group.append_message(message)
            if not self._contacts_manager.is_group_active(group_number):
                return
            self._create_message_item(message)
            self._screen.messageEdit.clear()
            self._screen.messages.scrollToBottom()

    def new_group_message(self, group_number, message_type, message, peer_id):
        """
        Current user gets new message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        t = util.get_unix_time()
        group = self._get_group_by_number(group_number)
        peer = group.get_peer_by_id(peer_id)
        text_message = TextMessage(message, MessageAuthor(peer.name, MESSAGE_AUTHOR['GC_PEER']), t, message_type)
        self._add_message(text_message, group)

    # -----------------------------------------------------------------------------------------------------------------
    # Messaging - group peers
    # -----------------------------------------------------------------------------------------------------------------

    def send_message_to_group_peer(self, text, message_type, group_number=None, peer_id=None):
        if group_number is None or peer_id is None:
            group_peer_contact = self._contacts_manager.get_curr_contact()
            peer_id = group_peer_contact.number
            group = self._get_group_by_public_key(group_peer_contact.group_pk)
            group_number = group.number

        if not text or group_number < 0 or peer_id < 0:
            return

        group_peer_contact = self._contacts_manager.get_or_create_group_peer_contact(group_number, peer_id)
        group = self._get_group_by_number(group_number)
        messages = self._split_message(text.encode('utf-8'))
        t = util.get_unix_time()
        for message in messages:
            self._tox.group_send_private_message(group_number, peer_id, message_type, message)
            message_author = MessageAuthor(group.get_self_name(), MESSAGE_AUTHOR['GC_PEER'])
            message = OutgoingTextMessage(text, message_author, t, message_type)
            group_peer_contact.append_message(message)
            if not self._contacts_manager.is_contact_active(group_peer_contact):
                return
            self._create_message_item(message)
            self._screen.messageEdit.clear()
            self._screen.messages.scrollToBottom()

    def new_group_private_message(self, group_number, message_type, message, peer_id):
        """
        Current user gets new message
        :param message: text of message
        """
        t = util.get_unix_time()
        group = self._get_group_by_number(group_number)
        peer = group.get_peer_by_id(peer_id)
        text_message = TextMessage(message, MessageAuthor(peer.name, MESSAGE_AUTHOR['GC_PEER']),
                                   t, message_type)
        group_peer_contact = self._contacts_manager.get_or_create_group_peer_contact(group_number, peer_id)
        self._add_message(text_message, group_peer_contact)

    # -----------------------------------------------------------------------------------------------------------------
    # Message receipts
    # -----------------------------------------------------------------------------------------------------------------

    def receipt(self, friend_number, message_id):
        friend = self._get_friend_by_number(friend_number)
        friend.mark_as_sent(message_id)

    # -----------------------------------------------------------------------------------------------------------------
    # Typing notifications
    # -----------------------------------------------------------------------------------------------------------------

    def send_typing(self, typing):
        """
        Send typing notification to a friend
        """
        if not self._contacts_manager.can_send_typing_notification():
            return
        contact = self._contacts_manager.get_curr_contact()
        contact.typing_notification_handler.send(self._tox, typing)

    def friend_typing(self, friend_number, typing):
        """
        Display incoming typing notification
        """
        if self._contacts_manager.is_friend_active(friend_number):
            self._screen.typing.setVisible(typing)

    # -----------------------------------------------------------------------------------------------------------------
    # Contact info updated
    # -----------------------------------------------------------------------------------------------------------------

    def new_friend_name(self, friend, old_name, new_name):
        if old_name == new_name or friend.has_alias():
            return
        message = util_ui.tr('User {} is now known as {}')
        message = message.format(old_name, new_name)
        friend.actions = True
        self._add_info_message(friend.number, message)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _split_message(message):
        messages = []
        while len(message) > TOX_MAX_MESSAGE_LENGTH:
            size = TOX_MAX_MESSAGE_LENGTH * 4 / 5
            last_part = message[size:TOX_MAX_MESSAGE_LENGTH]
            if ' ' in last_part:
                index = last_part.index(' ')
            elif ',' in last_part:
                index = last_part.index(',')
            elif '.' in last_part:
                index = last_part.index('.')
            else:
                index = TOX_MAX_MESSAGE_LENGTH - size - 1
            index += size + 1
            messages.append(message[:index])
            message = message[index:]
        if message:
            messages.append(message)

        return messages

    def _get_friend_by_number(self, friend_number):
        return self._contacts_provider.get_friend_by_number(friend_number)

    def _get_group_by_number(self, group_number):
        return self._contacts_provider.get_group_by_number(group_number)

    def _get_group_by_public_key(self, public_key):
        return self._contacts_provider.get_group_by_public_key( public_key)

    def _on_profile_name_changed(self, new_name):
        if self._profile_name == new_name:
            return
        message = util_ui.tr('User {} is now known as {}')
        message = message.format(self._profile_name, new_name)
        for friend in self._contacts_provider.get_all_friends():
            self._add_info_message(friend.number, message)
        self._profile_name = new_name

    def _on_call_started(self, friend_number, audio, video, is_outgoing):
        if is_outgoing:
            text = util_ui.tr("Outgoing video call") if video else util_ui.tr("Outgoing audio call")
        else:
            text = util_ui.tr("Incoming video call") if video else util_ui.tr("Incoming audio call")
        self._add_info_message(friend_number, text)

    def _on_call_finished(self, friend_number, is_declined):
        text = util_ui.tr("Call declined") if is_declined else util_ui.tr("Call finished")
        self._add_info_message(friend_number, text)

    def _add_info_message(self, friend_number, text):
        friend = self._get_friend_by_number(friend_number)
        message = InfoMessage(text, util.get_unix_time())
        friend.append_message(message)
        if self._contacts_manager.is_friend_active(friend_number):
            self._create_info_message_item(message)

    def _create_info_message_item(self, message):
        self._items_factory.create_message_item(message)
        self._screen.messages.scrollToBottom()

    def _add_message(self, text_message, contact):
        if self._contacts_manager.is_contact_active(contact):  # add message to list
            self._create_message_item(text_message)
            self._screen.messages.scrollToBottom()
            self._contacts_manager.get_curr_contact().append_message(text_message)
        else:
            contact.inc_messages()
            contact.append_message(text_message)
            if not contact.visibility:
                self._contacts_manager.update_filtration()

    def _create_message_item(self, text_message):
        # pixmap = self._contacts_manager.get_curr_contact().get_pixmap()
        self._items_factory.create_message_item(text_message)
