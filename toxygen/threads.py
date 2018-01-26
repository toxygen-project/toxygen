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
