import clock
from math import exp
from tools import Tools


class System:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data


class RGL(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)

    def move_temp_rod(self, rod, target):
        if not self.data['is_temp_active']:
            self.data['is_temp_active'] = True
            self.data['temp_target'] = target
            self.data['current_temp_rod'] = rod

    def move_power_rod(self, rod, target):
        if not self.data['is_power_active']:
            self.data['is_power_active'] = True
            self.data['power_target'] = target
            self.data['current_power_rod'] = rod

    def stop_temp_rod(self):
        self.data['is_temp_active'] = False

    def stop_power_rod(self):
        self.data['is_power_active'] = False

    def update(self):
        rho = 0
        if self.data['is_temp_active']:
            rod = self.data['current_temp_rod'].lower()
            rod_pos = rod + 'pos'
            rod_value = rod + '_value'
            rho = 0
            if self.data[rod_pos] < self.data['temp_target']:
                rho = Tools.lookup(self.data[rod_value], self.data[rod_pos])
                self.data[rod_pos] += 1
            elif self.data[rod_pos] > self.data['temp_target']:
                rho = -Tools.lookup(self.data[rod_value], self.data[rod_pos])
                self.data[rod_pos] -= 1
            else:
                self.data['is_temp_active'] = False

        if self.data['is_power_active']:
            rod = self.data['current_power_rod'].lower()
            rod_pos = rod + 'pos'
            rod_value = rod + '_value'
            if self.data[rod_pos] < self.data['power_target']:
                rho = Tools.lookup(self.data[rod_value], self.data[rod_pos])
                self.data[rod_pos] += 1
            elif self.data[rod_pos] > self.data['power_target']:
                rho = -Tools.lookup(self.data[rod_value], self.data[rod_pos])
                self.data[rod_pos] -= 1
            else:
                self.data['is_power_active'] = False

        self.data['delta_rho'] = rho


class REA(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)

    def dilute(self, vol, rate):
        if not self.data['is_dilute_active']:
            self.data['dilute_vol'] = vol
            self.data['dilute_rate'] = rate
            self.data['is_dilute_active'] = True

    def stop_dilute(self):
        self.data['is_dilute_active'] = False

    def boron(self, vol, rate):
        if not self.data['is_boron_active']:
            self.data['boron_vol'] = vol
            self.data['boron_rate'] = rate
            self.data['is_boron_active'] = True

    def stop_boron(self):
        self.data['is_boron_active'] = False

    def update(self):
        loop_bc = self.data['loop_bc']
        rcp_vol = self.data['rcp_vol']
        boron_value = Tools.lookup(self.data['boron_value'], loop_bc)
        if self.data['is_dilute_active']:
            dilute_vol = self.data['dilute_vol']
            dilute_rate = self.data['dilute_rate']
            e = exp(-dilute_rate / 3600 / rcp_vol)
            if dilute_vol < (dilute_rate / 3600):
                self.data['dilute_vol'] = 0
                self.data['is_dilute_active'] = False
            else:
                self.data['loop_bc'] = e * loop_bc
                self.data['dilute_vol'] -= dilute_rate / 3600

        if self.data['is_boron_active']:
            boron_vol = self.data['boron_vol']
            boron_rate = self.data['boron_rate']
            tank_bc = self.data['tank_bc']
            e = exp(-boron_rate / 3600 / rcp_vol)
            if boron_vol < (boron_rate / 3600):
                self.data['boron_vol'] = 0
                self.data['is_boron_active'] = False
            else:
                self.data['loop_bc'] = e * loop_bc + (1 - e) * tank_bc
                self.data['boron_vol'] -= boron_rate / 3600

        rho = -(loop_bc - self.data['loop_bc']) * boron_value
        self.data['delta_rho'] = rho


class Reac(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self.systems = []

    def add_system(self, s):
        self.systems.append(s)

    def rho(self, double_t):
        t = double_t / 0.693
        s = sum([b / (1 + L * t) for b, L in self.data['beta']])
        return self.data['neutron_life'] / t + 0.97 * s * 100000

    def rho_d(self, double_t):
        t = double_t / 0.693
        s = sum([b * L / (1 + L * t) ** 2 for b, L in self.data['beta']])
        return -self.data['neutron_life'] / (t ** 2) - 0.97 * s * 100000

    def double_time(self):
        sign = 1
        rho = self.data['reactivity']
        if rho > 300:
            raise ValueError('rho = %.1f pcm, two large.' % rho)
        elif 0 <= rho < 1:
            rho = 1
        elif -1 <= rho < 0:
            sign = -1
            rho = 1
        elif rho < -1:
            sign = -1
            rho = abs(rho)

        t0 = 10
        t1 = t0 - (self.rho(t0) - rho) / self.rho_d(t0)
        while abs(t0 - t1) > 1.0E-3:
            # print('t0=%.2f\tt1=%.2f' % (t0, t1))
            t0 = t1
            t1 = t0 - (self.rho(t0) - rho) / self.rho_d(t0)

        return t1 * sign

    def update(self):
        system_dict = {s.get_data()['name']: s for s in self.systems}
        self.data['reactivity'] += system_dict['rgl'].get_data()['delta_rho']
        self.data['reactivity'] += system_dict['rea'].get_data()['delta_rho']


class KIC(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self.systems = []

    def add_systems(self, s):
        self.systems.append(s)

    def update(self):
        system_dict = {s.get_data()['name']: s for s in self.systems}
        self.data['core_power'] *= (2 ** (1 / system_dict['reac'].double_time()))
        self.data['irc1'] = self.data['core_power'] / self.data['irc1a2fp']
        self.data['irc2'] = self.data['core_power'] / self.data['irc2a2fp']
        self.data['src1'] = self.data['core_power'] / self.data['src1cps2fp']
        self.data['src2'] = self.data['core_power'] / self.data['src2cps2fp']

