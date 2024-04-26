import pyvisa
import threading
from queue import Queue
import time

from lib.KEYTHLEY2000 import KEYTHLEY2000
from lib.PSU import PSU

# from gui import gui

import sys
import threading

def main_app(shared_data):
	rm = pyvisa.ResourceManager('@py')
	# d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	# d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	# # d.displayText("OwnTech")
	# # d.animateText("OwnTech")

	# d.configTemp(rjunc=26)
	# d.getTemp()
	# print(d.measureVoltage())
	# print(d.measureCurrent())
	d = PSU(rm, 'ASRL/dev/cu.usbmodem21201::INSTR')
	d.check(role="PSU", name="Rohde&Schwarz,NGL202,3638.3376k03/105048,04.000 002CBB20D8F", port="1")
	d.set_channel(1)
	d.set_max_voltage(0)
	d.set_max_voltage(20)
	d.enable_output()
	time.sleep(1)
	
	d.set_channel(2)
	d.set_max_voltage(0)
	d.set_max_voltage(20)
	d.enable_output()

	step_volt = 1 #in v
	start_volt = 0
	stop_volt = 20

	for x in range(start_volt, stop_volt + step_volt, step_volt):
		d.set_channel(1)
		d.set_voltage(x/2)
		d.set_channel(2)
		d.set_voltage(x/2)
		time.sleep(1)

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
