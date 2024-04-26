import pyvisa
import threading
from queue import Queue
import time

from lib.KEYTHLEY2000 import KEYTHLEY2000
from lib.NGL202 import NGL202

# from gui import gui

import sys
import threading

def main_app(shared_data):
	rm = pyvisa.ResourceManager()
	# d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	# d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	# # d.displayText("OwnTech")
	# # d.animateText("OwnTech")

	# d.configTemp(rjunc=26)
	# d.getTemp()
	# print(d.measureVoltage())
	# print(d.measureCurrent())
	print(rm.list_resources())
	d = NGL202(rm, 'ASRL8::INSTR')
	d.check(role="PSU", name="Rohde&Schwarz,NGL202,3638.3376k03/105048,04.000 002CBB20D8F", port="1")

	d.set_channel(1) #select the channel 1 to do the setup on this specific channel
	d.enable_channel() #enable the channel (turn the green light for the channel)
	d.set_min_voltage(0) #set the minimum voltage available (min in 0)
	d.set_max_voltage(20) #set the maximum voltage available (max is 20.05)
	#d.set_min_current(0) #set the minimum current available (min in 0)
	d.set_max_current(3.01) #set the maximum current available (max is 6.01a bellow 6v and 3.01a from that point)
	d.set_current(3)

	d.set_channel(2)
	d.enable_channel()
	d.set_max_voltage(0)
	d.set_max_voltage(20) 
	#d.set_min_current(0)
	d.set_max_current(3.01)
	d.set_current(3)

	step_volt = 1 #in v
	start_volt = 0
	stop_volt = 20

	for x in range(start_volt, stop_volt + step_volt, step_volt):	
		d.set_channel(1)
		d.set_voltage(x/2)
		d.set_channel(2)
		d.set_voltage(x/2)
		time.sleep(1)
	
	d.disable_output()

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
