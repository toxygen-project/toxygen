# TODO: add support of file transfers
# TODO: add support of avatars
from toxcore_enums_and_consts import TOX_FILE_KIND
from os.path import basename, getsize


TOX_FILE_TRANSFER_STATE = {
    'RUNNING': 0,
    'PAUSED': 1,
    'CANCELED': 2,
    'FINISHED': 3,
}


class FileTransfer(object):
    def __init__(self, path, tox, friend_number, file_number = None):
        self._path = path
        self._tox = tox
        self._friend_number = friend_number
        self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        self._file_number = file_number

    def set_tox(self, tox):
        self._tox = tox

    def get_file_number(self):
        return self._file_number

    def get_friend_number(self):
        return self._friend_number

    def send_control(self, control):
        if self._tox.file_control(self._friend_number, self._file_number, control):
            self.state = control

    def get_file_id(self):
        return self._tox.file_get_file_id(self._friend_number, self._file_number)

    def file_seek(self):
        # TODO implement
        pass


class SendTransfer(FileTransfer):
    def __init__(self, path, tox, friend_number):
        super(self.__class__, self).__init__(path, tox, friend_number)
        self._file_number = tox.file_send(friend_number, TOX_FILE_KIND['DATA'], getsize(path), None, basename(path))
        self._file = open(path, 'rb')

    def send_chunk(self, position, size):
        self._file.seek(position)
        data = self._file.read(size)
        return self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)


class ReceiveTransfer(FileTransfer):
    def __init__(self, path, tox, friend_number, file_number):
        super(self.__class__, self).__init__(path, tox, friend_number, file_number)
        self._file = open(self._path, 'wb')
        self._file.truncate(0)
        self._size = 0

    def write_chunk(self, position, data):
        if data is not None:
            data = ''.join(chr(x) for x in data)
            if self._size < position:
                self._file.seek(0, 2)
                self._file.write('\0' * (position - self._size))
            self._file.seek(position)
            self._file.write(data)
            self._file.flush()
            if position + len(data) > self._size:
                self._size = position + len(data)
        else:
            self._file.close()
