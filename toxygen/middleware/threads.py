from bootstrap.bootstrap import *
import threading
import queue
from util import util
import time


class BaseThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self._stop = False

    def stop_thread(self):
        self._stop = True
        self.join()


class InitThread(BaseThread):

    def __init__(self, tox, ms, tray):
        super().__init__()
        self.tox, self.ms, self.tray = tox, ms, tray

    def run(self):
        # initializing callbacks
        init_callbacks(self.tox, self.ms, self.tray)
        # download list of nodes if needed
        download_nodes_list()
        # bootstrap
        try:
            for data in generate_nodes():
                if self._stop:
                    return
                self.tox.bootstrap(*data)
                self.tox.add_tcp_relay(*data)
        except:
            pass
        for _ in range(10):
            if self._stop:
                return
            time.sleep(1)
        while not self.tox.self_get_connection_status():
            try:
                for data in generate_nodes():
                    if self._stop:
                        return
                    self.tox.bootstrap(*data)
                    self.tox.add_tcp_relay(*data)
            except:
                pass
            finally:
                time.sleep(5)


class ToxIterateThread(BaseThread):

    def __init__(self, tox):
        super().__init__()
        self._tox = tox

    def run(self):
        while not self._stop:
            self._tox.iterate()
            time.sleep(self._tox.iteration_interval() / 1000)


class ToxAVIterateThread(BaseThread):

    def __init__(self, toxav):
        super().__init__()
        self._toxav = toxav

    def run(self):
        while not self._stop:
            self._toxav.iterate()
            time.sleep(self._toxav.iteration_interval() / 1000)


class FileTransfersThread(BaseThread):

    def __init__(self):
        super().__init__()
        self._queue = queue.Queue()
        self._timeout = 0.01

    def execute(self, func, *args, **kwargs):
        self._queue.put((func, args, kwargs))

    def run(self):
        while not self._stop:
            try:
                func, args, kwargs = self._queue.get(timeout=self._timeout)
                func(*args, **kwargs)
            except queue.Empty:
                pass
            except queue.Full:
                util.log('Queue is full in _thread')
            except Exception as ex:
                util.log('Exception in _thread: ' + str(ex))


_thread = FileTransfersThread()


def start():
    _thread.start()


def stop():
    _thread.stop_thread()


def execute(func, *args, **kwargs):
    _thread.execute(func, *args, **kwargs)


class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Invoker(QtCore.QObject):

    def event(self, event):
        event.fn(*event.args, **event.kwargs)
        return True


_invoker = Invoker()


def invoke_in_main_thread(fn, *args, **kwargs):
    QtCore.QCoreApplication.postEvent(_invoker, InvokeEvent(fn, *args, **kwargs))

