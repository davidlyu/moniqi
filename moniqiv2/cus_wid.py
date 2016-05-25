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
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.current_temp_changed = QtCore.pyqtSignal()
        self.current_power_changed = QtCore.pyqtSignal()

        self._temp_selector = QtGui.QComboBox()
        self._power_selector = QtGui.QComboBox()
        self._temp_need = QtGui.QLineEdit()
        self._power_need = QtGui.QLineEdit()
        self._temp_button = QtGui.QPushButton()
        self._power_button = QtGui.QPushButton()

        self._set_widget()

    def _set_widget(self):
        self._temp_selector.addItems(['R', 'SA', 'SB', 'SC', 'SD'])
        self._power_selector.addItems(['G1', 'G2', 'N1', 'N2', 'G'])
        self._temp_button.setText('Start')
        self._power_button.setText('Start')

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self._temp_selector)
        hbox.addWidget(self._temp_need)
        hbox.addWidget(self._temp_button)
        hbox.addWidget(self._power_selector)
        hbox.addWidget(self._power_need)
        hbox.addWidget(self._power_button)
        self.setLayout(hbox)

        self.connect(self._temp_selector, QtCore.SIGNAL('currentIndexChanged()'), self._on_temp_changed)
        self.connect(self._power_selector, QtCore.SIGNAL('currentIndexChanged()'), self._on_power_changed)

    def _on_temp_changed(self):
        self.current_temp_changed.emit()

    def _on_power_changed(self):
        self.current_power_changed.emit()

    def get_current_temp(self):
        temp_rod = str(self._temp_selector.currentText())
        return temp_rod

    def get_current_power(self):
        power_rod = str(self._power_selector.currentText())
        return power_rod

    def get_temp_need(self):
        try:
            temp_pos = int(self._temp_need.text())
            tools.check_integer(temp_pos, 0, 225)
        except ValueError:
            msgbox = QtGui.QMessageBox()
            msgbox.setIcon(QtGui.QMessageBox.Warning)
            msgbox.setWindowTitle('错误')
            msgbox.setText('R/S目标棒位必须是0-225的整数')
            msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
            msgbox.exec_()
            return None
        return temp_pos

    def get_power_need(self):
        try:
            power_pos = int(self._power_need.text())
            tools.check_integer(power_pos, 0, 225)
        except ValueError:
            msgbox = QtGui.QMessageBox()
            msgbox.setIcon(QtGui.QMessageBox.Warning)
            msgbox.setWindowTitle('错误')
            msgbox.setText('功率补偿棒目标棒位必须是0-225的整数')
            msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
            msgbox.exec_()
            return None
        return power_pos

