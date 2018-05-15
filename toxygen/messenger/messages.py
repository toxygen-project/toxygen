from history.database import MESSAGE_AUTHOR
from ui.messages_widgets import *


MESSAGE_TYPE = {
    'TEXT': 0,
    'ACTION': 1,
    'FILE_TRANSFER': 2,
    'INLINE': 3,
    'INFO_MESSAGE': 4
}

PAGE_SIZE = 42


class MessageAuthor:

    def __init__(self, author_name, author_type):
        self.name = author_name
        self.type = author_type


class Message:

    def __init__(self, message_type, author, time):
        self._time = time
        self._type = message_type
        self._author = author
        self._widget = None

    def get_type(self):
        return self._type

    type = property(get_type)

    def get_author(self):
        return self._author

    author = property(get_author)

    def get_time(self):
        return self._time

    time = property(get_time)

    def get_widget(self, *args):
        if self._widget is None:
            self._widget = self._create_widget(*args)

        return self._widget

    widget = property(get_widget)

    def remove_widget(self):
        self._widget = None

    def mark_as_sent(self):
        self._author.author_type = MESSAGE_AUTHOR['ME']

    def _create_widget(self, *args):
        pass


class TextMessage(Message):
    """
    Plain text or action message
    """

    def __init__(self, message, owner, time, message_type):
        super().__init__(message_type, owner, time)
        self._message = message

    def get_text(self):
        return self._message

    text = property(get_text)

    def get_data(self):
        return self._message, self._owner, self._time, self._type

    def _create_widget(self, *args):
        return MessageItem(self, *args)


class OutgoingTextMessage(TextMessage):

    def __init__(self, message, owner, time, message_type, tox_message_id):
        super().__init__(message, owner, time, message_type)
        self._tox_message_id = tox_message_id

    def get_tox_message_id(self):
        return self._tox_message_id

    tox_message_id = property(get_tox_message_id)


class GroupChatMessage(TextMessage):

    def __init__(self, id, message, owner, time, message_type, name):
        super().__init__(id, message, owner, time, message_type)
        self._user_name = name

    def get_data(self):
        return self._message, self._owner, self._time, self._type, self._user_name


class TransferMessage(Message):
    """
    Message with info about file transfer
    """

    def __init__(self, owner, time, status, size, name, friend_number, file_number):
        super().__init__(MESSAGE_TYPE['FILE_TRANSFER'], owner, time)
        self._status = status
        self._size = size
        self._file_name = name
        self._friend_number, self._file_number = friend_number, file_number

    def is_active(self, file_number):
        return self._file_number == file_number and self._status not in (2, 3)

    def get_friend_number(self):
        return self._friend_number

    def get_file_number(self):
        return self._file_number

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    def get_data(self):
        return self._file_name, self._size, self._time, self._owner, self._friend_number, self._file_number, self._status


class UnsentFile(Message):
    def __init__(self, id, path, data, time):
        super().__init__(id, MESSAGE_TYPE['FILE_TRANSFER'], 0, time)
        self._data, self._path = data, path

    def get_data(self):
        return self._path, self._data, self._time

    def get_status(self):
        return None


class InlineImage(Message):
    """
    Inline image
    """

    def __init__(self, id, data):
        super().__init__(id, MESSAGE_TYPE['INLINE'], None, None)
        self._data = data

    def get_data(self):
        return self._data


class InfoMessage(TextMessage):

    def __init__(self, id, message, time):
        super().__init__(id, message, None, time, MESSAGE_TYPE['INFO_MESSAGE'])