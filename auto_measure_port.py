import os
import serial
import pyvisa
import time
import sys
import json
from datetime import datetime

import vna_8722ES_readparams 

class SerialControllerBoardInterface():

    def __init__(self):
        #define constants for byte package size
        self._header_len = 5
        #define constants for masking
        self._rsp_mask_master = 0x50
        self._rsp_mask_status = 0xAA
        self._rsp_mask_data = 0xBB
        self._rsp_codes = {
            1:"ACK",
            2:"Unknown Group",
            3:"Unknown Command",
            4:"Invalid Argument Length",
            5:"Invalid Argument",
            6:"Error processing command",
        }
        self._serial_port = None

    def open_port(self,serial_port_name):
        if self._serial_port is not None:
            return
        self._serial_port = serial.Serial(serial_port_name,115200)

    def close_port(self):
        if self._serial_port is None:
            return
        self._serial_port.close()
        self._serial_port = None

    def build_command(self,group,command,data = []):
        header = []
        if type(data) is int:
            data = [data]
        elif type(data) is not list:
            raise Exception("Data format is not correct (list or str)")
        
        header.append(0xAF)
        header.append(len(data))
        header.append(0xFF)
        header.append(group)
        header.append(command)
        return bytearray(header + data)
            
    
    def send_command(self,cmd_bin,rsp_len):
        self._serial_port.write(cmd_bin)
        bytes_read = []
        try:
            bytes_read = self._serial_port.read(rsp_len)
        except:
            print("Error reading bytes")

        if len(bytes_read) < rsp_len:
            print("Error reading, len not matched")
            return

        if bytes_read[0] != self._rsp_mask_master:
            raise Exception("Master Mask Error")
        if bytes_read[2] == self._rsp_mask_status:
            #Check if ACK(1) or Error 
            if bytes_read[1] != 1:
                raise Exception(self._rsp_codes[bytes_read[1]] if bytes_read[1] in self._rsp_codes[bytes_read[1]] else "Unkwown error code" )
        
            return []

        elif bytes_read[2] == self._rsp_mask_data:
            #Check Len
            if int(bytes_read[1]) != rsp_len - self._header_len:
                raise Exception("Length provided does not match received")
            return bytes_read[self._header_len:len(bytes_read)]
        else:
            raise Exception("Unknown response")

class ControllerBoardInterface():
    def __init__(self,port_name):
        self._serial_ctrl = SerialControllerBoardInterface()
        self._port_name = port_name

    def board_complete_init(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x05),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()

    def board_complete_init_rx(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x0C),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()
    
    def board_complete_init_rx_channel(self,channel):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x0D,channel),5)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0x01 << channel),5)
        self._serial_ctrl.close_port()

    def enable_all_channels(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,0xFF),5)
        self._serial_ctrl.close_port()

    def turn_board_on(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x00),5)
        self._serial_ctrl.close_port()

    def init_chip(self):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x05),5)
        self._serial_ctrl.close_port()

    def send_set_phase_amp_to_channel(self,channel,phase,amp):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x08,[channel,phase,amp]),5)
        self._serial_ctrl.close_port()

    def send_phases_amps_once(self,phases,amps):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x09,phases+amps),5)
        self._serial_ctrl.close_port()

    def send_set_phase_amp_to_zero(self):
        some_zeroes_phase = [0 for i in range(0,8)]
        some_zeroes_amp = [0x3F for i in range(0,8)]
        self.send_phases_amps_once(some_zeroes_phase,some_zeroes_amp)
    
    def open_comm_port(self):
        self._serial_ctrl.open_port(self._port_name)
    
    def close_comm_port(self):
        self._serial_ctrl.close_port()

    def send_phases_amps_mutiple(self,phases,amps):
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x09,phases+amps),5)
    
    def enable_channels(self,channels):
        self._serial_ctrl.open_port(self._port_name)
        self._serial_ctrl.send_command(self._serial_ctrl.build_command(0x01,0x03,channels),5)
        self._serial_ctrl.close_port()

