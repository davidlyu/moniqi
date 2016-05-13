import clock
from math import exp
from tools import Tools
from scipy.stats import norm as norm_module


class System:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data


class RGL(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self.random_item = 1 + norm_module.rvs(0, data['rod_value_accuracy'], 1)[0]

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
            value_table = self.data[rod_value]
            if self.data[rod_pos] < self.data['temp_target']:
                rho = (Tools.lookup(value_table, self.data[rod_pos]) +
                       Tools.lookup(value_table, self.data[rod_pos] + 1)) / 2
                self.data[rod_pos] += 1
            elif self.data[rod_pos] > self.data['temp_target']:
                rho = -(Tools.lookup(value_table, self.data[rod_pos]) +
                        Tools.lookup(value_table, self.data[rod_pos] - 1)) / 2
                self.data[rod_pos] -= 1
            else:
                self.data['is_temp_active'] = False

        if self.data['is_power_active']:
            rod = self.data['current_power_rod'].lower()
            rod_pos = rod + 'pos'
            rod_value = rod + '_value'
            value_table = self.data[rod_value]
            if self.data[rod_pos] < self.data['power_target']:
                rho = (Tools.lookup(value_table, self.data[rod_pos]) +
                       Tools.lookup(value_table, self.data[rod_pos] + 1)) / 2
                self.data[rod_pos] += 1
            elif self.data[rod_pos] > self.data['power_target']:
                rho = -(Tools.lookup(value_table, self.data[rod_pos]) +
                        Tools.lookup(value_table, self.data[rod_pos] - 1)) / 2
                self.data[rod_pos] -= 1
            else:
                self.data['is_power_active'] = False

        self.data['delta_rho'] = rho * self.random_item


class REA(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self._residual_boron_rate = 0
        self._residual_dilute_rate = 0
        self._residual_boron_on = False
        self._residual_dilute_on = False

    def dilute(self, vol, rate):
        if not self.data['is_dilute_active']:
            self.data['dilute_vol'] = vol
            self.data['dilute_rate'] = rate
            self.data['is_dilute_active'] = True

    def stop_dilute(self):
        self.data['is_dilute_active'] = False
        self._residual_dilute_on = True
        self._residual_dilute_rate = self.data['dilute_rate']

    def boron(self, vol, rate):
        if not self.data['is_boron_active']:
            self.data['boron_vol'] = vol
            self.data['boron_rate'] = rate
            self.data['is_boron_active'] = True

    def stop_boron(self):
        self.data['is_boron_active'] = False
        self._residual_boron_on = True
        self._residual_boron_rate = self.data['boron_rate']

    def update(self):
        loop_bc = self.data['loop_bc']
        rcp_vol = self.data['rcp_vol']
        boron_value = Tools.lookup(self.data['boron_value'], loop_bc)
        tank_bc = self.data['tank_bc']
        dilute_vol = self.data['dilute_vol']
        dilute_rate = self.data['dilute_rate']
        boron_vol = self.data['boron_vol']
        boron_rate = self.data['boron_rate']
        if self.data['is_dilute_active']:
            e = exp(-dilute_rate / 3600 / rcp_vol)
            if dilute_vol < (dilute_rate / 3600):
                self.data['dilute_vol'] = 0
                self.stop_dilute()
            else:
                loop_bc *= e
                self.data['dilute_vol'] -= dilute_rate / 3600
        elif self.data['is_boron_active']:
            e = exp(-boron_rate / 3600 / rcp_vol)
            if boron_vol < (boron_rate / 3600):
                self.data['boron_vol'] = 0
                self.stop_boron()
            else:
                loop_bc = e * loop_bc + (1 - e) * tank_bc
                self.data['boron_vol'] -= boron_rate / 3600
        elif self._residual_boron_on:
            if self._residual_boron_rate > 0.1:
                e = exp(-self._residual_boron_rate / 3600 / rcp_vol)
                loop_bc = e * loop_bc + (1 - e) * tank_bc
                self._residual_boron_rate *= 2 ** (-1 / self.data['boron_rate_half_time'])
                print('boron rate = %f, boron half time = %d' % (self._residual_boron_rate,
                                                                 self.data['boron_rate_half_time']))
            else:
                self._residual_boron_on = False
        elif self._residual_dilute_on:
            if self._residual_dilute_rate > 0.1:
                e = exp(-self._residual_dilute_rate / 3600 / rcp_vol)
                loop_bc *= e
                self._residual_dilute_rate *= 2 ** (-1 / self.data['dilute_rate_half_time'])
            else:
                self._residual_dilute_on = False

        rho = (loop_bc - self.data['loop_bc']) * boron_value
        self.data['delta_rho'] = rho
        self.data['loop_bc'] = loop_bc


class Reac(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self.systems = []
        self.previous_random = norm_module.rvs(0, data['reactivity_accuracy'], 1)[0]

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

        # 将反应性加上相邻两个随机数的差，而不是直接加上一个随机数，这样做的目的是消除长时间随机数累加和的漂移。
        current = norm_module.rvs(0, self.data['reactivity_accuracy'], 1)[0]
        self.data['reactivity'] += current - self.previous_random
        self.previous_random = current


class KIC(System, clock.Observer):
    def __init__(self, data):
        System.__init__(self, data)
        self.systems = []

    def add_systems(self, s):
        self.systems.append(s)

    def update(self):
        system_dict = {s.get_data()['name']: s for s in self.systems}
        self.data['core_power'] *= (2 ** (1 / system_dict['reac'].double_time()))

        power = self.data['core_power']
        src1_accuracy = self.data['src1_accuracy']
        src2_accuracy = self.data['src2_accuracy']
        irc1_accuracy = self.data['irc1_accuracy']
        irc2_accuracy = self.data['irc2_accuracy']
        self.data['irc1'] = power / self.data['irc1a2fp'] * (1 + norm_module.rvs(0, src1_accuracy, 1)[0])
        self.data['irc2'] = power / self.data['irc2a2fp'] * (1 + norm_module.rvs(0, src2_accuracy, 1)[0])
        self.data['src1'] = power / self.data['src1cps2fp'] * (1 + norm_module.rvs(0, irc1_accuracy, 1)[0])
        self.data['src2'] = power / self.data['src2cps2fp'] * (1 + norm_module.rvs(0, irc2_accuracy, 1)[0])
