

class Event:

    def __init__(self):
        self._callbacks = set()

    def __iadd__(self, callback):
        self.add_callback(callback)

    def __isub__(self, callback):
        self.remove_callback(callback)

    def __call__(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)

    def add_callback(self, callback):
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        self._callbacks.discard(callback)
