from matplotlib.pyplot import switch_backend
from numpy.lib.function_base import append
import pyvisa
import matplotlib.pyplot as plt
import numpy as np
import skrf as rf 

import struct
import time
import sys
import os.path

freq_start = 0.1
freq_end = 3
n_points = 801
bw_if = 100

def config_vna(instrument):
    instrument.write("STAR {} GHZ;".format(freq_start))
    instrument.write("STOP {} GHZ;".format(freq_end))
    instrument.write("LINFREQ;")
    instrument.write("POIN {};".format(n_points))
    instrument.write("IFBW {};".format(bw_if))

def read_vna_config(instrument):
    global freq_end,freq_start,n_points
    freq_start = float(instrument.query("STAR?;"))
    freq_end = float(instrument.query("STOP?;"))
    n_points = int(float(instrument.query("POIN?;")))

def config_vna_power(instrument,power):
    instrument.write('POWE{};'.format(power))

def config_channel_setup(instrument):
    instrument.write('SPLID4;')
    instrument.write('CHAN1;')
    instrument.write('S11;')
    instrument.write("POLA;")
    instrument.write("POLMRI;")
    instrument.write('CHAN2;')
    instrument.write('S21;')
    instrument.write("POLA;")
    instrument.write("POLMRI;")
    instrument.write('CHAN3;')
    instrument.write('S12;')
    instrument.write("POLA;")
    instrument.write("POLMRI;")
    instrument.write('CHAN4;')
    instrument.write('S22;')
    instrument.write("POLA;")
    instrument.write("POLMRI;")

def return_config_channel_setup(instrument):
    instrument.write('SPLID4;')
    instrument.write('CHAN1;')
    instrument.write('S11;')
    instrument.write("LOGM;")
    instrument.write('CHAN2;')
    instrument.write('S21;')
    instrument.write("LOGM;")
    instrument.write('CHAN3;')
    instrument.write('S12;')
    instrument.write("LOGM;")
    instrument.write('CHAN4;')
    instrument.write('S22;')
    instrument.write("LOGM;")

def measure_s_param_float32(instrument,graphTitle=""):
    instrument.write("FORM2;")
    instrument.write("OUTPFORM;")
    data = instrument.read_raw()
    #print(str(data[0:2]))
    #num_data = int.from_bytes(data[2:4],"big")
    #print(num_data)
    #print(len(data))
    trace = convert_to_ieee_float32(data[4:len(data)])
    # print(trace)
    # ax = np.linspace(freq_start,freq_end,n_points)
    # plt.plot(ax,20*np.log10(np.absolute(trace)))
    return np.transpose(np.matrix(trace))
    

def measure_s2p(instrument,filename,format="f32"):
    s2p_matrix = np.transpose(np.matrix(np.linspace(freq_start,freq_end,n_points)))
    if format == "f32":
        measure_fun = measure_s_param_float32;
    else:
        raise Exception("Unvalid format for the instrument")
    config_channel_setup(instrument)
    print("Single Trig")
    start = time.time()
    resp_trig = instrument.query("OPC?;SING;")
    if resp_trig == "1\n":
        print("Trigger Done")
    else:
        print("Trigger Error")
    end = time.time()
    print("Trigger time {}s".format(end-start))
    for i in range(1,5):
        instrument.write("CHAN{}".format(i))
        new_data = measure_fun(instrument)
        s2p_matrix = np.concatenate((s2p_matrix, new_data),axis=1)
    #print(s2p_matrix)
    with open('save.npy', 'wb') as f:
        np.save(f, s2p_matrix)
    instrument.write("CONT;")

    freq2 = rf.Frequency(start=freq_start,stop=freq_end,npoints=n_points, unit='GHz')
    s = np.empty((len(s2p_matrix[:,1]), 2, 2),dtype=complex)
    s[:,0,0] = s2p_matrix[:,1].flatten() #S11
    s[:,0,1] = s2p_matrix[:,3].flatten() #S12
    s[:,1,0] = s2p_matrix[:,2].flatten() #S21
    s[:,1,1] = s2p_matrix[:,4].flatten() #S22

    ntw = rf.Network(frequency=freq2, s=s)
    save_s2p(ntw,"{}.s2p".format(filename))
    return_config_channel_setup(instrument)

def power_sweep_measurement(instrument,power_min,power_max,filename):
    for power in range(power_min,power_max+1):
        config_vna_power(instrument,power)
        measure_s2p(instrument,"{}_po{}".format(filename,power))

def convert_to_ieee_float32(data):
    real = np.array([])
    imag = np.array([])
    for i in range(0,len(data),4):
        num = struct.unpack('>f', data[i:i+4])
        if i % 8 == 0:
            real = np.append(real,num)
        else:
            imag = np.append(imag,num)

    return real + 1j*imag

def save_s2p(rf_ntw,filename):
    if os.path.isfile(filename):
        while True:
            rsp = input("The file already exists, do you want to overwrite it (Y/n/q): ")
            if rsp == "y" or rsp == "yes" or rsp == "":
                break;
            elif rsp == "n" or rsp == "no":
                filename = input("Write a new filename (.s2p not needed)")
                break;
            elif rsp=="q" or rsp =="Quit":
                print("Measurement not saved to file")
                return 
            print("Try Again :(")

    rf_ntw.write_touchstone(filename)

    
def plot_s2p(s2p_data):
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].plot(s2p_data[:,0], s2p_data[:,1])
    axs[0, 0].set_title('S11')
    axs[0, 1].plot(s2p_data[:,0], s2p_data[:,2], 'tab:orange')
    axs[0, 1].set_title('S21')
    axs[1, 0].plot(s2p_data[:,0], s2p_data[:,3], 'tab:green')
    axs[1, 0].set_title('S12')
    axs[1, 1].plot(s2p_data[:,0], s2p_data[:,4], 'tab:red')
    axs[1, 1].set_title('S22')

    for ax in axs.flat:
        ax.set(xlabel='x-label', ylabel='y-label')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    for ax in axs.flat:
        ax.label_outer()


if __name__ == "__main__":
    rm = pyvisa.ResourceManager()
    #print(rm.list_resources())
    try:
        inst = rm.open_resource('GPIB1::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    print(inst.query("*IDN?"))
    if len(sys.argv) < 2:
        config_vna(inst)
        print("VNA Configured")
        inst.close()
        exit()
    read_vna_config(inst)
    #config_vna(inst)
    start = time.time()
    measure_s2p(inst,str(sys.argv[1]))
    end = time.time()
    print("Total Time time {}s".format(end-start))
    inst.close()


