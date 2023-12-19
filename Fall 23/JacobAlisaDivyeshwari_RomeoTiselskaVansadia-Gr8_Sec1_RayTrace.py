# initialization
from rayoptics.gui.appcmds import *
import matplotlib.pyplot as plt
isdark = True
# Import Zemax file
opm, info = open_model('PS812-C-Zemax(ZMX).zmx',info=True)
print(info)
# Displaying model parameters
sm  = opm['seq_model']
sm.list_model();print('\n--------------------------------------------------------------------------------------------------\n')
# Plotting
# wav_plt = plt.figure(FigureClass=RayFanFigure, opt_model=opm, data_type='OPD', is_dark=isdark).plot()
# plt.title('Aberration Plot')
yybar_plt = plt.figure(FigureClass=InteractiveLayout, opt_model=opm, do_draw_axes=True, do_draw_frame=True, is_dark=isdark).plot()
plt.title('Rounded Wedge Prism Ray Diagram')
plt.text(-33,4,'Point Source\n Distribution',color='red')
plt.text(1.5,14,'Wedge 1',color='red')
plt.text(27,14,'Wedge 2',color='red')
plt.text(45,23,'Screen',color='red')
plt.xlabel('Z-axis [mm]')
plt.ylabel('Y-axis [mm]')
plt.show()