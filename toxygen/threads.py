from PyQt5 import QtCore
from bootstrap.bootstrap import *
import threading
import queue
from util import util



class InitThread(QtCore.QThread):

    def __init__(self, tox, ms, tray):
        QtCore.QThread.__init__(self)
        self.tox, self.ms, self.tray = tox, ms, tray
        self.stop = False

    def run(self):
        # initializing callbacks
        init_callbacks(self.tox, self.ms, self.tray)
        # download list of nodes if needed
        download_nodes_list()
        # bootstrap
        try:
            for data in generate_nodes():
                if self.stop:
                    return
                self.tox.bootstrap(*data)
                self.tox.add_tcp_relay(*data)
        except:
            pass
        for _ in range(10):
            if self.stop:
                return
            self.msleep(1000)
        while not self.tox.self_get_connection_status():
            try:
                for data in generate_nodes():
                    if self.stop:
                        return
                    self.tox.bootstrap(*data)
                    self.tox.add_tcp_relay(*data)
            except:
                pass
            finally:
                self.msleep(5000)


class ToxIterateThread(QtCore.QThread):

    def __init__(self, tox):
        QtCore.QThread.__init__(self)
        self.tox = tox
        self.stop = False

    def run(self):
        while not self.stop:
            self.tox.iterate()
            self.msleep(self.tox.iteration_interval())


class ToxAVIterateThread(QtCore.QThread):

    def __init__(self, toxav):
        QtCore.QThread.__init__(self)
        self.toxav = toxav
        self.stop = False

    def run(self):
        while not self.stop:
            self.toxav.iterate()
            self.msleep(self.toxav.iteration_interval())


class FileTransfersThread(threading.Thread):

    def __init__(self):
        self._queue = queue.Queue()
        self._timeout = 0.01
        self._continue = True
        super().__init__()

    def execute(self, func, *args, **kwargs):
        self._queue.put((func, args, kwargs))

    def stop(self):
        self._continue = False

    def run(self):
        while self._continue:
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
    _thread.stop()
    _thread.join()


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

