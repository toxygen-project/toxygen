from history.history_logs_generators import *


class History:

    def __init__(self, contact_provider, db, settings, main_screen, messages_items_factory):
        self._contact_provider = contact_provider
        self._db = db
        self._settings = settings
        self._messages = main_screen.messages
        self._messages_items_factory = messages_items_factory
        self._is_loading = False
           
    def __del__(self):
        del self._db

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
                self._db.save_messages_to_db(friend.tox_id, messages)
                unsent_messages = friend.get_unsent_messages()
                # unsent_time = unsent_messages[0].get_data()[2] if len(unsent_messages) else time.time() + 1
                # self._db.update_messages(friend.tox_id, unsent_time)
        self._db.save()

    def clear_history(self, friend, save_unsent=False):
        """
        Clear chat history
        """
        friend.clear_corr(save_unsent)
        self._db.delete_friend_from_db(friend.tox_id)

    def delete_message(self, message):
        pass

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
            if message.get_type() <= 1:  # text message
                self._create_message_item(message)
            elif message.get_type() == MESSAGE_TYPE['FILE_TRANSFER']:  # file transfer
                if message.get_status() is None:
                    self._create_unsent_file_item(message)
                    continue
                self._create_file_transfer_item(message)
            elif message.get_type() == MESSAGE_TYPE['INLINE']:  # inline image
                self._create_inline_item(message)
            else:  # info message
                self._create_message_item(message)
        self._is_loading = False

    def get_message_getter(self, friend_public_key):
        self._db.add_friend_to_db(friend_public_key)

        return self._db.messages_getter(friend_public_key)

    def delete_history(self, friend):
        self.clear_history(friend)
        self._db.delete_friend_from_db(friend.tox_id)

    def add_friend_to_db(self, tox_id):
        self._db.add_friend_to_db(tox_id)

    @staticmethod
    def export_history(contact, as_text=True, _range=None):
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
