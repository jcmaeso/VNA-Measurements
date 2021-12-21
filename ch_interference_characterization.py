import sys
import pyvisa
from ControllerBoardInterface import ControllerBoardInterface
import vna_8722ES_readparams
import time

import numpy as np
import scipy.io as sio

from nptyping import NDArray
from typing import Any


def premeasurement_checks(board):
    board.enable_channels(0xFF)
    for i in range(0,8):
        board.send_set_phase_amp_to_channel(i,0,0)    
    input("Check Power Consumption!! (All channels enabled with max attenuation)")
    time.sleep(1);
    for i in range(0,8):
        board.send_set_phase_amp_to_channel(i,0,0x3F)    
    input("Check Power Consumption!! (All channels enabled with min attenuation)")



def measure_m_file(boardInterface,instaddr,channel: int,pha_state = 0, amp_state = 0x3F):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init() #TX board Init LNA registers and Enable channels
    try:
        inst = rm.open_resource(instaddr)
        inst.timeout = 50000
    except:
        print("Error openning instrument")
        exit()
    time.sleep(1);
    premeasurement_checks(board)
    board.enable_channels(0xFF) #Enable all Channels
    #Set all channels
    for c in range(0,8):
        if c == channel:
            board.send_set_phase_amp_to_channel(c,pha_state,amp_state)
        else:
            board.send_set_phase_amp_to_channel(c,0,0x3F)
    #Set amps
    for mod_ch in range(0,8):
        if mod_ch == channel:
            continue
        for i in range(0,64):
            print("Medida {}/{}".format(i+1,128))
            board.send_set_phase_amp_to_channel(mod_ch,0,i)
            time.sleep(0.2)
            vna_8722ES_readparams.measure_s2p(inst,"intrf/meas_ch{}_state_{}-{}_mod_ch{}_amp{}".format(channel,pha_state,amp_state,mod_ch,i))
        #Set phases
        for i in range(0,64):
            print("Medida {}/{}".format(i+64,128))
            board.send_set_phase_amp_to_channel(mod_ch,i,0x3F)
            time.sleep(0.2)
            vna_8722ES_readparams.measure_s2p(inst,"intrf/meas_ch{}_state_{}-{}_mod_ch{}_pha{}".format(channel,pha_state,amp_state,mod_ch,i))
        #Reset to max amp uniform state
        for c in range(0,8):
            if c == channel:
                board.send_set_phase_amp_to_channel(c,pha_state,amp_state)
            else:
                board.send_set_phase_amp_to_channel(c,0,0x3F) 
    inst.close()

if __name__ == "__main__":
    channel = int(4)
    pha_state = 10
    amp_state = 0x3F
    start = time.time()
    measure_m_file("COM3","GPIB0::15::INSTR",channel,pha_state,amp_state)
    end = time.time()
    print("Esta vaina ha tardado {}s".format(end-start))
