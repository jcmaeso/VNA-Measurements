import matplotlib.pyplot as plt
import numpy as np
import skrf as rf
from skrf import network 
from matplotlib.backends.backend_pdf import PdfPages


def multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)
    if figs is None:
        figs = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figs:
        fig.savefig(pp, format='pdf')
    pp.close()


freq = '19.957ghz'
files = ["P{}_single_phase_0_amp_63.s2p".format(i) for i in range(0,8)]
networks = []
#Load listed files
for file in files:
    networks.append(rf.Network(file))

relative_networks = []
reference_network = networks[0]
for network in networks:
    plt.figure("S11")
    plt.title("S11")
    network.plot_s_db(m=0,n=0)
    plt.figure("S22")
    plt.title("S22")
    network.plot_s_db(m=1,n=1)
    plt.figure("S21 (amp)")
    plt.title("S21 (amp)")
    network.plot_s_db(m=1,n=0)
    plt.figure("S21 (phase)")
    plt.title("S21 (phase)")
    network.plot_s_deg(m=1,n=0)
    if network is not reference_network:
        relative_networks.append(network/reference_network)

cnt = 1
for network in relative_networks:
    plt.figure("Relative Amplitudes (P1 as ref)")
    plt.title("Relative Amplitudes (P1 as ref)")
    network.plot_s_db(m=1,n=0)
    plt.figure("Relative Phases (P1 as ref)")
    plt.title("Relative Phases (P1 as ref)")
    network.plot_s_deg(m=1,n=0)
    cnt = cnt + 1

multipage("graficas.pdf")

plt.show()