def custom_measuremrnt_tx(boardInterface,inst_dir,channels,amplitudes,phases,meas_out):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init() #TX board Init LNA registers and Enable channels
    
    board.enable_channels(channels)
    board.open_comm_port()
    board.send_phases_amps_mutiple(phases,amplitudes)
    board.close_comm_port()
    time.sleep(1);
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource(inst_dir)
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    vna_8722ES_readparams.read_vna_config(inst) #Track VNA config
    vna_8722ES_readparams.measure_s2p(inst,meas_out)
    inst.close()


def phase_measurement(board,inst,channel):
    amplitudes = [0x3F for i in range(0,8)]
    print("Starting Phase Measurement")
    board.open_comm_port()
    for i in range(0,64):
        print("Port {} Phase measurement {}({}º)".format(channel,i,i*(11.25/2)))
        phases = [i if x == channel else 0 for x in range(0,8)]
        start = time.time()
        board.send_phases_amps_mutiple(phases,amplitudes)
        vna_8722ES.measure_s2p(inst,"P{}_pha_{}".format(channel,i))
        end = time.time()
        print("Time State {}s".format(end-start))
    board.close_comm_port()

def amplitude_measurement(board,inst,channel):
    phases = [0 for i in range(0,8)]
    board.open_comm_port()
    for i in range(0,63):
        print("Port {} Amp measurement {}dB".format(channel,(i)*0.5))
        amplitudes = [(63-i) if x == channel else 0x3F for x in range(0,8)]
        start = time.time()
        board.send_phases_amps_mutiple(phases,amplitudes)
        vna_8722ES.measure_s2p(inst,"P{}_amp_{}".format(channel,(i)))
        end = time.time()
        print("Time State {}s".format(end-start))
    board.close_comm_port()

def zerostate_measuremet(boardInterface):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    for channel in range(0,8):
        board.board_complete_init() #Init LNA registers and Enable channels
        board.send_set_phase_amp_to_zero()
        time.sleep(1);
        input("Check Power Consumption!!")
        try:
            inst = rm.open_resource('GPIB0::15::INSTR')
        except:
            print("Error openning instrument")
            exit()
        inst.timeout = 20000
        vna_8722ES.measure_s2p(inst,"P{}_zero".format(channel))
        inst.close()
        if channel != 7:
            input("Channel Done, change vna port and reset PSU")

