from toxcore_enums_and_consts import TOX_FILE_KIND, TOX_FILE_CONTROL
from os.path import basename, getsize, exists
from os import remove
from time import time
from tox import Tox
import profile


TOX_FILE_TRANSFER_STATE = {
    'RUNNING': 0,
    'PAUSED': 1,
    'CANCELED': 2,
    'FINISHED': 3,
}


class FileTransfer(object):
    def __init__(self, path, tox, friend_number, file_number=None):
        self._path = path
        self._tox = tox
        self._friend_number = friend_number
        self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        self._file_number = file_number
        self._creation_time = time()

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
    def __init__(self, path, tox, friend_number, kind=TOX_FILE_KIND['DATA'], file_id=None):
        super(SendTransfer, self).__init__(path, tox, friend_number)
        self._file_number = tox.file_send(friend_number,
                                          kind,
                                          getsize(path) if path else 0,
                                          file_id,
                                          basename(path) if path else '')
        if path is not None:
            self._file = open(path, 'rb')

    def send_chunk(self, position, size):
        if size:
            self._file.seek(position)
            data = self._file.read(size)
            return self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
        else:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']


class SendAvatar(SendTransfer):
    def __init__(self, path, tox, friend_number):
        if path is None:
            super(SendAvatar, self).__init__(path, tox, friend_number, TOX_FILE_KIND['AVATAR'])
        else:
            with open(path, 'rb') as fl:
                hash = Tox.hash(fl.read())
            super(self.__class__, self).__init__(path, tox, friend_number, TOX_FILE_KIND['AVATAR'], hash)


class ReceiveTransfer(FileTransfer):
    def __init__(self, path, tox, friend_number, file_number):
        super(ReceiveTransfer, self).__init__(path, tox, friend_number, file_number)
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
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']


class ReceiveAvatar(ReceiveTransfer):
    def __init__(self, tox, friend_number, file_number, has_size=True):
        path = profile.ProfileHelper.get_path() + '/avatars/{}.png'.format(tox.friend_get_public_key(friend_number))
        super(ReceiveAvatar, self).__init__(path, tox, friend_number, file_number)
        if exists(path):
            if not has_size:
                remove(path)
                self.send_control(TOX_FILE_CONTROL['CANCEL'])
                self.state = TOX_FILE_TRANSFER_STATE['CANCELED']
            else:
                hash = self.get_file_id()
                with open(path, 'rb') as fl:
                    existing_hash = Tox.hash(fl.read())
                if hash == existing_hash:
                    self.send_control(TOX_FILE_CONTROL['CANCEL'])
                    self.state = TOX_FILE_TRANSFER_STATE['CANCELED']
                else:
                    self.send_control(TOX_FILE_CONTROL['RESUME'])
        else:
            self.send_control(TOX_FILE_CONTROL['RESUME'])
