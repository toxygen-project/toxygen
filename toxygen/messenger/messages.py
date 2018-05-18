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

    MESSAGE_ID = 0

    def __init__(self, message_type, author, time):
        self._time = time
        self._type = message_type
        self._author = author
        self._widget = None
        self._message_id = self._get_id()

    def get_type(self):
        return self._type

    type = property(get_type)

    def get_author(self):
        return self._author

    author = property(get_author)

    def get_time(self):
        return self._time

    time = property(get_time)

    def get_message_id(self):
        return self._message_id

    message_id = property(get_message_id)

    def get_widget(self, *args):
        if self._widget is None:
            self._widget = self._create_widget(*args)

        return self._widget

    widget = property(get_widget)

    def remove_widget(self):
        self._widget = None

    def mark_as_sent(self):
        self._author.author_type = MESSAGE_AUTHOR['ME']
        if self._widget is not None:
            self._widget.mark_as_sent()

    def _create_widget(self, *args):
        pass

    @staticmethod
    def _get_id():
        Message.MESSAGE_ID += 1

        return int(Message.MESSAGE_ID)


class TextMessage(Message):
    """
    Plain text or action message
    """

    def __init__(self, message, owner, time, message_type, message_id=0):
        super().__init__(message_type, owner, time)
        self._message = message
        self._id = message_id

    def get_text(self):
        return self._message

    text = property(get_text)

    def get_id(self):
        return self._id

    id = property(get_id)

    def is_saved(self):
        return self._id > 0

    def _create_widget(self, *args):
        return MessageItem(self, *args)


class OutgoingTextMessage(TextMessage):

    def __init__(self, message, owner, time, message_type, tox_message_id):
        super().__init__(message, owner, time, message_type)
        self._tox_message_id = tox_message_id

    def get_tox_message_id(self):
        return self._tox_message_id

    def set_tox_message_id(self, tox_message_id):
        self._tox_message_id = tox_message_id

    tox_message_id = property(get_tox_message_id, set_tox_message_id)


class GroupChatMessage(TextMessage):

    def __init__(self, id, message, owner, time, message_type, name):
        super().__init__(id, message, owner, time, message_type)
        self._user_name = name


class TransferMessage(Message):
    """
    Message with info about file transfer
    """

    def __init__(self, author, time, state, size, file_name, friend_number, file_number):
        super().__init__(MESSAGE_TYPE['FILE_TRANSFER'], author, time)
        self._state = state
        self._size = size
        self._file_name = file_name
        self._friend_number, self._file_number = friend_number, file_number

    def is_active(self, file_number):
        return self._file_number == file_number and self._state not in (2, 3)

    def get_friend_number(self):
        return self._friend_number

    friend_number = property(get_friend_number)

    def get_file_number(self):
        return self._file_number

    file_number = property(get_file_number)

    def get_state(self):
        return self._state

    def set_state(self, value):
        self._state = value

    state = property(get_state, set_state)

    def get_size(self):
        return self._size

    size = property(get_size)

    def get_file_name(self):
        return self._file_name

    file_name = property(get_file_name)

    def transfer_updated(self, state, percentage, time):
        self._state = state
        if self._widget is not None:
            self._widget.update_transfer_state(state, percentage, time)

    def _create_widget(self, *args):
        return FileTransferItem(self, *args)


class UnsentFileMessage(Message):

    def __init__(self, path, data, time):
        super().__init__(MESSAGE_TYPE['FILE_TRANSFER'], 0, time)
        self._data, self._path = data, path

    def get_data(self):
        return self._data

    data = property(get_data)

    def get_state(self):
        return FILE_TRANSFER_STATE['UNSENT']

    state = property(get_state)

    def get_path(self):
        return self._path

    path = property(get_path)

    def _create_widget(self, *args):
        return UnsentFileItem(self, *args)


class InlineImageMessage(Message):
    """
    Inline image
    """

    def __init__(self, data):
        super().__init__(MESSAGE_TYPE['INLINE'], None, None)
        self._data = data

    def get_data(self):
        return self._data

    data = property(get_data)

    def _create_widget(self, *args):
        return InlineImageItem(self, *args)


class InfoMessage(TextMessage):

    def __init__(self, message, time):
        super().__init__(message, None, time, MESSAGE_TYPE['INFO_MESSAGE'])
