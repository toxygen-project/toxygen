

class GroupChatPeer:
    """
    Represents peer in group chat.
    """

    def __init__(self, peer_id, name, status, role, public_key, is_current_user=False, is_muted=False):
        self._peer_id = peer_id
        self._name = name
        self._status = status
        self._role = role
        self._public_key = public_key
        self._is_current_user = is_current_user
        self._is_muted = is_muted

    # -----------------------------------------------------------------------------------------------------------------
    # Readonly properties
    # -----------------------------------------------------------------------------------------------------------------

    def get_id(self):
        return self._peer_id

    id = property(get_id)

    def get_public_key(self):
        return self._public_key

    public_key = property(get_public_key)

    def get_is_current_user(self):
        return self._is_current_user

    is_current_user = property(get_is_current_user)

    # -----------------------------------------------------------------------------------------------------------------
    # Read-write properties
    # -----------------------------------------------------------------------------------------------------------------

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    name = property(get_name, set_name)

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status

    status = property(get_status, set_status)

    def get_role(self):
        return self._role

    def set_role(self, role):
        self._role = role

    role = property(get_role, set_role)

    def get_is_muted(self):
        return self._is_muted

    def set_is_muted(self, is_muted):
        self._is_muted = is_muted

    is_muted = property(get_is_muted, set_is_muted)
