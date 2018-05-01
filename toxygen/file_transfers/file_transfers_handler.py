from file_transfers.file_transfers import *
from messenger.messages import *
from history.database import MESSAGE_AUTHOR
import os
import util.util as util


class FileTransfersHandler:

    def __init__(self, tox, settings, contact_provider):
        self._tox = tox
        self._settings = settings
        self._contact_provider = contact_provider
        self._file_transfers = {}
        # key = (friend number, file number), value - transfer instance
        self._paused_file_transfers = dict(settings['paused_file_transfers'])
        # key - file id, value: [path, friend number, is incoming, start position]
        
    def __del__(self):
        self._settings['paused_file_transfers'] = self._paused_file_transfers if self._settings['resend_files'] else {}
        self._settings.save()

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def incoming_file_transfer(self, friend_number, file_number, size, file_name):
        """
        New transfer
        :param friend_number: number of friend who sent file
        :param file_number: file number
        :param size: file size in bytes
        :param file_name: file name without path
        """
        friend = self._get_friend_by_number(friend_number)
        auto = self._settings['allow_auto_accept'] and friend.tox_id in self._settings['auto_accept_from_friends']
        inline = is_inline(file_name) and self._settings['allow_inline']
        file_id = self._tox.file_get_file_id(friend_number, file_number)
        accepted = True
        if file_id in self._paused_file_transfers:
            data = self._paused_file_transfers[file_id]
            pos = data[-1] if os.path.exists(data[0]) else 0
            if pos >= size:
                self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
                return
            self._tox.file_seek(friend_number, file_number, pos)
            self.accept_transfer(None, data[0], friend_number, file_number, size, False, pos)
            tm = TransferMessage(MESSAGE_AUTHOR['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['RUNNING'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)
        elif inline and size < 1024 * 1024:
            self.accept_transfer(None, '', friend_number, file_number, size, True)
            tm = TransferMessage(MESSAGE_AUTHOR['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['RUNNING'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)

        elif auto:
            path = self._settings['auto_accept_path'] or util.curr_directory()
            self.accept_transfer(None, path + '/' + file_name, friend_number, file_number, size)
            tm = TransferMessage(MESSAGE_AUTHOR['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['RUNNING'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)
        else:
            tm = TransferMessage(MESSAGE_AUTHOR['FRIEND'],
                                 time.time(),
                                 TOX_FILE_TRANSFER_STATE['INCOMING_NOT_STARTED'],
                                 size,
                                 file_name,
                                 friend_number,
                                 file_number)
            accepted = False
        if friend_number == self.get_active_number() and self.is_active_a_friend():
            item = self.create_file_transfer_item(tm)
            if accepted:
                self._file_transfers[(friend_number, file_number)].set_state_changed_handler(item.update_transfer_state)
            self._messages.scrollToBottom()
        else:
            friend.actions = True

        friend.append_message(tm)

    def cancel_transfer(self, friend_number, file_number, already_cancelled=False):
        """
        Stop transfer
        :param friend_number: number of friend
        :param file_number: file number
        :param already_cancelled: was cancelled by friend
        """
        i = self._get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                          TOX_FILE_TRANSFER_STATE['CANCELLED'])
        if (friend_number, file_number) in self._file_transfers:
            tr = self._file_transfers[(friend_number, file_number)]
            if not already_cancelled:
                tr.cancel()
            else:
                tr.cancelled()
            if (friend_number, file_number) in self._file_transfers:
                del tr
                del self._file_transfers[(friend_number, file_number)]
        else:
            if not already_cancelled:
                self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
            if friend_number == self.get_active_number() and self.is_active_a_friend():
                tmp = self._messages.count() + i
                if tmp >= 0:
                    self._messages.itemWidget(
                        self._messages.item(tmp)).update_transfer_state(TOX_FILE_TRANSFER_STATE['CANCELLED'],
                                                                        0, -1)

    def cancel_not_started_transfer(self, cancel_time):
        self.get_curr_friend().delete_one_unsent_file(cancel_time)
        self.update()

    def pause_transfer(self, friend_number, file_number, by_friend=False):
        """
        Pause transfer with specified data
        """
        tr = self._file_transfers[(friend_number, file_number)]
        tr.pause(by_friend)
        t = TOX_FILE_TRANSFER_STATE['PAUSED_BY_FRIEND'] if by_friend else TOX_FILE_TRANSFER_STATE['PAUSED_BY_USER']
        self.get_friend_by_number(friend_number).update_transfer_data(file_number, t)

    def resume_transfer(self, friend_number, file_number, by_friend=False):
        """
        Resume transfer with specified data
        """
        # self.get_friend_by_number(friend_number).update_transfer_data(file_number,
        #                                                               TOX_FILE_TRANSFER_STATE['RUNNING'])
        tr = self._file_transfers[(friend_number, file_number)]
        if by_friend:
            tr.state = TOX_FILE_TRANSFER_STATE['RUNNING']
            tr.signal()
        else:
            tr.send_control(TOX_FILE_CONTROL['RESUME'])

    def accept_transfer(self, item, path, friend_number, file_number, size, inline=False, from_position=0):
        """
        :param item: transfer item.
        :param path: path for saving
        :param friend_number: friend number
        :param file_number: file number
        :param size: file size
        :param inline: is inline image
        :param from_position: position for start
        """
        path, file_name = os.path.split(path)
        new_file_name, i = file_name, 1
        if not from_position:
            while os.path.isfile(path + '/' + new_file_name):  # file with same name already exists
                if '.' in file_name:  # has extension
                    d = file_name.rindex('.')
                else:  # no extension
                    d = len(file_name)
                new_file_name = file_name[:d] + ' ({})'.format(i) + file_name[d:]
                i += 1
        path = os.path.join(path, new_file_name)
        if not inline:
            rt = ReceiveTransfer(path, self._tox, friend_number, size, file_number, from_position)
        else:
            rt = ReceiveToBuffer(self._tox, friend_number, size, file_number)
        rt.set_transfer_finished_handler(self.transfer_finished)
        self._file_transfers[(friend_number, file_number)] = rt
        self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['RESUME'])
        if item is not None:
            rt.set_state_changed_handler(item.update_transfer_state)
        self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                      TOX_FILE_TRANSFER_STATE['RUNNING'])

    def send_screenshot(self, data):
        """
        Send screenshot to current active friend
        :param data: raw data - png
        """
        self.send_inline(data, 'toxygen_inline.png')

    def send_sticker(self, path):
        with open(path, 'rb') as fl:
            data = fl.read()
        self.send_inline(data, 'sticker.png')

    def send_inline(self, data, file_name, friend_number=None, is_resend=False):
        friend_number = friend_number or self.get_active_number()
        friend = self.get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            m = UnsentFile(file_name, data, time.time())
            friend.append_message(m)
            self.update()
            return
        elif friend.status is None and is_resend:
            raise RuntimeError()
        st = SendFromBuffer(self._tox, friend.number, data, file_name)
        st.set_transfer_finished_handler(self.transfer_finished)
        self._file_transfers[(friend.number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_AUTHOR['ME'],
                             time.time(),
                             TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED'],
                             len(data),
                             file_name,
                             friend.number,
                             st.get_file_number())
        item = self.create_file_transfer_item(tm)
        friend.append_message(tm)
        st.set_state_changed_handler(item.update_transfer_state)
        self._messages.scrollToBottom()

    def send_file(self, path, number=None, is_resend=False, file_id=None):
        """
        Send file to current active friend
        :param path: file path
        :param number: friend_number
        :param is_resend: is 'offline' message
        :param file_id: file id of transfer
        """
        friend_number = self.get_active_number() if number is None else number
        friend = self.get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            m = UnsentFile(path, None, time.time())
            friend.append_message(m)
            self.update()
            return
        elif friend.status is None and is_resend:
            print('Error in sending')
            raise RuntimeError()
        st = SendTransfer(path, self._tox, friend_number, TOX_FILE_KIND['DATA'], file_id)
        st.set_transfer_finished_handler(self.transfer_finished)
        self._file_transfers[(friend_number, st.get_file_number())] = st
        tm = TransferMessage(MESSAGE_AUTHOR['ME'],
                             time.time(),
                             TOX_FILE_TRANSFER_STATE['OUTGOING_NOT_STARTED'],
                             os.path.getsize(path),
                             os.path.basename(path),
                             friend_number,
                             st.get_file_number())
        if friend_number == self.get_active_number():
            item = self.create_file_transfer_item(tm)
            st.set_state_changed_handler(item.update_transfer_state)
            self._messages.scrollToBottom()
        self._contacts[friend_number].append_message(tm)

    def incoming_chunk(self, friend_number, file_number, position, data):
        """
        Incoming chunk
        """
        self._file_transfers[(friend_number, file_number)].write_chunk(position, data)

    def outgoing_chunk(self, friend_number, file_number, position, size):
        """
        Outgoing chunk
        """
        self._file_transfers[(friend_number, file_number)].send_chunk(position, size)

    def transfer_finished(self, friend_number, file_number):
        transfer = self._file_transfers[(friend_number, file_number)]
        t = type(transfer)
        if t is ReceiveAvatar:
            self.get_friend_by_number(friend_number).load_avatar()
            if friend_number == self.get_active_number() and self.is_active_a_friend():
                self.set_active(None)
        elif t is ReceiveToBuffer or (t is SendFromBuffer and self._settings.get_instance()['allow_inline']):  # inline image
            print('inline')
            inline = InlineImage(transfer.get_data())
            i = self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                              TOX_FILE_TRANSFER_STATE['FINISHED'],
                                                                              inline)
            if friend_number == self.get_active_number() and self.is_active_a_friend():
                count = self._messages.count()
                if count + i + 1 >= 0:
                    elem = QtWidgets.QListWidgetItem()
                    item = InlineImageItem(transfer.get_data(), self._messages.width(), elem)
                    elem.setSizeHint(QtCore.QSize(self._messages.width(), item.height()))
                    self._messages.insertItem(count + i + 1, elem)
                    self._messages.setItemWidget(elem, item)
                    self._messages.scrollToBottom()
        elif t is not SendAvatar:
            self.get_friend_by_number(friend_number).update_transfer_data(file_number,
                                                                          TOX_FILE_TRANSFER_STATE['FINISHED'])
        del self._file_transfers[(friend_number, file_number)]
        del transfer

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars support
    # -----------------------------------------------------------------------------------------------------------------

    def send_avatar(self, friend_number, avatar_path=None):
        """
        :param friend_number: number of friend who should get new avatar
        :param avatar_path: path to avatar or None if reset
        """
        sa = SendAvatar(avatar_path, self._tox, friend_number)
        self._file_transfers[(friend_number, sa.get_file_number())] = sa

    def incoming_avatar(self, friend_number, file_number, size):
        """
        Friend changed avatar
        :param friend_number: friend number
        :param file_number: file number
        :param size: size of avatar or 0 (default avatar)
        """
        ra = ReceiveAvatar(self._tox, friend_number, size, file_number)
        if ra.state != TOX_FILE_TRANSFER_STATE['CANCELLED']:
            self._file_transfers[(friend_number, file_number)] = ra
            ra.set_transfer_finished_handler(self.transfer_finished)
        else:
            self.get_friend_by_number(friend_number).load_avatar()
            if self.get_active_number() == friend_number and self.is_active_a_friend():
                self.set_active(None)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _get_friend_by_number(self, friend_number):
        return self._contact_provider.get_friend_by_number(friend_number)
