# encoding=utf-8

"""
FILE   : controller
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-19 01:34
"""

import sys

import system


class Controller(object):
    def __init__(self, gui):
        object.__init__(self)
        self._gui = gui

        rgl = system.RGL()
        kic = system.KIC()
        rea = system.REA()
        reac = system.Reac()

        self._systems = {
            'rgl': rgl, 'kic': kic, 'rea': rea, 'reac': reac,
        }

    def temp_on(self):
        pass

    def temp_off(self):
        pass

    def power_on(self):
        pass

    def power_off(self):
        pass

    def dilute_on(self):
        pass

    def dilute_off(self):
        pass

    def show(self):
        self._gui.show()
