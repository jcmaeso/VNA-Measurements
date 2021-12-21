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


def measure_m_file(boardInterface,instaddr,amps: NDArray[(8, ...), np.uint8],phases: NDArray[(8, ...), np.uint8],channel: int):
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
    for state in range(0,amps.shape[1]+1):
        print("Measuring state {}/{}".format(state+1,amps.shape[1]+1))
        for ch in range(0,8):
            board.send_set_phase_amp_to_channel(ch,int(phases[state,ch]),int(amps[state,ch]))
        vna_8722ES_readparams.measure_s2p(inst,"FA/m_{}_p{}".format(state,channel))
    inst.close()

if __name__ == "__main__":
    m_filename = sys.argv[1]
    channel = int(sys.argv[2])
    try:
        mat_contents = sio.loadmat(m_filename)
        phases = mat_contents["phases_list_discretized"]/(5.625)
        amps = 0x3F + 20*np.log10(mat_contents["amps_list_discretized"])
    except:
        print("Error in mat file")
    measure_m_file("COM3","GPIB0::15::INSTR",amps,phases,channel)
