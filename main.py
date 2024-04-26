import pyvisa
import threading
from queue import Queue
import time

from lib.KEYTHLEY2000 import KEYTHLEY2000

from owntech.Twist_Class import Twist_Device
from owntech import find_devices

import sys
import threading
import matplotlib.pyplot as plt
import serial

scope_address = 'USB0::0x0699::0x0522::C062816::INSTR'


def config_scope(scope):
	scope.write('*CLS')     # clear the queue
	scope.write('CLEAR')
	scope.write('MEASUrement:DELETEALL')            # Delete all measurements
	scope.write('DISplay:WAVEView1:CH1:STATE ON')   # Enable Ch1
	scope.write('CH1:SCAle 0.5')                    # Set ch1 vertical scale to 0.5V/div
	scope.write('CH1:POSition -3.2')                # Set ch1 vertical position to -3.2 div
	scope.write('HORizontal:SCAle 2e-4')            # Set horizontal scale to 200ns/div
	scope.write('HORizontal:POSition 10')           # Time ref at 10% of the screen
	scope.write('TRIGger:A:EDGE:SOUrce CH1')        # Trigger on ch1
	scope.write('TRIGger:A:LEVel:CH1 0.5')          # Set trigger level at 1V on ch1
	scope.write('TRIGger:A:EDGE:SLOpe RISe')        # Trigger on rising edge
	scope.write('TRIGger:A:EDGE:COUPling NOISErej') # Noise reject coupling mode
	scope.write('TRIGger:A:MODe AUTO')              # Trigger mode auto
	scope.write('DATa:SOUrce CH1')                  # Set ch1 as data source
	scope.write('DATa:ENCdg ASCii')                 # Set data ASCII encoding
	scope.write('WFMOutpre:ENCdg ASCii')            # Preamble encoded in ASCII
	scope.write('WFMOutpre:BYT_Nr 2')               # 2 bytes per sample
	# scope.query('*OPC?')
	# print(scope.query('WFMOutpre?'))                # Print waveform preamble


def main_app(shared_data):
	# rm = pyvisa.ResourceManager('@py')
	# d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	# d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	rm = pyvisa.ResourceManager()
	scope = rm.open_resource(scope_address)

	print('Scope ID: {}\n'.format(scope.query('*IDN?')))     # Print instrument id to console window

	config_scope(scope)

	ymult = float(scope.query('WFMOutpre:YMUlt?').strip('\n'))
	yzero = float(scope.query('WFMOutpre:YZEro?').strip('\n'))
	xincr = float(scope.query('WFMOutpre:XINcr?').strip('\n'))
	ptoff = int(scope.query('WFMOutpre:PT_Off?').strip('\n'))
	xoff = ptoff*xincr

	xunit = scope.query('WFMOutpre:XUNit?').strip('\"\n')
	yunit = scope.query('WFMOutpre:YUNit?').strip('\"\n')

	wfid = scope.query('WFMOutpre:WFId?').strip('\"\n')
	print(wfid)

	wfm_str = scope.query("CURVe?")
	frames = wfm_str.splitlines()[0].split(";")

	print(f'YMULT? : {ymult}')
	print(f'YZERO? : {yzero}')
	print(f'XINCR? : {xincr}')
	print(f'PTOFF? : {ptoff}')
	print(f'XUNIT? : {xunit}')
	print(f'YUNIT? : {yunit}')

	data = [int(b)*ymult+yzero for b in frames[0].split(",")]
	time = [i*xincr-xoff for i in range(len(data))]

	plt.plot(time, data, label=wfid)
	plt.xlabel("Time (s)")
	plt.ylabel(f"{wfid.split(',')[0]} ({yunit})")
	plt.grid()
	plt.legend()
	plt.show()

	scope.close()
	rm.close()

	# twist_vid = 0x2fe3
	# twist_pid = 0x0100
	#
	# Twist_ports = find_devices.find_twist_device_ports(twist_vid, twist_pid)
	# print(Twist_ports)
	#
	# Twist = Twist_Device(twist_port= Twist_ports[0])
	#
	# message = Twist.sendCommand("IDLE")
	# print(message)
	#
	# message = Twist.sendCommand( "BUCK", "LEG2", "ON")
	# print(message)
	# message = Twist.sendCommand( "BUCK", "LEG1", "ON")
	# print(message)
	#
	# message = Twist.sendCommand("LEG","LEG1","ON")
	# print(message)
	# message = Twist.sendCommand("LEG","LEG2","ON")
	# print(message)
	#
	# message = Twist.sendCommand("DEAD_TIME_RISING", "LEG1", 300)
	# print(message)
	# message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG1", 100)
	# print(message)
	#
	# message = Twist.sendCommand("DEAD_TIME_RISING", "LEG2", 300)
	# print(message)
	# message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG2", 100)
	# print(message)
	#
	# message = Twist.sendCommand("POWER_ON")
	# print(message)
	#
	# message = Twist.sendCommand("DUTY", "LEG1", 0.5)
	# print(message)
	# message = Twist.sendCommand("DUTY", "LEG2", 0.5)
	# print(message)
	#
	# message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 0)
	# print(message)
	#
	#
	# while True:
	#
	# 	time.sleep(10)
	# 	message = Twist.sendCommand("DUTY", "LEG1", 0.55)
	# 	print(message)
	# 	time.sleep(10)
	# 	message = Twist.sendCommand("DUTY", "LEG1", 0.5)
	# 	print(message)
	# 	time.sleep(10)
	# 	message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 10)
	# 	print(message)
	# 	time.sleep(10)
	# 	message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 0)
	# 	print(message)

	# d.displayText("OwnTech")
	# d.animateText("OwnTech")

	# d.configTemp(rjunc=26)
	# d.getTemp()
	# print(d.measureVoltage())
	# print(d.measureCurrent())

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
