from PyQt4 import QtGui

def clstree(cls, indent):
    print('.' * indent + cls.__name__)
    for supercls in cls.__bases__:
        clstree(supercls, indent+4)

if __name__ == '__main__':
    clstree(QtGui.QLabel, 0)
