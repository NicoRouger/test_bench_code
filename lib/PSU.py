import time
import pyvisa
from .Instrument import Instrument

class PSU(Instrument):
	def __init__(self, rm, instr):
		super().__init__(rm, instr)
		self.channel = None
		# print("PSU")
