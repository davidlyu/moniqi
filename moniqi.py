# encoding=utf-8

"""
FILE   : moniqi
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-19 01:52
"""

import sys
from PyQt4 import QtGui

import controller
import gui


def main():
    app = QtGui.QApplication(sys.argv)

    view = gui.MainWindow()
    ctrl = controller.Controller(view)
    ctrl.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
