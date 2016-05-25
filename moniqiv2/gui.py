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
        rgl_operator = cus_wid.RGLOperateWidget()

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(rgl_view)
        vbox.addWidget(rgl_operator)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)
