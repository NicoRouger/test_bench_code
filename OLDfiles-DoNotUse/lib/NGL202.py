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

	# def check_limits(volt):
	# 	if (volt >= 0 and volt <= 6.01):
	# 		return True
	# 	return False
	
	def set_channel(self, channel=None):
		self.channel = channel

	def change_channel(self):
		if (self.channel != None):
			# print(f"INST OUT{self.channel}")
			self.ress.write(f"INST OUT{self.channel}")
			# time.sleep(0.1)

	def enable_channel(self):
		if (self.channel != None):
			self.change_channel()
			# print(f"OUTP 1")
			self.ress.write(f"OUTP 1") #1 means ON
	
	def disable_channel(self):
		if (self.channel != None):
			self.change_channel()
			# print(f"OUTP 0")
			self.ress.write(f"OUTP 0") #0 means OFF
		
	def set_voltage(self, volt):
		self.change_channel()
		# print(f"VOLT {volt}")
		voltage = self.ress.write(f"VOLT {volt}")
		# print(voltage)
		
	def set_max_voltage(self, volt):
		self.change_channel()
		voltage = self.ress.write(f"VOLT:ALIM {volt}")

	def set_min_voltage(self, volt):
		self.change_channel()
		voltage = self.ress.write(f"VOLT:ALIM:LOW {volt}")
	
	def set_max_current(self, amps):
		self.change_channel()
		current = self.ress.write(f"CURR:ALIM {amps}")

	def set_min_current(self, amps):
		self.change_channel()
		current = self.ress.write(f"CURR:ALIM:LOW {amps}")

	def set_current(self, amps):
		self.change_channel()
		current = self.ress.write(f"CURR {amps}")
		# print(current)
		pass

	def enable_current_limit(self):
		self.change_channel()
		curr_lim = self.ress.write(f"ALIM 1")

	def disable_current_limit(self):
		self.change_channel()
		curr_lim = self.ress.write(f"ALIM 0")

	def enable_output(self):
		# self.ress.write(f"INST OUT1")
		# out = self.ress.write(f"OUTP 1")
		# self.ress.write(f"INST OUT2")
		# out = self.ress.write(f"OUTP 1")
		# print(f"OUTP:GEN 1")
		out = self.ress.write(f"OUTP:GEN 1")
		self.change_channel()

	def disable_output(self):
		# self.ress.write(f"INST OUT1")
		# out = self.ress.write(f"OUTP 0")
		# self.ress.write(f"INST OUT2")
		# out = self.ress.write(f"OUTP 0")
		# print(f"OUTP:GEN 0")
		out = self.ress.write(f"OUTP:GEN 0")
		self.change_channel()