#limits
#20.05 VDC
#Maximum output current 6.01 A (<= 6 V)
#3.01 A (> 6 V)

import time
import pyvisa
from .PSU import PSU

class NGL202(PSU):
	def __init__(self, rm, instr):
		super().__init__(rm, instr)
		# print("PSU")

	def check_limits(volt):
		if (volt >= 0 and volt <= 6.01):
			return True
		return False