import contact
from messages import *
from history import *
import util
import file_transfers as ft


class Friend(contact.Contact):
    """
    Friend in list of friends. Can be hidden, properties 'has unread messages' and 'has alias' added
    """

    def __init__(self, message_getter, number, *args):
        """
        :param message_getter: gets messages from db
        :param number: number of friend.
        """
        super(Friend, self).__init__(*args)
        self._number = number
        self._new_messages = False
        self._visible = True
        self._alias = False
        self._message_getter = message_getter
        self._corr = []
        self._unsaved_messages = 0
        self._history_loaded = self._new_actions = False
        self._receipts = 0
        self._curr_text = ''

    def __del__(self):
        self.set_visibility(False)
        del self._widget
        if hasattr(self, '_message_getter'):
            del self._message_getter

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def get_receipts(self):
        return self._receipts

    receipts = property(get_receipts)  # read receipts

    def inc_receipts(self):
        self._receipts += 1

    def dec_receipt(self):
        if self._receipts:
            self._receipts -= 1
            self.mark_as_sent()

    def load_corr(self, first_time=True):
        """
        :param first_time: friend became active, load first part of messages
        """
        if (first_time and self._history_loaded) or (not hasattr(self, '_message_getter')):
            return
        data = list(self._message_getter.get(PAGE_SIZE))
        if data is not None and len(data):
            data.reverse()
        else:
            return
        data = list(map(lambda tupl: TextMessage(*tupl), data))
        self._corr = data + self._corr
        self._history_loaded = True

    def get_corr_for_saving(self):
        """
        Get data to save in db
        :return: list of unsaved messages or []
        """
        messages = list(filter(lambda x: x.get_type() <= 1, self._corr))
        return list(map(lambda x: x.get_data(), messages[-self._unsaved_messages:])) if self._unsaved_messages else []

    def get_corr(self):
        return self._corr[:]

    def append_message(self, message):
        """
        :param message: text or file transfer message
        """
        self._corr.append(message)
        if message.get_type() <= 1:
            self._unsaved_messages += 1

    def get_last_message_text(self):
        messages = list(filter(lambda x: x.get_type() <= 1 and x.get_owner() != MESSAGE_OWNER['FRIEND'], self._corr))
        if messages:
            return messages[-1].get_data()[0]
        else:
            return ''

    def get_unsent_messages(self):
        """
        :return list of unsent messages
        """
        messages = filter(lambda x: x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr)
        return list(messages)

    def get_unsent_messages_for_saving(self):
        """
        :return list of unsent messages for saving
        """
        messages = filter(lambda x: x.get_type() <= 1 and x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr)
        return list(map(lambda x: x.get_data(), messages))

    def delete_message(self, time):
        elem = list(filter(lambda x: type(x) is TextMessage and x.get_data()[2] == time, self._corr))[0]
        tmp = list(filter(lambda x: x.get_type() <= 1, self._corr))
        if elem in tmp[-self._unsaved_messages:]:
            self._unsaved_messages -= 1
        self._corr.remove(elem)

    def mark_as_sent(self):
        try:
            message = list(filter(lambda x: x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr))[0]
            message.mark_as_sent()
        except Exception as ex:
            util.log('Mark as sent ex: ' + str(ex))

    def clear_corr(self, save_unsent=False):
        """
        Clear messages list
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        # don't delete data about active file transfer
        if not save_unsent:
            self._corr = list(filter(lambda x: x.get_type() in (2, 3) and
                                               x.get_status() in ft.ACTIVE_FILE_TRANSFERS, self._corr))
            self._unsaved_messages = 0
        else:
            self._corr = list(filter(lambda x: (x.get_type() in (2, 3) and x.get_status() in ft.ACTIVE_FILE_TRANSFERS)
                                     or (x.get_type() <= 1 and x.get_owner() == MESSAGE_OWNER['NOT_SENT']),
                                     self._corr))
            self._unsaved_messages = len(self.get_unsent_messages())

    def get_curr_text(self):
        return self._curr_text

    def set_curr_text(self, value):
        self._curr_text = value

    curr_text = property(get_curr_text, set_curr_text)

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def update_transfer_data(self, file_number, status, inline=None):
        """
        Update status of active transfer and load inline if needed
        """
        try:
            tr = list(filter(lambda x: x.get_type() == MESSAGE_TYPE['FILE_TRANSFER'] and x.is_active(file_number),
                        self._corr))[0]
            tr.set_status(status)
            i = self._corr.index(tr)
            if inline:  # inline was loaded
                self._corr.insert(i, inline)
            return i - len(self._corr)
        except:
            pass

    def get_unsent_files(self):
        messages = filter(lambda x: type(x) is UnsentFile, self._corr)
        return messages

    def clear_unsent_files(self):
        self._corr = list(filter(lambda x: type(x) is not UnsentFile, self._corr))

    def delete_one_unsent_file(self, time):
        self._corr = list(filter(lambda x: not (type(x) is UnsentFile and x.get_data()[2] == time), self._corr))

    # -----------------------------------------------------------------------------------------------------------------
    # Alias support
    # -----------------------------------------------------------------------------------------------------------------

    def set_name(self, value):
        """
        Set new name or ignore if alias exists
        :param value: new name
        """
        if not self._alias:
            super(Friend, self).set_name(value)

    def set_alias(self, alias):
        self._alias = bool(alias)

    # -----------------------------------------------------------------------------------------------------------------
    # Visibility in friends' list
    # -----------------------------------------------------------------------------------------------------------------

    def get_visibility(self):
        return self._visible

    def set_visibility(self, value):
        self._visible = value

    visibility = property(get_visibility, set_visibility)

    # -----------------------------------------------------------------------------------------------------------------
    # Unread messages from friend
    # -----------------------------------------------------------------------------------------------------------------

    def get_actions(self):
        return self._new_actions

    def set_actions(self, value):
        self._new_actions = value
        self._widget.connection_status.update(self.status, value)

    actions = property(get_actions, set_actions)  # unread messages, incoming files, av calls

    def get_messages(self):
        return self._new_messages

    def inc_messages(self):
        self._new_messages += 1
        self._new_actions = True
        self._widget.connection_status.update(self.status, True)
        self._widget.messages.update(self._new_messages)

    def reset_messages(self):
        self._new_actions = False
        self._new_messages = 0
        self._widget.messages.update(self._new_messages)
        self._widget.connection_status.update(self.status, False)

    messages = property(get_messages)

    # -----------------------------------------------------------------------------------------------------------------
    # Friend's number (can be used in toxcore)
    # -----------------------------------------------------------------------------------------------------------------

    def get_number(self):
        return self._number

    def set_number(self, value):
        self._number = value

    number = property(get_number, set_number)
