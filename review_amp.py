import skrf as rf
import matplotlib.pyplot as plt
import numpy as np

import csv

angle_increment = 11.25/2

p0_1 = rf.Network('P0_pha_0.s2p')
amps = [20*np.log10(np.abs(p0_1.s21['29.005ghz'].s[0][0][0]))]
for i in range(1,64):
    new_network = rf.Network('P0_pha_{}.s2p'.format(i))
    amps.append(20*np.log10(np.abs(new_network.s21['29.005ghz'].s[0][0][0])))


with open('amps.csv', mode='w',newline='') as amps_file:
    amps_csv = csv.writer(amps_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    amps_csv.writerow(["State","Amplitude Errpr"])
    for i in range(1,64):
        amps_csv.writerow([i,(amps[i]-amps[0])])



 

