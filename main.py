import pyvisa
import threading
from queue import Queue
import time
import pandas as pd

from lib.KEYTHLEY2000 import KEYTHLEY2000

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
	print('resources :' , rm.list_resources())
	digit_voltage = KEYTHLEY2000(rm, 'GPIB0::3::INSTR')
	digit_current = KEYTHLEY2000(rm, 'GPIB0::1::INSTR')
	digit_temp1 = KEYTHLEY2000(rm, 'GPIB0::2::INSTR')
	digit_temp2 = KEYTHLEY2000(rm, 'GPIB0::4::INSTR')
	print(digit_temp2.ress.query("*IDN?"))
	digit_voltage.check(role="voltage_high", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1053308,A19  /A02', port="A")
	digit_current.check(role="current_high", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,0972521,A17  /A02', port="A")
	digit_temp1.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1102655,A19  /A02', port="A")
	digit_temp2.check(role="temp2", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	digit_temp1.configTemp(rjunc=26)
	digit_temp2.configTemp(rjunc=26)

	return digit_voltage, digit_current, digit_temp1, digit_temp2


def main_app(shared_data):
	digit_voltage, digit_current, digit_temp1, digit_temp2 = resource_init()

	res = {'Voltage':[], 'Current':[], 'Temp1':[], 'Temp2':[]}

	for i in range(10):
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

	while True:
		time.sleep(10)
		message = Twist.sendCommand("DUTY", "LEG1", 0.55)
		print(message)
		time.sleep(10)
		message = Twist.sendCommand("DUTY", "LEG1", 0.5)
		print(message)
		time.sleep(10)
		message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 10)
		print(message)
		time.sleep(10)
		message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 0)
		print(message)

	# d.displayText("OwnTech")
	# d.animateText("OwnTech")

	# d.configTemp(rjunc=26)
	# d.getTemp()
	# print(d.measureVoltage())
	# print(d.measureCurrent())

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
