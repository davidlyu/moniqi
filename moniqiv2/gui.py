# encoding=utf-8

"""
FILE   : gui
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-21 17:46
"""


from PyQt4 import QtGui, QtCore
import cus_wid


class MoniqiWindow(QtGui.QMainWindow):
    def __init__(self, controller):
        QtGui.QMainWindow.__init__(self)
        self._controller = controller

        rgl_view = cus_wid.RGLViewWidget()
        rgl_view.set_positions((5, 25, 35, 45, 5, 5, 5, 5, 5))

        self.setCentralWidget(rgl_view)
