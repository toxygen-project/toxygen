from contacts import basecontact
import random
import threading
import common.tox_save as tox_save


class Profile(basecontact.BaseContact, tox_save.ToxSave):
    """
    Profile of current toxygen user.
    """
    def __init__(self, profile_manager, tox, screen, contacts_provider, reset_action):
        """
        :param tox: tox instance
        :param screen: ref to main screen
        """
        basecontact.BaseContact.__init__(self,
                                         profile_manager,
                                         tox.self_get_name(),
                                         tox.self_get_status_message(),
                                         screen.user_info,
                                         tox.self_get_address())
        tox_save.ToxSave.__init__(self, tox)
        self._screen = screen
        self._messages = screen.messages
        self._contacts_provider = contacts_provider
        self._reset_action = reset_action
        self._waiting_for_reconnection = False
        self._timer = None

    # -----------------------------------------------------------------------------------------------------------------
    # Edit current user's data
    # -----------------------------------------------------------------------------------------------------------------

    def change_status(self):
        """
        Changes status of user (online, away, busy)
        """
        if self._status is not None:
            self.set_status((self._status + 1) % 3)

    def set_status(self, status):
        super().set_status(status)
        if status is not None:
            self._tox.self_set_status(status)
        elif not self._waiting_for_reconnection:
            self._waiting_for_reconnection = True
            self._timer = threading.Timer(50, self._reconnect)
            self._timer.start()

    def set_name(self, value):
        if self.name == value:
            return
        super().set_name(value)
        self._tox.self_set_name(self._name)

    def set_status_message(self, value):
        super().set_status_message(value)
        self._tox.self_set_status_message(self._status_message)

    def set_new_nospam(self):
        """Sets new nospam part of tox id"""
        self._tox.self_set_nospam(random.randint(0, 4294967295))  # no spam - uint32
        self._tox_id = self._tox.self_get_address()

        return self._tox_id

    # -----------------------------------------------------------------------------------------------------------------
    # Reset
    # -----------------------------------------------------------------------------------------------------------------

    def restart(self):
        """
        Recreate tox instance
        """
        self.status = None
        self._reset_action()

    def _reconnect(self):
        self._waiting_for_reconnection = False
        contacts = self._contacts_provider.get_all_friends()
        if self.status is None or (all(list(map(lambda x: x.status is None, contacts))) and len(contacts)):
            self._waiting_for_reconnection = True
            self.restart()
            self._timer = threading.Timer(50, self._reconnect)
            self._timer.start()
