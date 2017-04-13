from PyQt5 import QtCore, QtGui
from history import *
import basecontact
import util
from messages import *
import file_transfers as ft
import re


class Contact(basecontact.BaseContact):
    """
    Class encapsulating TOX contact
    Properties: number, message getter, history etc. Base class for friend and gc classes
    """

    def __init__(self, message_getter, number, name, status_message, widget, tox_id):
        """
        :param message_getter: gets messages from db
        :param number: number of friend.
        """
        super().__init__(name, status_message, widget, tox_id)
        self._number = number
        self._new_messages = False
        self._visible = True
        self._alias = False
        self._message_getter = message_getter
        self._corr = []
        self._unsaved_messages = 0
        self._history_loaded = self._new_actions = False
        self._curr_text = self._search_string = ''
        self._search_index = 0

    def __del__(self):
        self.set_visibility(False)
        del self._widget
        if hasattr(self, '_message_getter'):
            del self._message_getter

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def load_corr(self, first_time=True):
        """
        :param first_time: friend became active, load first part of messages
        """
        if (first_time and self._history_loaded) or (not hasattr(self, '_message_getter')):
            return
        if self._message_getter is None:
            return
        data = list(self._message_getter.get(PAGE_SIZE))
        if data is not None and len(data):
            data.reverse()
        else:
            return
        data = list(map(lambda tupl: TextMessage(*tupl), data))
        self._corr = data + self._corr
        self._history_loaded = True

    def load_all_corr(self):
        """
        Get all chat history from db for current friend
        """
        data = list(self._message_getter.get_all())
        if data is not None and len(data):
            data.reverse()
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

    # -----------------------------------------------------------------------------------------------------------------
    # Unsent messages
    # -----------------------------------------------------------------------------------------------------------------

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

    def mark_as_sent(self):
        try:
            message = list(filter(lambda x: x.get_owner() == MESSAGE_OWNER['NOT_SENT'], self._corr))[0]
            message.mark_as_sent()
        except Exception as ex:
            util.log('Mark as sent ex: ' + str(ex))

    # -----------------------------------------------------------------------------------------------------------------
    # Message deletion
    # -----------------------------------------------------------------------------------------------------------------

    def delete_message(self, time):
        elem = list(filter(lambda x: type(x) is TextMessage and x.get_data()[2] == time, self._corr))[0]
        tmp = list(filter(lambda x: x.get_type() <= 1, self._corr))
        if elem in tmp[-self._unsaved_messages:] and self._unsaved_messages:
            self._unsaved_messages -= 1
        self._corr.remove(elem)
        self._message_getter.delete_one()
        self._search_index = 0

    def delete_old_messages(self):
        """
        Delete old messages (reduces RAM usage if messages saving is not enabled)
        """
        def save_message(x):
            if x.get_type() == 2 and (x.get_status() >= 2 or x.get_status() is None):
                return True
            return x.get_owner() == MESSAGE_OWNER['NOT_SENT']

        old = filter(save_message, self._corr[:-SAVE_MESSAGES])
        self._corr = list(old) + self._corr[-SAVE_MESSAGES:]
        text_messages = filter(lambda x: x.get_type() <= 1, self._corr)
        self._unsaved_messages = min(self._unsaved_messages, len(list(text_messages)))
        self._search_index = 0

    def clear_corr(self, save_unsent=False):
        """
        Clear messages list
        """
        if hasattr(self, '_message_getter'):
            del self._message_getter
        self._search_index = 0
        # don't delete data about active file transfer
        if not save_unsent:
            self._corr = list(filter(lambda x: x.get_type() == 2 and
                                               x.get_status() in ft.ACTIVE_FILE_TRANSFERS, self._corr))
            self._unsaved_messages = 0
        else:
            self._corr = list(filter(lambda x: (x.get_type() == 2 and x.get_status() in ft.ACTIVE_FILE_TRANSFERS)
                                               or (x.get_type() <= 1 and x.get_owner() == MESSAGE_OWNER['NOT_SENT']),
                                     self._corr))
            self._unsaved_messages = len(self.get_unsent_messages())

    # -----------------------------------------------------------------------------------------------------------------
    # Chat history search
    # -----------------------------------------------------------------------------------------------------------------

    def search_string(self, search_string):
        self._search_string, self._search_index = search_string, 0
        return self.search_prev()

    def search_prev(self):
        while True:
            l = len(self._corr)
            for i in range(self._search_index - 1, -l - 1, -1):
                if self._corr[i].get_type() > 1:
                    continue
                message = self._corr[i].get_data()[0]
                if re.search(self._search_string, message, re.IGNORECASE) is not None:
                    self._search_index = i
                    return i
            self._search_index = -l
            self.load_corr(False)
            if len(self._corr) == l:
                return None  # not found

    def search_next(self):
        if not self._search_index:
            return None
        for i in range(self._search_index + 1, 0):
            if self._corr[i].get_type() > 1:
                continue
            message = self._corr[i].get_data()[0]
            if re.search(self._search_string, message, re.IGNORECASE) is not None:
                self._search_index = i
                return i
        return None  # not found

    # -----------------------------------------------------------------------------------------------------------------
    # Current text - text from message area
    # -----------------------------------------------------------------------------------------------------------------

    def get_curr_text(self):
        return self._curr_text

    def set_curr_text(self, value):
        self._curr_text = value

    curr_text = property(get_curr_text, set_curr_text)

    # -----------------------------------------------------------------------------------------------------------------
    # Alias support
    # -----------------------------------------------------------------------------------------------------------------

    def set_name(self, value):
        """
        Set new name or ignore if alias exists
        :param value: new name
        """
        if not self._alias:
            super().set_name(value)

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

    def set_widget(self, widget):
        self._widget = widget
        self.init_widget()

    # -----------------------------------------------------------------------------------------------------------------
    # Unread messages and other actions from friend
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
