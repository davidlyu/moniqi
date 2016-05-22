# encoding=utf-8

"""
FILE   : controller
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-21 17:45
"""

import sys
import gui
from PyQt4 import QtCore


class Clock(QtCore.QObject):
    def __init__(self, listener):
        QtCore.QObject.__init__(self)
        self._listener = listener
        self._timer = QtCore.QTimer(self)
        self.connect(self._timer, QtCore.SIGNAL('timeout()'),
                     self._update)

    def start(self, interval):
        self._timer.start(interval)

    def pause(self):
        self._timer.stop()

    def _update(self):
        self._listener.update()


class Controller:
    def __init__(self, model):
        self._model = model
        self._window = gui.MoniqiWindow(self)

        self._clock = Clock(self)

    def show(self):
        self._window.show()

    def start_moniqi(self, interval=1000):
        self._clock.start(interval)

    def update(self):
        self._window.update()
