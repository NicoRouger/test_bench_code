import pyvisa
import threading
from queue import Queue
import time
import pandas as pd
import matplotlib.pyplot as plt

from lib.KEYTHLEY2000 import KEYTHLEY2000
from lib.NGL202 import NGL202

from owntech.Twist_Class import Twist_Device
from owntech import find_devices

import sys
import threading
import matplotlib.pyplot as plt
import serial

SCOPE_ADDRESS = 'USB0::0x0699::0x0522::C062816::INSTR'


def config_scope(scope):
	# print('Scope ID: {}\n'.format(scope.query('*IDN?'))
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

def get_scope_data(scope):
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

	return time, data, wfid, yunit

def plot_scope_data(scope_time, data, wfid, yunit):
	plt.plot(scope_time, data, label=wfid)
	plt.xlabel("Time (s)")
	plt.ylabel(f"{wfid.split(',')[0]} ({yunit})")
	plt.grid()
	plt.legend()
	plt.show()
 
def twist_init():
	twist_vid = 0x2fe3
	twist_pid = 0x0100

	Twist_ports = find_devices.find_twist_device_ports(twist_vid, twist_pid)
	print(Twist_ports)

	Twist = Twist_Device(twist_port= Twist_ports[0])

	message = Twist.sendCommand("IDLE")
	message = Twist.sendCommand( "BUCK", "LEG2", "ON")
	message = Twist.sendCommand( "BUCK", "LEG1", "ON")
	message = Twist.sendCommand("LEG","LEG1","ON")
	message = Twist.sendCommand("LEG","LEG2","ON")
	message = Twist.sendCommand("DEAD_TIME_RISING", "LEG1", 300)
	message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG1", 100)
	message = Twist.sendCommand("DEAD_TIME_RISING", "LEG2", 300)
	message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG2", 100)
	message = Twist.sendCommand("POWER_ON")
	message = Twist.sendCommand("DUTY", "LEG1", 0.5)
	message = Twist.sendCommand("DUTY", "LEG2", 0.5)
	message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 0)
	print("Twist init OK")
	return Twist

def measure_devices_init(rm):
	
	# Get measurement devices
	digit_voltage = KEYTHLEY2000(rm, 'GPIB0::3::INSTR')
	digit_current = KEYTHLEY2000(rm, 'GPIB0::1::INSTR')
	digit_temp1 = KEYTHLEY2000(rm, 'GPIB0::2::INSTR')
	digit_temp2 = KEYTHLEY2000(rm, 'GPIB0::4::INSTR')
	# Check
	digit_voltage.check(role="voltage_high", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1053308,A19  /A02', port="A")
	digit_current.check(role="current_high", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,0972521,A17  /A02', port="A")
	digit_temp1.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1102655,A19  /A02', port="A")
	digit_temp2.check(role="temp2", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")
	digit_temp1.configTemp(rjunc=26)
	digit_temp2.configTemp(rjunc=26)
	print("init measurement devices OK")
	return digit_voltage, digit_current, digit_temp1, digit_temp2

def supply_init(rm):
	rm = pyvisa.ResourceManager()
	print(rm.list_resources())
	supply = NGL202(rm, 'ASRL8::INSTR')
	supply.check(role="PSU", name="Rohde&Schwarz,NGL202,3638.3376k03/105048,04.000 002CBB20D8F", port="1")

	# Config DC supply
	supply.set_channel(1) #select the channel 1 to do the setup on this specific channel
	supply.enable_channel() #enable the channel (turn the green light for the channel)
	supply.set_min_voltage(0) #set the minimum voltage available (min in 0)
	supply.set_max_voltage(20) #set the maximum voltage available (max is 20.05)
	#supply.set_min_current(0) #set the minimum current available (min in 0)
	supply.set_max_current(3.01) #set the maximum current available (max is 6.01a bellow 6v and 3.01a from that point)
	supply.set_current(3)

	supply.set_channel(2)
	supply.enable_channel()
	supply.set_max_voltage(0)
	supply.set_max_voltage(20) 
	#supply.set_min_current(0)
	supply.set_max_current(3.01)
	supply.set_current(3)
	print("init supply OK")
	return supply

def main_app(shared_data):
	rm = pyvisa.ResourceManager()
	digit_voltage, digit_current, digit_temp1, digit_temp2 = measure_devices_init(rm)
	supply = supply_init(rm)
	scope = rm.open_resource(SCOPE_ADDRESS)
	scope_time, data, wfid, yunit = get_scope_data(scope)

	plot_scope_data(scope_time, data, wfid, yunit)

	# Dictionnary to store results
	res = {'Voltage':[], 'Current':[], 'Temp1':[], 'Temp2':[]}

	# Drive duty cycle and phase shift
	Twist = twist_init()

	# while True:
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

	# Config supply ramp
	step_volt = 1 #in v
	start_volt = 0
	stop_volt = 4

	for x in range(start_volt, stop_volt + step_volt, step_volt):
		supply.set_channel(1)
		supply.set_voltage(x/2)
		supply.set_channel(2)
		supply.set_voltage(x/2)
		res['Voltage'].append(digit_voltage.measureVoltage())
		res['Current'].append(digit_current.measureCurrent())
		res['Temp1'].append(digit_temp1.getTemp())
		res['Temp2'].append(digit_temp2.getTemp())
		time.sleep(1)

	df = pd.DataFrame(res)
	df.to_csv('res_2024.csv', index=False)
	
	scope.close()
	rm.close()

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
