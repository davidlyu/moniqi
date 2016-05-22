# encoding=utf-8

"""
FILE   : moniqi
PROJECT: moniqi
AUTHOR : bj
DATE   : 2016-05-21 17:45
"""

import sys

import plant
import control


from PyQt4 import QtGui, QtCore


def main():
    app = QtGui.QApplication(sys.argv)

    plant_model = plant.PlantModel()
    ctrl = control.Controller(plant_model)

    ctrl.start_moniqi()
    ctrl.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()