import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
from skrf import network 
from matplotlib.backends.backend_pdf import PdfPages

from os import listdir
from os.path import isfile, join

freq_start = 17.5
freq_end = 21.4
n_points = 401

s2p_files = [f for f in listdir("./") if f.endswith(".s2p")]
new_freq_ax = rf.Frequency(freq_start,freq_end,n_points)
for s2p_file in s2p_files:
    nw = rf.Network(s2p_file)
    nw.frequency = new_freq_ax
    nw.write_touchstone(s2p_file)
