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

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _create_message_item(self, text_message):
        # pixmap = self._contacts_manager.get_curr_contact().get_pixmap()
        self._items_factory.create_message_item(text_message)

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

        if self._contacts_manager.is_friend_active(friend_number):  # add message to list
            self._create_message_item(text_message)
            self._screen.messages.scrollToBottom()
            self._contacts_manager.get_curr_contact().append_message(text_message)
        else:
            friend.inc_messages()
            friend.append_message(text_message)
            if not friend.visibility:
                self._contacts_manager.update_filtration()

    def send_message(self):
        text = self._screen.messageEdit.toPlainText()
        if self._contacts_manager.is_active_a_friend():
            self.send_message_to_friend(text)
        else:
            self.send_message_to_group(text)

    def send_message_to_friend(self, text, friend_number=None):
        """
        Send message
        :param text: message text
        :param friend_number: number of friend
        """
        if friend_number is None:
            friend_number = self._contacts_manager.get_active_number()
        if text.startswith('/plugin '):
            self._plugin_loader.command(text[8:])
            self._screen.messageEdit.clear()
        elif text and friend_number >= 0:
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
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
                if self._contacts_manager.is_friend_active(friend_number):
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

    def send_message_to_group(self, text, group_number=None):
        if group_number is None:
            group_number = self._contacts_manager.get_active_number()
        if text.startswith('/plugin '):
            self._plugin_loader.command(text[8:])
            self._screen.messageEdit.clear()
        elif text and group_number >= 0:
            if text.startswith('/me '):
                message_type = TOX_MESSAGE_TYPE['ACTION']
                text = text[4:]
            else:
                message_type = TOX_MESSAGE_TYPE['NORMAL']
            group = self._get_group_by_number(group_number)
            messages = self._split_message(text.encode('utf-8'))
            t = util.get_unix_time()
            for message in messages:
                self._tox.group_send_message(group_number, message_type, message)
                message_author = MessageAuthor(group.get_self_name(), MESSAGE_AUTHOR['GC_PEER'])
                message = OutgoingTextMessage(text, message_author, t, message_type)
                group.append_message(message)
                if self._contacts_manager.is_group_active(group_number):
                    self._create_message_item(message)
                    self._screen.messageEdit.clear()
                    self._screen.messages.scrollToBottom()

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
        if self._contacts_manager.can_send_typing_notification():
            try:
                contact = self._contacts_manager.get_curr_contact()
                contact.typing_notification_handler.send(self._tox, typing)
            except:
                pass

    def friend_typing(self, friend_number, typing):
        """
        Display incoming typing notification
        """
        if self._contacts_manager.is_friend_active(friend_number):
            self._screen.typing.setVisible(typing)

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

    def _on_profile_name_changed(self, new_name):
        if self._profile_name == new_name:
            return
        message = util_ui.tr('User {} is now known as {}')
        message = message.format(self._profile_name, new_name)
        for friend in self._contacts_provider.get_all_friends():
            friend.append_message(InfoMessage(message, util.get_unix_time()))
        if self._contacts_manager.is_active_a_friend():
            self._create_info_message_item(message)
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