def single_channel_measurement_rx(boardInterface,channel=0,phase = 0,amp = 0x3F):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init_rx_channel(channel) #Init LNA registers and Enable channels
    board.send_set_phase_amp_to_channel(channel,phase,amp)
    time.sleep(1);
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource('GPIB0::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    vna_8722ES.measure_s2p(inst,"P{}_single_phase_{}_amp_{}".format(channel,phase,amp))
    inst.close()

def single_channel_measurement_tx(boardInterface,channel=0,phase = 0,amp = 0x3F):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init() #TX board Init LNA registers and Enable channels
    board.enable_channels(1 << channel)
    board.send_set_phase_amp_to_channel(channel,phase,amp)
    time.sleep(1);
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource('GPIB1::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    vna_8722ES_readparams.read_vna_config(inst)
    vna_8722ES_readparams.measure_s2p(inst,"P{}_single_phase_{}_amp_{}".format(channel,phase,amp))
    inst.close()

def branchline_measurement(boardInterface,channels=[]):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init_rx() #Init LNA registers and Enable channels
    time.sleep(1);
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource('GPIB0::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    texts = ["Measuring P1->COM (ON)","Measuring P2->COM (ON)","Measuring P1->P2 (ON)"]
    texts2 = ["Measuring P1->COM (OFF)","Measuring P2->COM (OFF)","Measuring P1->P2 (OFF)"]
    output_files_on = ["rx_branch_port1_p{}_port2_p{}_on".format(channels[0],"com"),"rx_branch_port1_p{}_port2_p{}_on".format(channels[1],"com"),"rx_branch_port1_p{}_port2_p{}_on".format(channels[0],channels[1])]
    output_files_off = ["rx_branch_port1_p{}_port2_p{}_off".format(channels[0],"com"),"rx_branch_port1_p{}_port2_p{}_off".format(channels[1],"com"),"rx_branch_port1_p{}_port2_p{}_off".format(channels[0],channels[1])]

    for i in range (0,3):
        print(texts[i])
        board.board_complete_init_rx()
        board.send_set_phase_amp_to_channel(channels[0],0,0x3F)
        board.send_set_phase_amp_to_channel(channels[1],0,0x00)
        #Measure
        vna_8722ES_readparams.measure_s2p(inst,output_files_on[i])
        board.board_complete_init_rx()
        board.enable_channels(0x01 << channels[0])
        print(texts2[i])
        input("Check power consumption")
        board.send_set_phase_amp_to_channel(channels[0],0,0x3F)
        #Measure
        vna_8722ES_readparams.measure_s2p(inst,output_files_off[i])
        input("Change Port")

    inst.close()

def switching_measurement(boardInterface,port,channels_sequence):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    board.board_complete_init() #TX board Init LNA registers and Enable channels
    time.sleep(1);
    input("Check Power Consumption!! (All channels enabled with max attenuation)")
    board.enable_channels(0xFF)
    time.sleep(1);
    board.send_set_phase_amp_to_channel(0,0,0x3F)
    board.send_set_phase_amp_to_channel(1,0,0x3F)
    board.send_set_phase_amp_to_channel(2,0,0x3F)
    board.send_set_phase_amp_to_channel(3,0,0x3F)
    board.send_set_phase_amp_to_channel(4,0,0x3F)
    board.send_set_phase_amp_to_channel(5,0,0x3F)
    board.send_set_phase_amp_to_channel(6,0,0x3F)
    board.send_set_phase_amp_to_channel(7,0,0x3F)
    input("Check Power Consumption!! (All channels disabled with min attenuation)")
    """
    try:
        inst = rm.open_resource('GPIB0::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    """
    #inst.timeout = 20000
    enable_channels_bits = 0
    enabled_channels = 0

    for i in range(0,len(channels_sequence)):
        enable_channels_bits = enable_channels_bits | (1 << channels_sequence[i])
        board.enable_channels(enable_channels_bits)
        for j in range(0,i+1):
            board.send_set_phase_amp_to_channel(channels_sequence[j],0,0x3F)
        #input("Check power consumption")
        time.sleep(1)
        #vna_8722ES.measure_s2p(inst,"med_switching_p_{}_channels_on_{}".format(port,i+1))
    inst.close()
    
def power_curve_calibration(instaddr,min_power,max_power):
    rm = pyvisa.ResourceManager()
    folder = "Calibrations"
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource(instaddr)
    except:
        print("Error openning instrument")
        exit()
    vna_8722ES_readparams.read_vna_config(inst) #Track VNA config
    input("P1-Short P2-Open")
    vna_8722ES_readparams.power_sweep_measurement(inst,min_power,max_power,os.path.join(folder,"P1-Short:P2-Open"))
    input("P1-Load P2-Short")
    vna_8722ES_readparams.power_sweep_measurement(inst,min_power,max_power,os.path.join(folder,"P1-Load:P2-Short"))
    input("P1-Open P2-Load")
    vna_8722ES_readparams.power_sweep_measurement(inst,min_power,max_power,os.path.join(folder,"P1-Open:P2-Load"))
    input("Thru")
    vna_8722ES_readparams.power_sweep_measurement(inst,min_power,max_power,os.path.join(folder,"Thru"))

def power_curve_measurement(boardInterface,instaddr,min_power,max_power,channels,phases,amplitudes,filename):
    board = ControllerBoardInterface(boardInterface)
    rm = pyvisa.ResourceManager()
    #Board Programming
    board.board_complete_init() #TX board Init LNA registers and Enable channels
    board.enable_channels(channels)
    board.send_phases_amps_mutiple(phases,amplitudes)
    time.sleep(1);
    input("Check Power Consumption!!")
    try:
        inst = rm.open_resource(instaddr)
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    vna_8722ES_readparams.read_vna_config(inst) #Track VNA config
    vna_8722ES_readparams.power_sweep_measurement(inst,min_power,max_power,filename)
    inst.close()
    board.close_comm_port()


if __name__ == "__main__":
    boardInterface = "COM6"
    instaddr = "GPIB0::15::INSTR"
    if len(sys.argv) > 1:
        if sys.argv[1] == "zerostate":
            zerostate_measuremet(boardInterface)
        elif sys.argv[1] == "tx":
            if len(sys.argv) >= 3:
                single_channel_measurement_tx(boardInterface,channel = int(sys.argv[2]))
        elif sys.argv[1] == "rx":
            if len(sys.argv) >= 3:
                single_channel_measurement_rx(boardInterface,channel = int(sys.argv[2]))
        elif sys.argv[1] == "branchline":
            if len(sys.argv) == 4:
                branchline_measurement(boardInterface,channels = [int(sys.argv[2]),int(sys.argv[3])])
        elif sys.argv[1] == "switching":
            if len(sys.argv) == 4:
                channel_list = [int(i) for i in sys.argv[3].split(" ")] 
                switching_measurement(boardInterface,int(sys.argv[2]),channel_list)
        elif sys.argv[1] == "powercal":
            min_power = int(sys.argv[2])
            max_power = int(sys.argv[3])
            if (max_power > -10):
                print("Max power out of range")
                exit()
            if (min_power < -35):
                print("Min power out of range")
                exit()
            power_curve_calibration(instaddr,min_power,max_power)
        elif sys.argv[1] == "config":
            if(len(sys.argv) < 3):
                print("No file loaded selected")
                exit()
            #Read JSON
            try: 
                f = open(sys.argv[2])
                data = json.load(f)
                f.close()
            except (IOError, OSError) as e:
                print(e)
                f.close()
                exit()
            #Parse JSONs
            if data["board"] == "xphased_tx":
                amplitudes = []
                phases = []
                enables = 0
                vna_dir = ""
                out_file = sys.argv[2]
                if(len(sys.argv) >= 4):
                    out_file = sys.argv[3]
                try:
                    data_sorted = sorted(data["channels_config"],key=lambda k: k["descriptor"].lower())
                    for channel_index in range(0,len(data_sorted)):
                        amplitudes.append(data_sorted[channel_index]["amp"])
                        phases.append(data_sorted[channel_index]["pha"])
                        enables = enables | (int(data_sorted[channel_index]["enable"]) << channel_index)
                except:
                    print("Error in channel config")
                    print("Line {}".format(channel_index))

                try:
                    vna_dir = data["vna_config"]["addr"]
                except:
                    print("Error in VNA config")
                #Special Modes
                if(len(sys.argv) >= 5):
                    if(sys.argv[4] == "power"):
                        if(len(sys.argv) < 7):
                            print("Error in arguments for power mode")
                            exit()
                        try:
                            min_power = int(sys.argv[5])
                            max_power = int(sys.argv[6])
                            if (max_power > -10):
                                print("Max power out of range")
                                exit()
                            if (min_power < -35):
                                print("Min power out of range")
                                exit()
                        except:
                            print("Invalid Power arguments")
                            exit()
                        power_curve_measurement(boardInterface,vna_dir,min_power,max_power,enables,phases,amplitudes,out_file)
                #Normal Measurement
                else:
                    custom_measuremrnt_tx(boardInterface,vna_dir,enables,amplitudes,phases,out_file)
            
        exit()
        
    #Full measurement
    #Init board
    board = ControllerBoardInterface(boardInterface)
    board.board_complete_init()
    board.send_set_phase_amp_to_zero()

    #board.send_phases_amps_once([i for i in range(0,8)],[7-i for i in range(0,8)])
    #Init instrument
    rm = pyvisa.ResourceManager()
    try:
        inst = rm.open_resource('GPIB0::15::INSTR')
    except:
        print("Error openning instrument")
        exit()
    inst.timeout = 20000
    print(inst.query("*IDN?"))
    input("Hit Enter to start measurements")
    time_all_start = time.time()
    channel = 3
    print("Starting channel {} Measurement".format(channel))
    time_start_channel = time.time()
    phase_measurement(board,inst,channel)
    amplitude_measurement(board,inst,channel)
    time_end_channel = time.time()
    print("Total port time {}s".format(time_end_channel-time_start_channel))
    #input("Change vna p2 and hit enter")
    time_all_end = time.time()
    print("Measurement done in {}s".format(time_all_end-time_all_start))
    inst.close()


    