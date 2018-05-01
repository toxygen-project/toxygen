from history.history_logs_generators import *

# TODO: fix history loading and saving


class HistoryLoader:

    def __init__(self, contact_provider, db, settings):
        self._contact_provider = contact_provider
        self._db = db
        self._settings = settings
           
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
                if not self._db.friend_exists_in_db(friend.tox_id):
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
        if self._db.friend_exists_in_db(friend.tox_id):
            self._db.delete_messages(friend.tox_id)
            self._db.delete_friend_from_db(friend.tox_id)

    def load_history(self):
        """
        Tries to load next part of messages
        """
        if not self._load_db:
            return
        self._load_db = False
        friend = self.get_curr_friend()
        friend.load_corr(False)
        data = friend.get_corr()
        if not data:
            return
        data.reverse()
        data = data[self._messages.count():self._messages.count() + PAGE_SIZE]
        for message in data:
            if message.get_type() <= 1:  # text message
                data = message.get_data()
                self.create_message_item(data[0],
                                         data[2],
                                         data[1],
                                         data[3],
                                         False)
            elif message.get_type() == MESSAGE_TYPE['FILE_TRANSFER']:  # file transfer
                if message.get_status() is None:
                    self.create_unsent_file_item(message)
                    continue
                item = self.create_file_transfer_item(message, False)
                if message.get_status() in ACTIVE_FILE_TRANSFERS:  # active file transfer
                    try:
                        ft = self._file_transfers[(message.get_friend_number(), message.get_file_number())]
                        ft.set_state_changed_handler(item.update_transfer_state)
                        ft.signal()
                    except:
                        print('Incoming not started transfer - no info found')
            elif message.get_type() == MESSAGE_TYPE['INLINE']:  # inline image
                self.create_inline_item(message.get_data(), False)
            else:  # info message
                data = message.get_data()
                self.create_message_item(data[0],
                                         data[2],
                                         '',
                                         data[3],
                                         False)
        self._load_db = True

    def get_message_getter(self, friend_public_key):
        if not self._db.friend_exists_in_db(friend_public_key):
            self._db.add_friend_to_db(friend_public_key)

        return self._db.messages_getter(friend_public_key)

    def delete_history(self, friend):
        self.clear_history(friend)
        if self._db.friend_exists_in_db(friend.tox_id):
            self._db.delete_friend_from_db(friend.tox_id)

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
