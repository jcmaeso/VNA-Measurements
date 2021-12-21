import os
import serial
import pyvisa
import time
from datetime import datetime
from SerialControllerBoardInterface import SerialControllerBoardInterface

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