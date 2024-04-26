
import time
import pyvisa

class Instrument:
	def __init__(self, rm, instr):
		self.rm = rm
		self.instr = instr
		self.ress = self.rm.open_resource(self.instr)
		# print("Instrument")

	def check(self, role, name, port):
		rep = self.ress.query("*IDN?")
		rep = rep.strip()
		print(rep)
		if (rep == name):
			print("The " + role + " is connected on the port " + port)
		else:
			print("The " + role + " is not connected on the port " + port)
			exit() #abortProcedure()

