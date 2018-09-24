from messenger.messages import *
from ui.contact_items import *
import utils.util as util
from common.tox_save import ToxSave


class FileTransfersHandler(ToxSave):

    def __init__(self, tox, settings, contact_provider, file_transfers_message_service, profile):
        super().__init__(tox)
        self._settings = settings
        self._contact_provider = contact_provider
        self._file_transfers_message_service = file_transfers_message_service
        self._file_transfers = {}
        # key = (friend number, file number), value - transfer instance
        self._paused_file_transfers = dict(settings['paused_file_transfers'])
        # key - file id, value: [path, friend number, is incoming, start position]
        self._insert_inline_before = {}
        # key = (friend number, file number), value - message id

        profile.avatar_changed_event.add_callback(self._send_avatar_to_contacts)
        
    def stop(self):
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
            (path, ft_friend_number, is_incoming, start_position) = self._paused_file_transfers[file_id]
            pos = start_position if os.path.exists(path) else 0
            if pos >= size:
                self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])
                return
            self._tox.file_seek(friend_number, file_number, pos)
            self._file_transfers_message_service.add_incoming_transfer_message(
                friend, accepted, size, file_name, file_number)
            self.accept_transfer(path, friend_number, file_number, size, False, pos)
        elif inline and size < 1024 * 1024:
            self._file_transfers_message_service.add_incoming_transfer_message(
                friend, accepted, size, file_name, file_number)
            self.accept_transfer('', friend_number, file_number, size, True)
        elif auto:
            path = self._settings['auto_accept_path'] or util.curr_directory()
            self._file_transfers_message_service.add_incoming_transfer_message(
                friend, accepted, size, file_name, file_number)
            self.accept_transfer(path + '/' + file_name, friend_number, file_number, size)
        else:
            accepted = False
            self._file_transfers_message_service.add_incoming_transfer_message(
                friend, accepted, size, file_name, file_number)

    def cancel_transfer(self, friend_number, file_number, already_cancelled=False):
        """
        Stop transfer
        :param friend_number: number of friend
        :param file_number: file number
        :param already_cancelled: was cancelled by friend
        """
        if (friend_number, file_number) in self._file_transfers:
            tr = self._file_transfers[(friend_number, file_number)]
            if not already_cancelled:
                tr.cancel()
            else:
                tr.cancelled()
            if (friend_number, file_number) in self._file_transfers:
                del tr
                del self._file_transfers[(friend_number, file_number)]
        elif not already_cancelled:
            self._tox.file_control(friend_number, file_number, TOX_FILE_CONTROL['CANCEL'])

    def cancel_not_started_transfer(self, friend_number, message_id):
        self._get_friend_by_number(friend_number).delete_one_unsent_file(message_id)

    def pause_transfer(self, friend_number, file_number, by_friend=False):
        """
        Pause transfer with specified data
        """
        tr = self._file_transfers[(friend_number, file_number)]
        tr.pause(by_friend)

    def resume_transfer(self, friend_number, file_number, by_friend=False):
        """
        Resume transfer with specified data
        """
        tr = self._file_transfers[(friend_number, file_number)]
        if by_friend:
            tr.state = FILE_TRANSFER_STATE['RUNNING']
        else:
            tr.send_control(TOX_FILE_CONTROL['RESUME'])

    def accept_transfer(self, path, friend_number, file_number, size, inline=False, from_position=0):
        """
        :param path: path for saving
        :param friend_number: friend number
        :param file_number: file number
        :param size: file size
        :param inline: is inline image
        :param from_position: position for start
        """
        path = self._generate_valid_path(path, from_position)
        friend = self._get_friend_by_number(friend_number)
        if not inline:
            rt = ReceiveTransfer(path, self._tox, friend_number, size, file_number, from_position)
        else:
            rt = ReceiveToBuffer(self._tox, friend_number, size, file_number)
        rt.set_transfer_finished_handler(self.transfer_finished)
        message = friend.get_message(lambda m: m.type == MESSAGE_TYPE['FILE_TRANSFER']
                                               and m.state in (FILE_TRANSFER_STATE['INCOMING_NOT_STARTED'],
                                                               FILE_TRANSFER_STATE['RUNNING'])
                                               and m.file_number == file_number)
        rt.set_state_changed_handler(message.transfer_updated)
        self._file_transfers[(friend_number, file_number)] = rt
        rt.send_control(TOX_FILE_CONTROL['RESUME'])
        if inline:
            self._insert_inline_before[(friend_number, file_number)] = message.message_id

    def send_screenshot(self, data, friend_number):
        """
        Send screenshot
        :param data: raw data - png format
        :param friend_number: friend number
        """
        self.send_inline(data, 'toxygen_inline.png', friend_number)

    def send_sticker(self, path, friend_number):
        with open(path, 'rb') as fl:
            data = fl.read()
        self.send_inline(data, 'sticker.png', friend_number)

    def send_inline(self, data, file_name, friend_number, is_resend=False):
        friend = self._get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            self._file_transfers_message_service.add_unsent_file_message(friend, file_name, data)
            return
        elif friend.status is None and is_resend:
            raise RuntimeError()
        st = SendFromBuffer(self._tox, friend.number, data, file_name)
        self._send_file_add_set_handlers(st, friend, file_name, True)

    def send_file(self, path, friend_number, is_resend=False, file_id=None):
        """
        Send file to current active friend
        :param path: file path
        :param friend_number: friend_number
        :param is_resend: is 'offline' message
        :param file_id: file id of transfer
        """
        friend = self._get_friend_by_number(friend_number)
        if friend.status is None and not is_resend:
            self._file_transfers_message_service.add_unsent_file_message(friend, path, None)
            return
        elif friend.status is None and is_resend:
            print('Error in sending')
            return
        st = SendTransfer(path, self._tox, friend_number, TOX_FILE_KIND['DATA'], file_id)
        file_name = os.path.basename(path)
        self._send_file_add_set_handlers(st, friend, file_name)

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
            self._get_friend_by_number(friend_number).load_avatar()
        elif t is ReceiveToBuffer or (t is SendFromBuffer and self._settings['allow_inline']):  # inline image
            print('inline')
            inline = InlineImageMessage(transfer.data)
            message_id = self._insert_inline_before[(friend_number, file_number)]
            del self._insert_inline_before[(friend_number, file_number)]
            index = self._get_friend_by_number(friend_number).insert_inline(message_id, inline)
            self._file_transfers_message_service.add_inline_message(transfer, index)
        del self._file_transfers[(friend_number, file_number)]

    def send_files(self, friend_number):
        friend = self._get_friend_by_number(friend_number)
        friend.remove_invalid_unsent_files()
        files = friend.get_unsent_files()
        try:
            for fl in files:
                data, path = fl.data, fl.path
                if data is not None:
                    self.send_inline(data, path, friend_number, True)
                else:
                    self.send_file(path, friend_number, True)
            friend.clear_unsent_files()
            for key in self._paused_file_transfers.keys():
                (path, ft_friend_number, is_incoming, start_position) = self._paused_file_transfers[key]
                if not os.path.exists(path):
                    del self._paused_file_transfers[key]
                elif ft_friend_number == friend_number and not is_incoming:
                    self.send_file(path, friend_number, True, key)
                    del self._paused_file_transfers[key]
        except Exception as ex:
            print('Exception in file sending: ' + str(ex))

    def friend_exit(self, friend_number):
        for friend_num, file_num in self._file_transfers.keys():
            if friend_num != friend_number:
                continue
            ft = self._file_transfers[(friend_num, file_num)]
            if type(ft) is SendTransfer:
                self._paused_file_transfers[ft.file_id] = [ft.path, friend_num, False, -1]
            elif type(ft) is ReceiveTransfer and ft.state != FILE_TRANSFER_STATE['INCOMING_NOT_STARTED']:
                self._paused_file_transfers[ft.file_id] = [ft.path, friend_num, True, ft.total_size()]
            self.cancel_transfer(friend_num, file_num, True)

    # -----------------------------------------------------------------------------------------------------------------
    # Avatars support
    # -----------------------------------------------------------------------------------------------------------------

    def send_avatar(self, friend_number, avatar_path=None):
        """
        :param friend_number: number of friend who should get new avatar
        :param avatar_path: path to avatar or None if reset
        """
        sa = SendAvatar(avatar_path, self._tox, friend_number)
        self._file_transfers[(friend_number, sa.file_number)] = sa

    def incoming_avatar(self, friend_number, file_number, size):
        """
        Friend changed avatar
        :param friend_number: friend number
        :param file_number: file number
        :param size: size of avatar or 0 (default avatar)
        """
        friend = self._get_friend_by_number(friend_number)
        ra = ReceiveAvatar(friend.get_contact_avatar_path(), self._tox, friend_number, size, file_number)
        if ra.state != FILE_TRANSFER_STATE['CANCELLED']:
            self._file_transfers[(friend_number, file_number)] = ra
            ra.set_transfer_finished_handler(self.transfer_finished)
        elif not size:
            friend.reset_avatar(self._settings['identicons'])

    def _send_avatar_to_contacts(self, _):
        friends = self._get_all_friends()
        for friend in filter(self._is_friend_online, friends):
            self.send_avatar(friend.number)

    # -----------------------------------------------------------------------------------------------------------------
    # Private methods
    # -----------------------------------------------------------------------------------------------------------------

    def _is_friend_online(self, friend_number):
        friend = self._get_friend_by_number(friend_number)

        return friend.status is not None

    def _get_friend_by_number(self, friend_number):
        return self._contact_provider.get_friend_by_number(friend_number)

    def _get_all_friends(self):
        return self._contact_provider.get_all_friends()

    def _send_file_add_set_handlers(self, st, friend, file_name, inline=False):
        st.set_transfer_finished_handler(self.transfer_finished)
        file_number = st.get_file_number()
        self._file_transfers[(friend.number, file_number)] = st
        tm = self._file_transfers_message_service.add_outgoing_transfer_message(friend, st.size, file_name, file_number)
        st.set_state_changed_handler(tm.transfer_updated)
        if inline:
            self._insert_inline_before[(friend.number, file_number)] = tm.message_id

    @staticmethod
    def _generate_valid_path(path, from_position):
        path, file_name = os.path.split(path)
        new_file_name, i = file_name, 1
        if not from_position:
            while os.path.isfile(join_path(path, new_file_name)):  # file with same name already exists
                if '.' in file_name:  # has extension
                    d = file_name.rindex('.')
                else:  # no extension
                    d = len(file_name)
                new_file_name = file_name[:d] + ' ({})'.format(i) + file_name[d:]
                i += 1
        path = join_path(path, new_file_name)

        return path
