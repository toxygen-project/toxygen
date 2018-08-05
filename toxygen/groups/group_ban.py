

class GroupBan:

    def __init__(self, ban_id, ban_target, ban_time):
        self._ban_id = ban_id
        self._ban_target = ban_target
        self._ban_time = ban_time

    def get_ban_id(self):
        return self._ban_id

    ban_id = property(get_ban_id)

    def get_ban_target(self):
        return self._ban_target

    ban_target = property(get_ban_target)

    def get_ban_time(self):
        return self._ban_time

    ban_time = property(get_ban_time)
