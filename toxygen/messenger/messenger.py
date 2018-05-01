import util.util as util
from wrapper.toxcore_enums_and_consts import *
from messenger.messages import *


class Messenger(util.ToxSave):

    def __init__(self, tox, plugin_loader, screen, contacts_manager, contacts_provider, items_factory):
        super().__init__(tox)
        self._plugin_loader = plugin_loader
        self._screen = screen
        self._contacts_manager = contacts_manager
        self._contacts_provider = contacts_provider
        self._items_factory = items_factory

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _create_message_item(self, text_message):
        # pixmap = self._contacts_manager.get_curr_contact().get_pixmap()
        self._items_factory.message_item(text_message)

    # -----------------------------------------------------------------------------------------------------------------
    # Messaging
    # -----------------------------------------------------------------------------------------------------------------

    def new_message(self, friend_number, message_type, message):
        """
        Current user gets new message
        :param friend_number: friend_num of friend who sent message
        :param message_type: message type - plain text or action message (/me)
        :param message: text of message
        """
        t = util.get_unix_time()

        if self._contacts_manager.is_friend_active(friend_number):  # add message to list
            self.create_message_item(message, t, MESSAGE_AUTHOR['FRIEND'], message_type)
            self._screen.messages.scrollToBottom()
            self._contacts_manager.get_curr_contact().append_message(
                TextMessage(message, MESSAGE_AUTHOR['FRIEND'], t, message_type))
        else:
            friend = self.get_friend_by_number(friend_number)
            friend.inc_messages()
            friend.append_message(
                TextMessage(message, MESSAGE_AUTHOR['FRIEND'], t, message_type))
            if not friend.visibility:
                self._contacts_manager.update_filtration()

    def send_message(self):
        self.send_message_to_friend(self._screen.messageEdit.toPlainText())

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
            friend = self.get_friend_by_number(friend_number)
            messages = self._split_message(text.encode('utf-8'))
            t = util.get_unix_time()
            for message in messages:
                if friend.status is not None:
                    message_id = self._tox.friend_send_message(friend_number, message_type, message)
                    friend.inc_receipts()
                else:
                    message_id = 0
                message = TextMessage(message_id, text, MESSAGE_AUTHOR['NOT_SENT'], t, message_type)
                friend.append_message(message)
                if self._contacts_manager.is_friend_active(friend_number):
                    self._create_message_item(message)
                    self._screen.messageEdit.clear()
                    self._screen.messages.scrollToBottom()

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

    def get_friend_by_number(self, friend_number):
        return self._contacts_provider.get_friend_by_number(friend_number)
