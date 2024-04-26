import time
import pyvisa
from .Instrument import Instrument

class PSU(Instrument):
	def __init__(self, rm, instr):
		super().__init__(rm, instr)
		self.channel = None
		# print("PSU")

	def set_channel(self, channel=None):
		self.channel = channel

	def change_channel(self):
		if (self.channel != None):
			self.ress.write(f"INST OUT{self.channel}")


	def set_voltage(self, volt):
		self.change_channel()
		voltage = self.ress.write(f"VOLT {volt}")
		print(voltage)
		pass

	def set_max_voltage(self, volt):
		self.change_channel()
		voltage = self.ress.write(f"VOLT:ALIM {volt}")

	def set_min_voltage(self, volt):
		self.change_channel()
		voltage = self.ress.write(f"VOLT:ALIM:LOW {volt}")
	
	def set_current(self, amps):
		self.change_channel()
		current = self.ress.write(f"SOUR:CURR {amps}")
		print(current)
		pass

	def enable_current_limit(self):
		self.change_channel()
		curr_lim = self.ress.write(f"ALIM 1")

	def disable_current_limit(self):
		self.change_channel()
		curr_lim = self.ress.write(f"ALIM 0")

	def enable_output(self):
		out = self.ress.write(f"OUTP 1")
		# out = self.ress.write(f"OUTP 2")

		