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

import serial

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

def resource_init():
	rm = pyvisa.ResourceManager()
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

def supply_init():
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
	digit_voltage, digit_current, digit_temp1, digit_temp2 = resource_init()
	supply = supply_init()

	# Dictionnary to store results
	res = {'Voltage':[], 'Current':[], 'Temp1':[], 'Temp2':[]}

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
	df.to_csv('res_2024.csv')
		
	# rm = pyvisa.ResourceManager('@py')
	# d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	# d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	
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

	# d.displayText("OwnTech")
	# d.animateText("OwnTech")

	# d.configTemp(rjunc=26)
	# d.getTemp()
	# print(d.measureVoltage())
	# print(d.measureCurrent())

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
