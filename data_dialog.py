# encoding=utf-8

"""
FILE   : getDataDialog
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-13 21:57
"""

import sys

from PyQt4 import QtGui, QtCore


class DataDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        layout = QtGui.QVBoxLayout()

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.buttonLayout = layout

    def _data(self):
        raise NotImplementedError

    def get_data(self):

        result = self.exec_()
        data = self._data()
        if data is None:
            return data, False
        else:
            return data, result == QtGui.QDialog.Accepted


class InitialDataDialog(DataDialog):
    def __init__(self, init_data=None, parent=None):
        DataDialog.__init__(self, parent)

        self.setWindowTitle('初始状态设置')

        labels = ['R棒棒位', 'SA棒棒位', 'SB棒棒位', 'SC棒棒位', 'SD棒棒位',
                  'G1棒棒位', 'G2棒棒位', 'N1棒棒位', 'N2棒棒位', '硼浓度']
        names = ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos',
                 'g1pos', 'g2pos', 'n1pos', 'n2pos', 'loop_bc']
        self.names = names

        self.grid = QtGui.QGridLayout()
        self.widgets = {}
        for i in range(len(labels)):
            label_name = names[i] + 'Label'
            text_name = names[i] + 'TextEdit'
            self.widgets[label_name] = QtGui.QLabel(labels[i])
            self.widgets[text_name] = QtGui.QLineEdit()
            self.grid.addWidget(self.widgets[label_name], i, 0)
            self.grid.addWidget(self.widgets[text_name], i, 1)

            if isinstance(init_data, dict):
                self.widgets[text_name].setText(str(init_data.get(names[i], '')))

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.grid)
        vbox.addLayout(self.buttonLayout)
        self.setLayout(vbox)

    def _data(self):
        for key in self.names:
            try:
                value = float(self.widgets.get(key + 'TextEdit').text())
                if key == 'loop_bc' and value < 0:
                    raise ValueError('硼浓度不能小于0')
                elif key != 'loop_bc' and (value < 5 or value > 225):
                    raise ValueError('棒位不能小于5或大于225')
            except ValueError as e:
                msgbox = QtGui.QMessageBox()
                msgbox.setIcon(QtGui.QMessageBox.Warning)
                msgbox.setWindowTitle('错误')
                msgbox.setText(e.args[0])
                msgbox.setDefaultButton(QtGui.QMessageBox.Ok)
                msgbox.exec_()
                return None
        return {key: float(self.widgets.get(key + 'TextEdit').text())
                for key in self.names}


if __name__ == '__main__':
    qapp = QtGui.QApplication(sys.argv)

    i = {'rpos': 191, 'g1pos': 225}
    dialog = InitialDataDialog(i)
    print(dialog.get_data())

    sys.exit(qapp.exec_())

