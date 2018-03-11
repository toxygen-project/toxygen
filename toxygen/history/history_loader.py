from messenger.messages import *


class HistoryLoader:

    def __init__(self, db, settings):
        self._db = db
        self._settings = settings

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def save_history(self):
        """
        Save history to db
        """
        if hasattr(self, '_history'):
            if self._settings['save_history']:
                for friend in filter(lambda x: type(x) is Friend, self._contacts):
                    if not self._history.friend_exists_in_db(friend.tox_id):
                        self._history.add_friend_to_db(friend.tox_id)
                    if not self._settings['save_unsent_only']:
                        messages = friend.get_corr_for_saving()
                    else:
                        messages = friend.get_unsent_messages_for_saving()
                        self._history.delete_messages(friend.tox_id)
                    self._history.save_messages_to_db(friend.tox_id, messages)
                    unsent_messages = friend.get_unsent_messages()
                    unsent_time = unsent_messages[0].get_data()[2] if len(unsent_messages) else time.time() + 1
                    self._history.update_messages(friend.tox_id, unsent_time)
            self._history.save()
            del self._history

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
        if not self._load_history:
            return
        self._load_history = False
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
        self._load_history = True

    def export_history(self, friend, as_text=True, _range=None):
        if _range is None:
            friend.load_all_corr()
            corr = friend.get_corr()
        elif _range[1] + 1:
            corr = friend.get_corr()[_range[0]:_range[1] + 1]
        else:
            corr = friend.get_corr()[_range[0]:]

        generator = TextHistoryGenerator() if as_text else HtmlHistoryGenerator

        return generator.generate(corr)


class HtmlHistoryGenerator:

    def generate(self, corr):
        arr = []
        for message in corr:
            if type(message) is TextMessage:
                data = message.get_data()
                x = '[{}] <b>{}:</b> {}<br>'
                arr.append(x.format(convert_time(data[2]) if data[1] != MESSAGE_OWNER['NOT_SENT'] else 'Unsent',
                                    friend.name if data[1] == MESSAGE_OWNER['FRIEND'] else self.name,
                                    data[0]))
        s = '<br>'.join(arr)
        s = '<html><head><meta charset="UTF-8"><title>{}</title></head><body>{}</body></html>'.format(friend.name,
                                                                                                          s)
        return s


class TextHistoryGenerator:

    def generate(self, corr):
        arr = []
        for message in corr:
            if type(message) is TextMessage:
                data = message.get_data()
                x = '[{}] {}: {}\n'
                arr.append(x.format(convert_time(data[2]) if data[1] != MESSAGE_OWNER['NOT_SENT'] else 'Unsent',
                                    friend.name if data[1] == MESSAGE_OWNER['FRIEND'] else self.name,
                                    data[0]))
        s = '\n'.join(arr)

        return s

