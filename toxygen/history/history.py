from history.history_logs_generators import *


class History:

    def __init__(self, contact_provider, db, settings, main_screen, messages_items_factory):
        self._contact_provider = contact_provider
        self._db = db
        self._settings = settings
        self._messages = main_screen.messages
        self._messages_items_factory = messages_items_factory
        self._is_loading = False
        self._contacts_manager = None
           
    def __del__(self):
        del self._db

    def set_contacts_manager(self, contacts_manager):
        self._contacts_manager = contacts_manager

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def save_history(self):
        """
        Save history to db
        """
        if self._settings['save_db']:
            for friend in self._contact_provider.get_all_friends():
                self._db.add_friend_to_db(friend.tox_id)
                if not self._settings['save_unsent_only']:
                    messages = friend.get_corr_for_saving()
                else:
                    messages = friend.get_unsent_messages_for_saving()
                    self._db.delete_messages(friend.tox_id)
                messages = map(lambda m: (m.text, m.author.name, m.author.type, m.time, m.type), messages)
                self._db.save_messages_to_db(friend.tox_id, messages)

        self._db.save()

    def clear_history(self, friend, save_unsent=False):
        """
        Clear chat history
        """
        friend.clear_corr(save_unsent)
        self._db.delete_friend_from_db(friend.tox_id)

    def export_history(self, contact, as_text=True):
        extension = 'txt' if as_text else 'html'
        file_name, _ = util_ui.save_file_dialog(util_ui.tr('Choose file name'), extension)

        if not file_name:
            return

        if not file_name.endswith('.' + extension):
            file_name += '.' + extension

        history = self.generate_history(contact, as_text)
        with open(file_name, 'wt') as fl:
            fl.write(history)

    def delete_message(self, message):
        contact = self._contacts_manager.get_curr_contact()
        if message.type in (MESSAGE_TYPE['TEXT'], MESSAGE_TYPE['ACTION']):
            if message.is_saved():
                self._db.delete_message(contact.tox_id, message.id)
        contact.delete_message(message.message_id)

    def load_history(self, friend):
        """
        Tries to load next part of messages
        """
        if self._is_loading:
            return
        self._is_loading = True
        friend.load_corr(False)
        messages = friend.get_corr()
        if not messages:
            self._is_loading = False
            return
        messages.reverse()
        messages = messages[self._messages.count():self._messages.count() + PAGE_SIZE]
        for message in messages:
            message_type = message.get_type()
            if message_type in (MESSAGE_TYPE['TEXT'], MESSAGE_TYPE['ACTION']):  # text message
                self._create_message_item(message)
            elif message_type == MESSAGE_TYPE['FILE_TRANSFER']:  # file transfer
                if message.state == FILE_TRANSFER_STATE['UNSENT']:
                    self._create_unsent_file_item(message)
                else:
                    self._create_file_transfer_item(message)
            elif message_type == MESSAGE_TYPE['INLINE']:  # inline image
                self._create_inline_item(message)
            else:  # info message
                self._create_message_item(message)
        self._is_loading = False

    def get_message_getter(self, friend_public_key):
        self._db.add_friend_to_db(friend_public_key)

        return self._db.messages_getter(friend_public_key)

    def delete_history(self, friend):
        self._db.delete_friend_from_db(friend.tox_id)

    def add_friend_to_db(self, tox_id):
        self._db.add_friend_to_db(tox_id)

    @staticmethod
    def generate_history(contact, as_text=True, _range=None):
        if _range is None:
            contact.load_all_corr()
            corr = contact.get_corr()
        elif _range[1] + 1:
            corr = contact.get_corr()[_range[0]:_range[1] + 1]
        else:
            corr = contact.get_corr()[_range[0]:]

        generator = TextHistoryGenerator(corr, contact.name) if as_text else HtmlHistoryGenerator(corr, contact.name)

        return generator.generate()

    # -----------------------------------------------------------------------------------------------------------------
    # Items creation
    # -----------------------------------------------------------------------------------------------------------------

    def _create_message_item(self, message):
        return self._messages_items_factory.create_message_item(message, False)

    def _create_unsent_file_item(self, message):
        return self._messages_items_factory.create_unsent_file_item(message, False)

    def _create_file_transfer_item(self, message):
        return self._messages_items_factory.create_file_transfer_item(message, False)

    def _create_inline_item(self, message):
        return self._messages_items_factory.create_inline_item(message, False)
