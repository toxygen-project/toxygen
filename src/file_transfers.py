# TODO: add support of file transfers
# TODO: add support of avatars
from toxcore_enums_and_consts import TOX_FILE_KIND
from os.path import basename, getsize


class FileTransfer(object):
    def __init__(self, path, tox, friend_number):
        self._path = path
        self._tox = tox
        self._friend_number = friend_number

    def set_tox(self, tox):
        self._tox = tox


class SendTransfer(FileTransfer):
    def __init__(self, path, tox, friend_number):
        super(self.__class__, self).__init__(path, tox, friend_number)
        self._file_number = tox.file_send(friend_number, TOX_FILE_KIND['DATA'], getsize(path), None, basename(path))

    def get_file_number(self):
        return self._file_number

    def send_chunk(self, position, size):
        with open(self._path) as f:
            f.seek(position)
            data = f.read(size)
        return self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)


class ReceiveTransfer(FileTransfer):
    def __init__(self, path, tox, friend_number):
        super(self.__class__, self).__init__(path, tox, friend_number)

    def write_chunk(self, position, data):
        size = getsize(self._path)
        if size < position + len(data):
            with open(self._path, 'w') as f:
                f.write('\0' * (position + len(data) - size))
                f.seek(position)
                f.write(data)
        else:
            with open(self._path, 'w') as f:
                f.seek(position)
                f.write(data)
