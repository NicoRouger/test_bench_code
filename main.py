import pyvisa
import threading
from queue import Queue
import time

from lib.KEYTHLEY2000 import KEYTHLEY2000

from owntech.Twist_Class import Twist_Device
from owntech import find_devices

import sys
import threading

import serial



def main_app(shared_data):
	# rm = pyvisa.ResourceManager('@py')
	# d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	# d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	twist_vid = 0x2fe3
	twist_pid = 0x0100

	Twist_ports = find_devices.find_twist_device_ports(twist_vid, twist_pid)
	print(Twist_ports)

	Twist = Twist_Device(twist_port= Twist_ports[0])

	message = Twist.sendCommand("IDLE")
	print(message)

	message = Twist.sendCommand( "BUCK", "LEG2", "ON")
	print(message)
	message = Twist.sendCommand( "BUCK", "LEG1", "ON")
	print(message)

	message = Twist.sendCommand("LEG","LEG1","ON")
	print(message)
	message = Twist.sendCommand("LEG","LEG2","ON")
	print(message)

	message = Twist.sendCommand("DEAD_TIME_RISING", "LEG1", 300)
	print(message)
	message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG1", 100)
	print(message)

	message = Twist.sendCommand("DEAD_TIME_RISING", "LEG2", 300)
	print(message)
	message = Twist.sendCommand("DEAD_TIME_FALLING", "LEG2", 100)
	print(message)

	message = Twist.sendCommand("POWER_ON")
	print(message)

	message = Twist.sendCommand("DUTY", "LEG1", 0.5)
	print(message)
	message = Twist.sendCommand("DUTY", "LEG2", 0.5)
	print(message)

	message = Twist.sendCommand("PHASE_SHIFT", "LEG2", 0)
	print(message)


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
