from PyQt4 import QtGui, QtCore
import sys
import clock
import system
import data
import command
import datetime
import data_dialog


class Gui(QtGui.QWidget, clock.Observer):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.temp_on_command = None
        self.temp_off_command = None
        self.power_on_command = None
        self.power_off_command = None
        self.dilute_on_command = None
        self.dilute_off_command = None
        self.boron_on_command = None
        self.boron_off_command = None
        self.systems = []

        self.kic_buf = []
        header = '%5s %8s %7s %7s %8s %8s' % ('DATE', 'TIME', 'SRC1', 'SRC2', 'IRC1', 'IRC2')
        self.kic_buf.append(header)
        self.kic_buf.append('-' * len(header))

        self.save_file_on = False
        self.save_file_object = None
        # widgets

        self._widgets = {
            'rpos': QtGui.QLabel(),
            'sapos': QtGui.QLabel(),
            'sbpos': QtGui.QLabel(),
            'scpos': QtGui.QLabel(),
            'sdpos': QtGui.QLabel(),
            'g1pos': QtGui.QLabel(),
            'g2pos': QtGui.QLabel(),
            'n1pos': QtGui.QLabel(),
            'n2pos': QtGui.QLabel(),
            'gpos': QtGui.QLabel(),
            'rselect': QtGui.QComboBox(),
            'rneed': QtGui.QLineEdit(),
            'rstart': QtGui.QPushButton('Start'),
            'gselect': QtGui.QComboBox(),
            'gneed': QtGui.QLineEdit(),
            'gstart': QtGui.QPushButton('Start'),
            'boronvol': QtGui.QLineEdit(),
            'dilutevol': QtGui.QLineEdit(),
            'boronrate': QtGui.QLineEdit(),
            'diluterate': QtGui.QLineEdit(),
            'boronstart': QtGui.QPushButton('硼化'),
            'dilutestart': QtGui.QPushButton('稀释'),
            'table': QtGui.QTextEdit(),
            'reactivity': QtGui.QLabel(),
            'boronmeter': QtGui.QLabel(),
        }
        self._widgets['rselect'].addItems(['R', 'SA', 'SB', 'SC', 'SD'])
        self._widgets['gselect'].addItems(['G1', 'G2', 'N1', 'N2', 'G'])

        self._widgets['rstart'].setCheckable(True)
        self._widgets['gstart'].setCheckable(True)
        self._widgets['rstart'].setChecked(False)
        self._widgets['gstart'].setChecked(False)
        self._widgets['dilutestart'].setCheckable(True)
        self._widgets['dilutestart'].setChecked(False)
        self._widgets['boronstart'].setCheckable(True)
        self._widgets['boronstart'].setChecked(False)
        self.connect(self._widgets['rstart'], QtCore.SIGNAL('clicked()'),
                     self.on_temp)
        self.connect(self._widgets['gstart'], QtCore.SIGNAL('clicked()'),
                     self.on_power)
        self.connect(self._widgets['dilutestart'], QtCore.SIGNAL('clicked()'),
                     self.on_dilute)
        self.connect(self._widgets['boronstart'], QtCore.SIGNAL('clicked()'),
                     self.on_boron)
        self._rod_widgets = ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos',
                             'g1pos', 'g2pos', 'n1pos', 'n2pos', 'gpos']

        self._set_widget()
        self.setWindowTitle('物理试验模拟器')
        self.setGeometry(200, 200, 600, 800)
        self.setFixedSize(600, 800)

    def _set_widget(self):
        top_left_grid = QtGui.QGridLayout()
        i = 0
        for label, name in zip(['R', 'SA', 'SB', 'SC', 'SD'],
                               ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos']):
            top_left_grid.addWidget(QtGui.QLabel(label), 0, i)
            top_left_grid.addWidget(self._widgets[name], 1, i)
            i += 1

        labels = ['硼化量', '流量', '']
        r = ['rselect', 'rneed', 'rstart']
        b = ['boronvol', 'boronrate', 'boronstart']
        med_left_grid = QtGui.QGridLayout()
        for i in range(0, 3):
            med_left_grid.addWidget(self._widgets[r[i]], 0, i)
            med_left_grid.addWidget(QtGui.QLabel(labels[i]), 1, i)
            med_left_grid.addWidget(self._widgets[b[i]], 2, i)

        upper_left_vbox = QtGui.QVBoxLayout()
        upper_left_vbox.addLayout(top_left_grid)
        upper_left_vbox.addLayout(med_left_grid)

        top_right_grid = QtGui.QGridLayout()
        i = 0
        for label, name in zip(['G1', 'G2', 'N1', 'N2', 'G'],
                               ['g1pos', 'g2pos', 'n1pos', 'n2pos', 'gpos']):
            top_right_grid.addWidget(QtGui.QLabel(label), 0, i)
            top_right_grid.addWidget(self._widgets[name], 1, i)
            i += 1

        labels = ['稀释量', '流量', '']
        r = ['gselect', 'gneed', 'gstart']
        b = ['dilutevol', 'diluterate', 'dilutestart']
        med_right_grid = QtGui.QGridLayout()
        for i in range(3):
            med_right_grid.addWidget(self._widgets[r[i]], 0, i)
            med_right_grid.addWidget(QtGui.QLabel(labels[i]), 1, i)
            med_right_grid.addWidget(self._widgets[b[i]], 2, i)

        upper_right_vbox = QtGui.QVBoxLayout()
        upper_right_vbox.addLayout(top_right_grid)
        upper_right_vbox.addLayout(med_right_grid)

        upper_hbox = QtGui.QHBoxLayout()
        upper_hbox.addLayout(upper_left_vbox)
        upper_hbox.addLayout(upper_right_vbox)

        bottom_hbox = QtGui.QHBoxLayout()
        bottom_hbox.addWidget(QtGui.QLabel('反应性'))
        bottom_hbox.addWidget(self._widgets['reactivity'])
        bottom_hbox.addWidget(QtGui.QLabel('硼浓度'))
        bottom_hbox.addWidget(self._widgets['boronmeter'])

        bottom_vbox = QtGui.QVBoxLayout()
        bottom_vbox.addWidget(self._widgets['table'])
        bottom_vbox.addLayout(bottom_hbox)
        self._widgets['table'].setReadOnly(True)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(upper_hbox)
        vbox.addLayout(bottom_vbox)

        self.setLayout(vbox)

    def on_temp(self):
        if self._widgets['rstart'].isChecked():
            rod = str(self._widgets['rselect'].currentText())
            target = int(str(self._widgets['rneed'].text()))
            self.temp_on_command.execute(rod=rod, target=target)
            self._widgets['rstart'].setText('Stop')
        else:
            self.temp_off_command.execute()
            self._widgets['rstart'].setText('Start')

    def on_power(self):
        if self._widgets['gstart'].isChecked():
            rod = str(self._widgets['gselect'].currentText())
            target = int(str(self._widgets['gneed'].text()))
            self.power_on_command.execute(rod=rod, target=target)
            self._widgets['gstart'].setText('Stop')
        else:
            self.power_off_command.execute()
            self._widgets['gstart'].setText('Start')

    def on_dilute(self):
        if self._widgets['boronstart'].isChecked():
            self._widgets['dilutestart'].setChecked(False)
            return None

        if self._widgets['dilutestart'].isChecked():
            vol = float(str(self._widgets['dilutevol'].text()))
            rate = float(str(self._widgets['diluterate'].text()))
            self.dilute_on_command.execute(vol=vol, rate=rate)
            self._widgets['dilutestart'].setText('停止')
        else:
            self.dilute_off_command.execute()
            self._widgets['dilutestart'].setText('稀释')

    def on_boron(self):
        if self._widgets['dilutestart'].isChecked():
            self._widgets['boronstart'].setChecked(False)
            return None

        if self._widgets['boronstart'].isChecked():
            vol = float(str(self._widgets['boronvol'].text()))
            rate = float(str(self._widgets['boronrate'].text()))
            self.boron_on_command.execute(vol=vol, rate=rate)
            self._widgets['boronstart'].setText('停止')
        else:
            self.boron_off_command.execute()
            self._widgets['boronstart'].setText('硼化')

    def add_system(self, s):
        self.systems.append(s)

    def get_system_dict(self):
        return {s.get_data()['name']: s for s in self.systems}

    def update(self):
        system_dict = self.get_system_dict()
        self.display_rgl(system_dict['rgl'].get_data())
        self.display_rea(system_dict['rea'].get_data())
        self.display_reac(system_dict['reac'].get_data())
        self.display_kic(system_dict['kic'].get_data())

        if self.save_file_on:
            self.save_file(self.save_file_object, system_dict)

    def display_rgl(self, dat):
        for i in ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos',
                  'g1pos', 'g2pos', 'n1pos', 'n2pos', 'gpos']:
            self._widgets[i].setText(str(dat[i]))
        if not dat['is_temp_active']:
            self._widgets['rstart'].setChecked(False)
            self._widgets['rstart'].setText('Start')
        if not dat['is_power_active']:
            self._widgets['gstart'].setChecked(False)
            self._widgets['gstart'].setText('Start')

    def display_rea(self, dat):
        self._widgets['boronmeter'].setText(str(round(dat['loop_bc'] + 0.05, 1)))
        if not dat['is_dilute_active']:
            self._widgets['dilutestart'].setChecked(False)
            self._widgets['dilutestart'].setText('稀释')
        else:
            self._widgets['dilutevol'].setText(str(round(dat['dilute_vol']+0.005, 2)))

        if not dat['is_boron_active']:
            self._widgets['boronstart'].setChecked(False)
            self._widgets['boronstart'].setText('硼化')
        else:
            self._widgets['boronvol'].setText(str(round(dat['boron_vol']+0.005, 2)))

    def display_reac(self, dat):
        self._widgets['reactivity'].setText(str(round(dat['reactivity']+0.05, 1)))

    def display_kic(self, dat):
        n = datetime.datetime.now()
        d = n.strftime('%m-%d')
        t = n.strftime('%H:%M:%S')
        form = '%s %s %7d %7d %8.2E %8.2E' % (d, t, dat['src1'], dat['src2'], dat['irc1'], dat['irc2'])
        self.kic_buf.append(form)
        if len(self.kic_buf) > 32:
            self.kic_buf[2:-16] = []
        self._widgets['table'].setText('\n'.join(self.kic_buf))

    def set_save(self, save_file_object):
        self.save_file_on = True
        self.save_file_object = save_file_object

    @staticmethod
    def save_file(file_object, dat):
        src1 = dat['kic'].get_data()['src1']
        src2 = dat['kic'].get_data()['src2']
        irc1 = dat['kic'].get_data()['irc1']
        irc2 = dat['kic'].get_data()['irc2']
        reactivity = dat['reac'].get_data()['reactivity']
        n = datetime.datetime.now()
        d = n.strftime('%Y-%m-%d,%H:%M:%S')
        form = '{datetime:s},{src1:.0f},{src2:.0f},{irc1:.3E},{irc2:.3E},{reactivity:.1f}'.format(
            datetime=d, src1=src1, src2=src2, irc1=irc1, irc2=irc2,
            reactivity=reactivity
        )
        file_object.write(form + '\n')

    def set_temp_on_command(self, com):
        self.temp_on_command = com

    def set_temp_off_command(self, com):
        self.temp_off_command = com

    def set_power_on_command(self, com):
        self.power_on_command = com

    def set_power_off_command(self, com):
        self.power_off_command = com

    def set_dilute_on_command(self, com):
        self.dilute_on_command = com

    def set_dilute_off_command(self, com):
        self.dilute_off_command = com

    def set_boron_on_command(self, com):
        self.boron_on_command = com

    def set_boron_off_command(self, com):
        self.boron_off_command = com

    def set_init_data(self, init_data):
        """
        将个系统的参数设置为init_data所包含的参数。
        :param init_data:
        init_data是一个字典，包含的所有控制棒的棒位，和一回路的硼浓度。
        键列表为：
        ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos', 'g1pos', 'g2pos', 'n1pos', 'n2pos', 'boron']
        :return: None
        """
        system_dict = self.get_system_dict()
        init_data_names = ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos',
                           'g1pos', 'g2pos', 'n1pos', 'n2pos']
        for name in init_data_names:
            system_dict['rgl'].get_data()[name] = int(init_data[name])

        system_dict['rea'].get_data()['loop_bc'] = float(init_data['loop_bc'])

    def get_init_data(self):
        """
        返回各系统的初始参数
        :return: dict, see method set_init_data's parameter init_data.
        """
        system_dict = self.get_system_dict()
        init_data = {}
        init_data_names = ['rpos', 'sapos', 'sbpos', 'scpos', 'sdpos',
                           'g1pos', 'g2pos', 'n1pos', 'n2pos']
        for name in init_data_names:
            init_data[name] = system_dict['rgl'].get_data()[name]

        init_data['loop_bc'] = system_dict['rea'].get_data()['loop_bc']
        return init_data


