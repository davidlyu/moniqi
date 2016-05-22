from gui import Gui
from PyQt4 import QtGui
import system
import data

reac_data = data.ReacData()
reac_sys = system.Reac(reac_data)
# for i in range(1, 21):
#     print(round(reac_sys.rho_d(i), 2), i)
print(reac_sys.double_time(-20))
