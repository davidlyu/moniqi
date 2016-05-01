from PyQt4 import QtGui, QtCore


class Subject:
    def __init__(self):
        self.observer_list = []

    def add_observer(self, observer):
        self.observer_list.append(observer)

    def del_observer(self, observer):
        i = self.observer_list.index(observer)
        self.observer_list.pop(i)

    def notify_observers(self):
        for i in self.observer_list:
            i.update()


class Clock(Subject, QtCore.QObject):
    def __init__(self):
        Subject.__init__(self)
        QtCore.QObject.__init__(self)

        self.timer = QtCore.QTimer(self)
        self.connect(self.timer, QtCore.SIGNAL('timeout()'),
                     self.update)
        self.timer.start(1000)

    def update(self):
        self.notify_observers()


class Observer:
    def __init__(self):
        pass

    def update(self):
        pass


if __name__ == '__main__':
    pass

