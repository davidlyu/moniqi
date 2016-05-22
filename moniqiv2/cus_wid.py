# encoding=utf-8

"""
FILE   : cus_wid
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-22 19:27
"""

from PyQt4 import QtGui, QtCore
import collections
import tools


class RodViewWidget(QtGui.QWidget):
    def __init__(self, label='', pos=225, parent=None):
        QtGui.QWidget.__init__(self, parent)

        tools.check_integer(pos, 0, 225)
        tools.check_string(label)

        self._label = label
        self._pos = pos

    def set_label(self, label):
        tools.check_string(label)
        self._label = label

    def set_pos(self, pos):
        tools.check_integer(pos, 0, 225)
        self._pos = pos

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self._draw_widget(qp)
        qp.end()

    def _draw_widget(self, qp):
        font = QtGui.QFont('Serif', 10, QtGui.QFont.Bold)
        qp.setFont(font)

        size = self.size()
        width = size.width()
        height = size.height()

        # draw label
        pen = QtGui.QPen(QtGui.QColor(20, 20, 20), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        metrics = qp.fontMetrics()
        label_width = metrics.width(self._label)
        font_height = metrics.height()
        x = int((width - label_width) / 2)
        y = font_height
        qp.drawText(x, y, self._label)

        # draw position
        pos_width = metrics.width(str(self._pos))
        x = int((width - pos_width) / 2)
        y = height - 1
        qp.drawText(x, y, str(self._pos))

        # draw rod
        x = int(width / 5 * 2)
        y = font_height + 1
        w = width / 5
        h = (height - font_height - font_height) - 2
        qp.drawRect(x, y, w, h)
        qp.setBrush(QtGui.QColor(5, 5, 5))
        qp.drawRect(x, y, w, int(h - h/232*self._pos))


class RGLViewWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        label = ('R', 'SA', 'SB', 'SC', 'SD', 'G1', 'G2', 'N1', 'N2')
        pos = (191, 225, 225, 225, 225, 225, 225, 225, 225)
        hbox = QtGui.QHBoxLayout()
        self._rod_widgets = []
        for lb, ps in zip(label, pos):
            widget = RodViewWidget(lb, ps)
            self._rod_widgets.append(widget)
            hbox.addWidget(widget)
        self.setLayout(hbox)

    def set_labels(self, labels):
        if not isinstance(labels, collections.Iterable):
            raise ValueError('labels should be iterable')

        for label, widget in zip(labels, self._rod_widgets):
            widget.set_label(label)

    def set_positions(self, positions):
        if not isinstance(positions, collections.Iterable):
            raise ValueError('positions should be iterable')

        for pos, widget in zip(positions, self._rod_widgets):
            widget.set_pos(pos)


class RGLOperateWidget(QtGui.QWidget):
    