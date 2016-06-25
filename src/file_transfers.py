from toxcore_enums_and_consts import TOX_FILE_KIND, TOX_FILE_CONTROL
from os.path import basename, getsize, exists, dirname
from os import remove, rename, chdir
from time import time, sleep
from tox import Tox
import settings
try:
    from PySide import QtCore
except ImportError:
    from PyQt4 import QtCore

# TODO: threads!


TOX_FILE_TRANSFER_STATE = {
    'RUNNING': 0,
    'PAUSED_BY_USER': 1,
    'CANCELLED': 2,
    'FINISHED': 3,
    'PAUSED_BY_FRIEND': 4,
    'INCOMING_NOT_STARTED': 5,
    'OUTGOING_NOT_STARTED': 6
}

ACTIVE_FILE_TRANSFERS = (0, 1, 4, 5, 6)

PAUSED_FILE_TRANSFERS = (1, 4, 5, 6)

DO_NOT_SHOW_ACCEPT_BUTTON = (2, 3, 4, 6)

SHOW_PROGRESS_BAR = (0, 1, 4)

ALLOWED_FILES = ('toxygen_inline.png', 'utox-inline.png', 'sticker.png')


class StateSignal(QtCore.QObject):
    try:
        signal = QtCore.Signal(int, float, int)  # state and progress
    except:
        signal = QtCore.pyqtSignal(int, float, int)  # state and progress - pyqt4


class FileTransfer(QtCore.QObject):
    """
    Superclass for file transfers
    """

    def __init__(self, path, tox, friend_number, size, file_number=None):
        QtCore.QObject.__init__(self)
        self._path = path
        self._tox = tox
        self._friend_number = friend_number
        self.state = TOX_FILE_TRANSFER_STATE['RUNNING']
        self._file_number = file_number
        self._creation_time = None
        self._size = float(size)
        self._done = 0
        self._state_changed = StateSignal()

    def set_tox(self, tox):
        self._tox = tox

    def set_state_changed_handler(self, handler):
        self._state_changed.signal.connect(handler)

    def signal(self):
        percentage = self._done / self._size if self._size else 0
        if self._creation_time is None or not percentage:
            t = -1
        else:
            t = ((time() - self._creation_time) / percentage) * (1 - percentage)
        self._state_changed.signal.emit(self.state, percentage, int(t))

    def get_file_number(self):
        return self._file_number

    def get_friend_number(self):
        return self._friend_number

    def cancel(self):
        self.send_control(TOX_FILE_CONTROL['CANCEL'])
        if hasattr(self, '_file'):
            self._file.close()
        self.signal()

    def cancelled(self):
        if hasattr(self, '_file'):
            sleep(0.1)
            self._file.close()
        self.state = TOX_FILE_TRANSFER_STATE['CANCELLED']
        self.signal()

    def pause(self, by_friend):
        if not by_friend:
            self.send_control(TOX_FILE_CONTROL['PAUSE'])
        else:
            self.state = TOX_FILE_TRANSFER_STATE['PAUSED_BY_FRIEND']
        self.signal()

    def send_control(self, control):
        if self._tox.file_control(self._friend_number, self._file_number, control):
            self.state = control
            self.signal()

    def get_file_id(self):
        return self._tox.file_get_file_id(self._friend_number, self._file_number)

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
        self.state = TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED']
        self._file_number = tox.file_send(friend_number, kind, size, file_id,
                                          bytes(basename(path), 'utf-8') if path else b'')

    def send_chunk(self, position, size):
        """
        Send chunk
        :param position: start position in file
        :param size: chunk max size
        """
        if self._creation_time is None:
            self._creation_time = time()
        if size:
            self._file.seek(position)
            data = self._file.read(size)
            self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
            self._done += size
            self.signal()
        else:
            if hasattr(self, '_file'):
                self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self.signal()


class SendAvatar(SendTransfer):
    """
    Send avatar to friend. Doesn't need file transfer item
    """

    def __init__(self, path, tox, friend_number):
        if path is None:
            hash = None
        else:
            with open(path, 'rb') as fl:
                hash = Tox.hash(fl.read())
        super(SendAvatar, self).__init__(path, tox, friend_number, TOX_FILE_KIND['AVATAR'], hash)


