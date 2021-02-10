from matplotlib.pyplot import draw
import skrf as rf
import matplotlib.pyplot as plt
import numpy as np

import csv

angle_increment = 11.25/2
freq = '29.005ghz'

p0_1 = rf.Network('P3_pha_0.s2p')
#p0_2 = rf.Network('P0_pha_1.s2p')
#p0_3 = rf.Network('P0_pha_2.s2p')
#p0_4 = rf.Network('P0_pha_3.s2p')
#p0_5 = rf.Network('P0_pha_4.s2p')
#fig = plt.figure()
#plt.title('Phase Shift (S21)');
#(p0_2/p0_1).plot_s_deg(m=1,n=0)
#(p0_3/p0_1).plot_s_deg(m=1,n=0)
#(p0_4/p0_1).plot_s_deg(m=1,n=0)
#(p0_5/p0_1).plot_s_deg(m=1,n=0)
# plt.legend(['5.625º','11.25º','16.875º','22.5º',])
# plt.ylabel('Phases difference (S21)')
# fig.savefig('Phasecmp.png')
# plt.show()
phases = [np.angle(p0_1.s21[freq].s[0][0][0], deg = True)]
amps = [20*np.log10(np.abs(p0_1.s21[freq].s[0][0][0]))]

for i in range(1,64):
    new_network = rf.Network('P3_pha_{}.s2p'.format(i))
    phases.append(np.angle(new_network.s21[freq].s[0][0][0], deg = True))
    amps.append(20*np.log10(np.abs(new_network.s21[freq].s[0][0][0])))


with open('phases_rx_1_port.csv', mode='w',newline='') as phases_file:
    phases_csv = csv.writer(phases_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    phases_csv.writerow(["State","Theorical Increment","Measured Increment","Error Phase","Error Amplitude"])
    for i in range(0,64):
        phases_csv.writerow([i,i*angle_increment,(phases[i]-phases[0])%360,((phases[i]-phases[0])%360)-i*angle_increment,amps[i]-amps[0]])
 

