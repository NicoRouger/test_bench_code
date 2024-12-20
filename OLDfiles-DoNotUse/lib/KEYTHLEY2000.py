import time
import pyvisa
import string

from .DMM import DMM
#KEITHLEY INSTRUMENTS INC.,MODEL 2000,1053308,A19  /A02
class KEYTHLEY2000(DMM):
    def __init__(self, rm, instr):
        super().__init__(rm, instr)
        self.max_ascii_chars = 12

    def format_text(self, text):
        string = ''.join(c for c in text if ord(c) < 128) #convert to ascii only
        string = string[:self.max_ascii_chars] #12 chars max
        self.user_text = string

    def enableTextMode(self):
        self.ress.write(":DISP:TEXT:STAT 1")

    def displayText(self, text):
        self.format_text(text)
        self.ress.write(f":DISP:TEXT:DATA '{self.user_text}'")
        self.enableTextMode()

    def animareLR(self):
        x = 0
        offset = ''
        for x in range(0, self.max_ascii_chars - len(self.user_text), 1):
            offset = x * " "
            str = f"{offset}{self.user_text}"[:self.max_ascii_chars]
            print(f">{str}<")
            self.ress.write(f":DISP:TEXT:DATA '{str}'")
            time.sleep(0.5)

    def animateRL(self):
        offset = ''
        for x in range(self.max_ascii_chars - len(self.user_text), 0, -1):
            offset = x * " "
            str = f"{offset}{self.user_text}"[:self.max_ascii_chars]
            print(f">{str}<")
            self.ress.write(f":DISP:TEXT:DATA '{str}'")
            time.sleep(0.5)

    def animateText(self, text):
        self.format_text(text)
        while(1):
            self.animareLR()
            self.animateRL()
        # print(self.ress.query("DISP:WIND:TEXT:DATA?"))

    def refrestScreen(self):
        self.current_screen = self.ress.query(f"DISP:TEXT:DATA?")

    def getScreenData(self):
        return self.current_screen

    def configTemp(self, unit="C", type="K", rsel="SIM", rjunc=23):
        "CONF:TEMP"
        unit_list = ["C", "K", "F"]
        type_list = ["J", "T", "K"]
        junc_list = ["SIM", "CH1"]

        if (unit not in unit_list):
            print(f"unit {unit} is not allowed")
            print(*unit_list, sep = ", ")
            return
        if (type not in type_list):
            print(f"type {type} is not allowed")
            print(*type_list, sep = ", ")
            return
        if (rsel not in junc_list):
            print(f"junc {rsel} is not allowed")
            print(*junc_list, sep = ", ")
            return
        if (rjunc < 0 or rjunc > 50):
            print("rjunc must be between 0 and 50")
            return

        self.ress.write(f":UNIT:TEMP {unit}") #C
        self.ress.write(f":SENSE:TEMP:TC:TYPE {type}") #K
        self.ress.write(f":SENS:TEMP:TC:RJUN:RSEL {rsel}") #SIM
        self.ress.write(f":SENS:TEMP:TC:RJUN:SIM {rjunc}") #23
        print(f"temp configured {unit}, {type}, {rsel}, {rjunc}")

    def getTemp(self):
        temp = self.ress.query("MEAS:TEMP?") #query ?

        # print(temp)
        return temp
                