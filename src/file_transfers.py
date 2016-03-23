from toxcore_enums_and_consts import TOX_FILE_KIND, TOX_FILE_CONTROL
from os.path import basename, getsize, exists
from os import remove
from time import time
from tox import Tox
import profile
from PySide import QtCore


TOX_FILE_TRANSFER_STATE = {
    'RUNNING': 0,
    'PAUSED': 1,
    'CANCELED': 2,
    'FINISHED': 3,
}


class StateSignal(QtCore.QObject):
    signal = QtCore.Signal(int, float)


class FileTransfer(QtCore.QObject):

    def __init__(self, path, tox, friend_number, size, file_number=None):
        QtCore.QObject.__init__(self)
        self._path = path
        self._tox = tox
        self._friend_number = friend_number
        self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        self._file_number = file_number
        self._creation_time = time()
        self._size = float(size)
        self._done = 0
        self._state_changed = StateSignal()

    def set_tox(self, tox):
        self._tox = tox

    def set_state_changed_handler(self, handler):
        self._state_changed.signal.connect(handler)

    def get_file_number(self):
        return self._file_number

    def get_friend_number(self):
        return self._friend_number

    def cancel(self):
        self.send_control(TOX_FILE_CONTROL['CANCEL'])
        if hasattr(self, '_file'):
            print 'closing'
            self._file.close()
        self._state_changed.signal.emit(self.state, self._done / self._size)

    def cancelled(self):
        if hasattr(self, '_file'):
            self._file.close()
        self._state_changed.signal.emit(TOX_FILE_CONTROL['CANCEL'], self._done / self._size if self._size else 0)

    def send_control(self, control):
        if self._tox.file_control(self._friend_number, self._file_number, control):
            self.state = control
            self._state_changed.signal.emit(self.state, self._done / self._size if self._size else 0)

    def get_file_id(self):
        return self._tox.file_get_file_id(self._friend_number, self._file_number)

    def file_seek(self):
        # TODO implement or not implement
        pass

# -----------------------------------------------------------------------------------------------------------------
# Send file
# -----------------------------------------------------------------------------------------------------------------


class SendTransfer(FileTransfer):

    def __init__(self, path, tox, friend_number, kind=TOX_FILE_KIND['DATA'], file_id=None):
        if path is not None:
            self._file = open(path, 'rb')
            size = getsize(path)
        else:
            size = 0
        super(SendTransfer, self).__init__(path, tox, friend_number, size)
        self._file_number = tox.file_send(friend_number, kind, size, file_id,
                                          basename(path).encode('utf-8') if path else '')

    def send_chunk(self, position, size):
        if size:
            self._file.seek(position)
            data = self._file.read(size)
            self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
            self._done += size
            self._state_changed.signal.emit(self.state, self._done / self._size)
        else:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self._state_changed.signal.emit(self.state, 1)


class SendAvatar(SendTransfer):

    def __init__(self, path, tox, friend_number):
        if path is None:
            hash = None
        else:
            with open(path, 'rb') as fl:
                hash = Tox.hash(fl.read())
        super(SendAvatar, self).__init__(path, tox, friend_number, TOX_FILE_KIND['AVATAR'], hash)


class SendFromBuffer(FileTransfer):

    def __init__(self, tox, friend_number, data, file_name):
        super(SendFromBuffer, self).__init__(None, tox, friend_number, len(data))
        self._data = data
        self._file_number = tox.file_send(friend_number, TOX_FILE_KIND['DATA'], len(data), None, file_name)

    def send_chunk(self, position, size):
        if size:
            data = self._data[position:position + size]
            self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
            self._done += size
            self._state_changed.signal.emit(self.state, self._done / self._size)
        else:
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self._state_changed.signal.emit(self.state, 1)

# -----------------------------------------------------------------------------------------------------------------
# Receive file
# -----------------------------------------------------------------------------------------------------------------


class ReceiveTransfer(FileTransfer):

    def __init__(self, path, tox, friend_number, size, file_number):
        super(ReceiveTransfer, self).__init__(path, tox, friend_number, size, file_number)
        self._file = open(self._path, 'wb')
        self._file.truncate(0)
        self._file_size = 0

    def cancel(self):
        super(ReceiveTransfer, self).cancel()
        remove(self._path)

    def write_chunk(self, position, data):
        if data is None:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self._state_changed.signal.emit(self.state, self._done / self._size if self._size else 0)
        else:
            data = ''.join(chr(x) for x in data)
            if self._file_size < position:
                self._file.seek(0, 2)
                self._file.write('\0' * (position - self._file_size))
            self._file.seek(position)
            self._file.write(data)
            self._file.flush()
            l = len(data)
            if position + l > self._file_size:
                self._file_size = position + l
            self._done += l
            self._state_changed.signal.emit(self.state, self._done / self._size)


class ReceiveAvatar(ReceiveTransfer):

    def __init__(self, tox, friend_number, size, file_number):
        path = profile.ProfileHelper.get_path() + '/avatars/{}.png'.format(tox.friend_get_public_key(friend_number))
        super(ReceiveAvatar, self).__init__(path, tox, friend_number, size, file_number)
        if exists(path):
            if not size:
                self.send_control(TOX_FILE_CONTROL['CANCEL'])
                self.state = TOX_FILE_TRANSFER_STATE['CANCELED']
                self._file.close()
                remove(path)
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
