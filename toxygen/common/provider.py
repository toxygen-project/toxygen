

class Provider:

    def __init__(self, get_item_action):
        self._get_item_action = get_item_action
        self._item = None

    def get_item(self):
        if self._item is None:
            self._item = self._get_item_action()

        return self._item
