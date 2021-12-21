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



def measure_m_file(boardInterface,instaddr,channel: int):
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
        board.send_set_phase_amp_to_channel(c,0,0x3F)
    #Set amps
    for i in range(0,64):
        print("Medida {}/{}".format(i+1,128))
        board.send_set_phase_amp_to_channel(channel,0,i)
        time.sleep(0.2)
        vna_8722ES_readparams.measure_s2p(inst,"Caracterizacion/ch{}_amp{}_max".format(channel,i));
    #Set phases
    for i in range(0,64):
        print("Medida {}/{}".format(i+64,128))
        board.send_set_phase_amp_to_channel(channel,i,0x3F)
        time.sleep(0.2)
        vna_8722ES_readparams.measure_s2p(inst,"Caracterizacion/ch{}_pha{}_max".format(channel,i));  
    inst.close()

if __name__ == "__main__":
    channel = int(0)
    start = time.time()
    measure_m_file("COM3","GPIB0::15::INSTR",channel)
    end = time.time()
    print("Esta vaina ha tardado {}s".format(end-start))