class MainWindow(QtGui.QMainWindow):
    def __init__(self, gui):
        QtGui.QMainWindow.__init__(self)
        self.save_file_object = None

        width = self.sizeHint().width()
        height = self.sizeHint().height()
        self.setFixedSize(width, height)

        self.setWindowTitle('物理试验模拟器')
        self.gui = gui
        self.setCentralWidget(self.gui)
        save_action = QtGui.QAction(QtGui.QIcon('icons/save.png'), '记录', self)
        self.connect(save_action, QtCore.SIGNAL('triggered()'), self, QtCore.SLOT('on_save()'))

        close_action = QtGui.QAction(QtGui.QIcon('icons/close.png'), '退出', self)
        self.connect(close_action, QtCore.SIGNAL('triggered()'), self, QtCore.SLOT('on_quit()'))

        get_init_data_action = QtGui.QAction(QtGui.QIcon('icons/setting.png'), '初始数据', self)
        self.connect(get_init_data_action, QtCore.SIGNAL('triggered()'), self, QtCore.SLOT('on_init_data()'))

        menu_bar = self.menuBar()
        file = menu_bar.addMenu('&File')
        file.addAction(save_action)
        file.addAction(close_action)

        setting = menu_bar.addMenu('&Setting')
        setting.addAction(get_init_data_action)

    @QtCore.pyqtSlot()
    def on_save(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', './')
        self.save_file_object = open(filename, 'a')
        self.gui.set_save(self.save_file_object)

    @QtCore.pyqtSlot()
    def on_quit(self):
        self.save_file_object.close()
        QtGui.qApp.quit()

    @QtCore.pyqtSlot()
    def on_init_data(self):
        dialog = data_dialog.InitialDataDialog(self.gui.get_init_data())
        init_data, ok = dialog.get_data()
        if ok:
            self.gui.set_init_data(init_data)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    clc = clock.Clock()

    rgl_data = data.RglData()
    rgl = system.RGL(rgl_data)

    rea_data = data.ReaData()
    rea = system.REA(rea_data)

    reac_data = data.ReacData()
    reac = system.Reac(reac_data)
    reac.add_system(rgl)
    reac.add_system(rea)

    kic_data = data.KicData()
    kic = system.KIC(kic_data)
    kic.add_systems(reac)

    ui = Gui()
    ui.add_system(rgl)
    ui.add_system(rea)
    ui.add_system(reac)
    ui.add_system(kic)

    clc.add_observer(rgl)
    clc.add_observer(rea)
    clc.add_observer(reac)
    clc.add_observer(kic)
    clc.add_observer(ui)

    temp_on_com = command.TempOnCommand(rgl)
    temp_off_com = command.TempOffCommand(rgl)
    power_on_com = command.PowerOnCommand(rgl)
    power_off_com = command.PowerOffCommand(rgl)
    dilute_on_com = command.DiluteOnCommand(rea)
    dilute_off_com = command.DiluteOffCommand(rea)
    boron_on_com = command.BoronOnCommand(rea)
    boron_off_com = command.BoronOffCommand(rea)

    ui.set_temp_on_command(temp_on_com)
    ui.set_temp_off_command(temp_off_com)
    ui.set_power_on_command(power_on_com)
    ui.set_power_off_command(power_off_com)
    ui.set_dilute_on_command(dilute_on_com)
    ui.set_dilute_off_command(dilute_off_com)
    ui.set_boron_on_command(boron_on_com)
    ui.set_boron_off_command(boron_off_com)

    main_window = MainWindow(ui)
    main_window.show()

    sys.exit(app.exec_())