class SendFromBuffer(FileTransfer):
    """
    Send inline image
    """

    def __init__(self, tox, friend_number, data, file_name):
        super(SendFromBuffer, self).__init__(None, tox, friend_number, len(data))
        self.state = TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED']
        self._data = data
        self._file_number = tox.file_send(friend_number, TOX_FILE_KIND['DATA'],
                                          len(data), None, bytes(file_name, 'utf-8'))

    def get_data(self):
        return self._data

    def send_chunk(self, position, size):
        if self._creation_time is None:
            self._creation_time = time()
        if size:
            data = self._data[position:position + size]
            self._tox.file_send_chunk(self._friend_number, self._file_number, position, data)
            self._done += size
            self.signal()
        else:
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self.signal()


class SendFromFileBuffer(SendTransfer):

    def __init__(self, *args):
        super(SendFromFileBuffer, self).__init__(*args)

    def send_chunk(self, position, size):
        super(SendFromFileBuffer, self).send_chunk(position, size)
        if not size:
            chdir(dirname(self._path))
            remove(self._path)

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
        """
        Incoming chunk
        :param position: position in file to save data
        :param data: raw data (string)
        """
        if self._creation_time is None:
            self._creation_time = time()
        if data is None:
            self._file.close()
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
            self.signal()
        else:
            data = bytearray(data)
            if self._file_size < position:
                self._file.seek(0, 2)
                self._file.write(b'\0' * (position - self._file_size))
            self._file.seek(position)
            self._file.write(data)
            l = len(data)
            if position + l > self._file_size:
                self._file_size = position + l
            self._done += l
            self.signal()


class ReceiveToBuffer(FileTransfer):
    """
    Inline image - save in buffer not in file system
    """

    def __init__(self, tox, friend_number, size, file_number):
        super(ReceiveToBuffer, self).__init__(None, tox, friend_number, size, file_number)
        self._data = bytes()
        self._data_size = 0

    def get_data(self):
        return self._data

    def write_chunk(self, position, data):
        if self._creation_time is None:
            self._creation_time = time()
        if data is None:
            self.state = TOX_FILE_TRANSFER_STATE['FINISHED']
        else:
            data = bytes(data)
            l = len(data)
            if self._data_size < position:
                self._data += (b'\0' * (position - self._data_size))
            self._data = self._data[:position] + data + self._data[position + l:]
            if position + l > self._data_size:
                self._data_size = position + l
            self._done += l
        self.signal()


class ReceiveAvatar(ReceiveTransfer):
    """
    Get friend's avatar. Doesn't need file transfer item
    """
    MAX_AVATAR_SIZE = 512 * 1024

    def __init__(self, tox, friend_number, size, file_number):
        path = settings.ProfileHelper.get_path() + 'avatars/{}.png'.format(tox.friend_get_public_key(friend_number))
        super(ReceiveAvatar, self).__init__(path + '.tmp', tox, friend_number, size, file_number)
        if size > self.MAX_AVATAR_SIZE:
            self.send_control(TOX_FILE_CONTROL['CANCEL'])
            self._file.close()
            remove(path + '.tmp')
        elif not size:
            self.send_control(TOX_FILE_CONTROL['CANCEL'])
            self._file.close()
            if exists(path):
                remove(path)
            self._file.close()
            remove(path + '.tmp')
        elif exists(path):
            hash = self.get_file_id()
            with open(path, 'rb') as fl:
                data = fl.read()
            existing_hash = Tox.hash(data)
            if hash == existing_hash:
                self.send_control(TOX_FILE_CONTROL['CANCEL'])
                self._file.close()
                remove(path + '.tmp')
            else:
                self.send_control(TOX_FILE_CONTROL['RESUME'])
        else:
            self.send_control(TOX_FILE_CONTROL['RESUME'])

    def write_chunk(self, position, data):
        super(ReceiveAvatar, self).write_chunk(position, data)
        if self.state:
            avatar_path = self._path[:-4]
            if exists(avatar_path):
                chdir(dirname(avatar_path))
                remove(avatar_path)
            rename(self._path, avatar_path)
