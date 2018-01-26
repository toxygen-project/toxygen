import numpy as np
from PyQt5 import QtWidgets


class DesktopGrabber:

    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._width -= width % 4
        self._height -= height % 4
        self._screen = QtWidgets.QApplication.primaryScreen()

    def read(self):
        pixmap = self._screen.grabWindow(0, self._x, self._y, self._width, self._height)
        image = pixmap.toImage()
        s = image.bits().asstring(self._width * self._height * 4)
        arr = np.fromstring(s, dtype=np.uint8).reshape((self._height, self._width, 4))

        return True, arr
