import time
import pyvisa
from .Instrument import Instrument

class DMM(Instrument):
	def __init__(self, rm, instr):
		super().__init__(rm, instr)
		print("DMM")

	def measureVoltage(self):
				"""Measuring the voltage on the DMM"""
				voltage = self.ress.query("MEAS:VOLT:DC?")
				voltage = voltage.strip()
				return float(voltage)

	def measureCurrent(self):
				"""Measuring the current on the DMM"""
				current = self.ress.query("MEAS:CURR:DC?")
				current = current.strip()
				return float(current)

		# def check(self, role, name, port):
		#     rep = self.ress.query("*IDN?")
		#     rep = rep.strip()
		#     if (rep == name):
		#         print("The " + role + " is connected on the port " + port)
		#     else:
		#         print("The " + role + " is not connected on the port " + port)
		#         exit() #abortProcedure()

		# def measureVoltage(self):
		#     """Measuring the voltage on the DMM"""
		#     self.ress.write("MEAS:VOLT:DC?")
		#     voltage = self.ress.read()
		#     voltage = voltage.strip()
		#     return float(voltage)

		# def measureCurrent(self):
		#     """Measuring the current on the DMM"""
		#     self.ress.write("MEAS:CURR:DC?")
		#     current = self.ress.read()
		#     current = current.strip()
		#     return float(current)

