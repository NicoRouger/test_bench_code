import pyvisa
import threading
from queue import Queue
import time

from lib.KEYTHLEY2000 import KEYTHLEY2000

# from gui import gui

import sys
import threading

def main_app(shared_data):
	rm = pyvisa.ResourceManager('@py')
	d = KEYTHLEY2000(rm, 'ASRL/dev/cu.usbserial-2110::INSTR')
	d.check(role="temp1", name='KEITHLEY INSTRUMENTS INC.,MODEL 2000,1308393,A20  /A02', port="A")

	# d.displayText("OwnTech")
	# d.animateText("OwnTech")

	d.configTemp(rjunc=26)
	d.getTemp()
	print(d.measureVoltage())
	print(d.measureCurrent())

if __name__ == "__main__":
	shared_data = Queue()
	main_app(shared_data)
