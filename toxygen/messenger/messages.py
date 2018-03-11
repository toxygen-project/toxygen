

MESSAGE_TYPE = {
    'TEXT': 0,
    'ACTION': 1,
    'FILE_TRANSFER': 2,
    'INLINE': 3,
    'INFO_MESSAGE': 4
}


class Message:

    def __init__(self, message_id, message_type, owner, time):
        self._time = time
        self._type = message_type
        self._owner = owner
        self._message_id = message_id

    def get_type(self):
        return self._type

    def get_owner(self):
        return self._owner

    def mark_as_sent(self):
        self._owner = 0

    def get_message_id(self):
        return self._message_id

    message_id = property(get_message_id)


class TextMessage(Message):
    """
    Plain text or action message
    """

    def __init__(self, id, message, owner, time, message_type):
        super(TextMessage, self).__init__(id, message_type, owner, time)
        self._message = message

    def get_data(self):
        return self._message, self._owner, self._time, self._type


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

    def __init__(self, id, owner, time, status, size, name, friend_number, file_number):
        super(TransferMessage, self).__init__(MESSAGE_TYPE['FILE_TRANSFER'], owner, time)
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
        super(UnsentFile, self).__init__(id, MESSAGE_TYPE['FILE_TRANSFER'], 0, time)
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
        super(InlineImage, self).__init__(id, MESSAGE_TYPE['INLINE'], None, None)
        self._data = data

    def get_data(self):
        return self._data


class InfoMessage(TextMessage):

    def __init__(self, id, message, time):
        super(InfoMessage, self).__init__(id, message, None, time, MESSAGE_TYPE['INFO_MESSAGE'])
