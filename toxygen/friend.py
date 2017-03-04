import contact
from messages import *
import os


class Friend(contact.Contact):
    """
    Friend in list of friends.
    """

    def __init__(self, message_getter, number, name, status_message, widget, tox_id):
        super().__init__(message_getter, number, name, status_message, widget, tox_id)
        self._receipts = 0

    # -----------------------------------------------------------------------------------------------------------------
    # File transfers support
    # -----------------------------------------------------------------------------------------------------------------

    def update_transfer_data(self, file_number, status, inline=None):
        """
        Update status of active transfer and load inline if needed
        """
        try:
            tr = list(filter(lambda x: x.get_type() == MESSAGE_TYPE['FILE_TRANSFER'] and x.is_active(file_number),
                             self._corr))[0]
            tr.set_status(status)
            i = self._corr.index(tr)
            if inline:  # inline was loaded
                self._corr.insert(i, inline)
            return i - len(self._corr)
        except:
            pass

    def get_unsent_files(self):
        messages = filter(lambda x: type(x) is UnsentFile, self._corr)
        return messages

    def clear_unsent_files(self):
        self._corr = list(filter(lambda x: type(x) is not UnsentFile, self._corr))

    def remove_invalid_unsent_files(self):
        def is_valid(message):
            if type(message) is not UnsentFile:
                return True
            if message.get_data()[1] is not None:
                return True
            return os.path.exists(message.get_data()[0])
        self._corr = list(filter(is_valid, self._corr))

    def delete_one_unsent_file(self, time):
        self._corr = list(filter(lambda x: not (type(x) is UnsentFile and x.get_data()[2] == time), self._corr))

    # -----------------------------------------------------------------------------------------------------------------
    # History support
    # -----------------------------------------------------------------------------------------------------------------

    def get_receipts(self):
        return self._receipts

    receipts = property(get_receipts)  # read receipts

    def inc_receipts(self):
        self._receipts += 1

    def dec_receipt(self):
        if self._receipts:
            self._receipts -= 1
            self.mark_as_sent()
