# File MAP:
# -------------------------------------------------
# PART 1: Parameters for COM and SWEEP
# -------------------------------------------------
# -------------------------------------------------
# PART 2: Useful Functions
# -------------------------------------------------
# -------------------------------------------------
# PART 3: Identification of instruments
# -------------------------------------------------
# -------------------------------------------------
# PART 4: Functions for DMM
# -------------------------------------------------
# -------------------------------------------------
# PART 5: Functions for uController Phase Shift
# -------------------------------------------------
# -------------------------------------------------
# PART 6: Functions for HV power supply
# -------------------------------------------------
# -------------------------------------------------
# PART 7: MAIN function
# -------------------------------------------------
# Version avec paramètres centralisés
# Pas d'oscillo
# Modifs balayage tension HV
# 2 multimètres
# --------------------------
# Open Power Tuesday - v1.3
# Dec 17th 2024
# Author: Nicolas ROUGER, Luiz VILLA, Joseph KEMDENG, Pauline KERGUS, Matthieu MASSON, Lorenzo LEIJNEN
#
# Joint effort: LAPLACE + LAAS + Owntech -- thanks to all other contributors!
#
# Edit, cleaning and added functions compared to v1.2
# License: GPL 3.0
#
# -------------------------------------------------
# In this version, the Triggers for oscilloscope and DMMs are:
#   Oscillo: Segmented memory, trig on one channel, timeout of 100 ms
#   DMMs: Each DMM is auto-triggered. Idc and Vdc measurements are out of phase
# -> oscillo and both DMM are not synchronized.
# -> an additional (separate) function is provided to align Idc and Vdc afterwards
# -> (thanks Lorenzo!)
# -------------------------------------------------
#
# PURPOSE:
# Opposition method // control and measure 2 half bridges in opposition method
# for losses measurement.
#
# Supervisor to control:
#   1) microcontroller (Spin board from Owntech)
#   2) Power supply
#   3) Digital Multimeters (DMM)
#   4) Oscilloscope
#
# Test sequence is:
#   1) Config microcontroller and turn ON gate signal
#   2) Start logging DC current and DC voltage at 2xDMMs
#   3) Sweep DC bus Voltage (ramp up)
#   4) Sweep Phase Shift generated by microcontroller (ramp up and down)
#   5) Ramp down DC bus Voltage
#   6) Read Buffer of DMMs
#   7) Plot and export data in .csv with timestamp
#   8) Return to initial state
# -------------------------------------------------
#
# REQUIREMENTS:
# SPIN must be loaded with v1.0.0-rc-power_tuesday branch
# The python files with key functions for SPIN must be copied in the "comm_protocol" folder
#   > The folder is located in the cloned GIT repo. at owntech\lib\USB\comm_protocol
# The DMMs used are SDM3065 from Siglent
# The power supply used is Z650+ from TDK Lambda
# The oscilloscope is SDS2000X+ or SDS2000X HD from Siglent
# -------------------------------------------------

import serial
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, parent_dir)


from comm_protocol.src import find_devices
from comm_protocol.src.Shield_Class import Shield_Device

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import xmlrpc.client as xml
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import cast, Any

import os
from matplotlib import pyplot as plt
import pyvisa as visa
from pyvisa import constants
from pyvisa.resources.serial import SerialInstrument
#from pymeasure.instruments.keithley import Keithley2400, Keithley2600

import math
from datetime import datetime

# -------------------------------------------------
# PART 1: Parameters for COM and SWEEP
# -------------------------------------------------
delay = 0.1 #delay in seconds (100 ms)
delay2 = 0.2 #delay in seconds (200 ms)
delay3 = 0.2 #delay in seconds for cooldown during phase shift sweep

# PWM parameters
DutyPWM = 0.485 # 48.5%   1 <> 100% duty. Must consider the deadtime and freq values for dead time compensation!
frequencyPWM = 100e3 #100 kHz switching frequency
DeadTimePWM = 300 #ns, deadtime
InitialPhaseShiftPWM = 15 #15° initial & final phase shift between Leg1 and Leg2


# Sweep conditions:
VoltageLimit = 100 # MAX DC Voltage
CurrentLimit = 0.3 # MAX DC Current
VoltageWrite = 50 # Voltage ramp DC voltage value
timestep = 0.1 # delay between each DC voltage value during ramp in seconds
voltage_step = 1 # Voltage step during ramp
PhaseInit = 15 # Initial Phase for Phase sweep in °
PhaseFinal = 95 # Final Phase of phase sweep in °
PhaseStep = 10 # Phase step value during sweep in °

# CREATE ONLY A SINGLE RESOURCE MANAGER INSTANCE
rm = visa.ResourceManager()


# Instruments:
# Power Supply
# 'ASRL27::INSTR'
# 'ASRL6::INSTR'
HVpowerSupply = 'ASRL27::INSTR'
#
# DMM for DC Current
#
# SDM3055:
# 'USB0::0xF4EC::0x1206::SDM35HBQ7R1226::INSTR'
#
# SDM3065:
# 
# 'USB0::0xF4EC::0x1203::SDM36HCX800420::INSTR'
# 'USB0::0xF4EC::0x1203::SDM36HCX800421::INSTR'
# DMMforCurrent = 'USB0::0xF4EC::0x1203::SDM36HCX800420::INSTR'
# DMMforVoltage = 'USB0::0xF4EC::0x1203::SDM36HCX800421::INSTR'
DMMforCurrent = 'SDM36HCX800420'
DMMforVoltage = 'SDM36HCX800421'

# DMM for DC Voltage
#
# Oscilloscope
# Oscillo manipe Opposition: 'USB0::0xF4EC::0x1011::SDS2PFFX801302::INSTR'
# SDS_RSC = "USB0::0xF4EC::0x1011::SDS2PEEC6R0224::INSTR" 

# -------------------------------------------------
# PART 2: Useful Functions
# -------------------------------------------------
def ExportResultToCSV(String,TimeInfo):
    f = open('csv-'+TimeInfo+'.csv','w')
    f.write(String) #Give your csv text here.
    ## Python will convert \n to os.linesep
    f.close()


def PlotValues(data):
    x=data.split(",")
    dataFormatted=[float(i) for i in x]
    plt.plot(dataFormatted)
    plt.ylabel('current')
    #plt.show()

# -------------------------------------------------
# PART 3: Identification of instruments
# -------------------------------------------------


# ------------ Identification of instruments
def list_instruments():
    global rm
    # rm = visa.ResourceManager()

    for instrument in rm.list_resources():
        print("'{:s}': ".format(instrument), end=' ')
        try:
            device = rm.open_resource(instrument)
            print(type(device), end=' ')
            print(device.query("*IDN?"), end='\n')
            device.close()  # don't close ResourceManager

        except visa.errors.VisaIOError:
            print('INSTRUMENT ERROR\n')

    # ## rev3 19/11/2024 Close rm !!
    # rm.close()


## rev3 19/11/2024 no longer hard-code DMM addr
def auto_detect_device(name):
    global rm
    # rm = visa.ResourceManager()
    dmm_addr = ''

    for instrument in rm.list_resources():
        if name in instrument:
            dmm_addr = f"{instrument}"

    # rm.close() # Close rm
    return dmm_addr


# -------------------------------------------------
# PART 4: Functions for DMM
# -------------------------------------------------

def openSiglentDMM(name: str, **kwargs: Any) -> visa.resources.usb.USBInstrument:
    """Open a Siglent DMM resource.

     Parameters
     ----------
     name : str
            Multimeter name to identify in visa.ResourceManager() list
    kwargs : Any
            Keyword arguments to be used for visa.open_resource()

     Returns
     -------
     visa.resources.usb.USBInstrument
     """
    device_id = auto_detect_device(name)  # no longer hard-coded address
    print(f"Autodetected DMM: {device_id}")
    global rm
    # rm = visa.ResourceManager()
    dmm = cast(visa.resources.usb.USBInstrument, rm.open_resource(device_id, **kwargs))
    return dmm


# ## rev3 19/11/2024 Send list of command instead of line by line
def SendCmd(dmm, cmd_list: list[str], delay: float = 0):
    """Send a list of commands to Siglent DMM.

     Parameters
     ----------
     dmm : VISA Resource corresponding to the multimeter
     cmd_list : list of string commands
     delay : delay in seconds between each command (default 0)
     """
    print(f'{print(dmm.resource_info.resource_name)} send command :')
    for cmd in cmd_list:
        dmm.write(cmd)
        print(f'\t - {cmd}')
        time.sleep(delay)

       
def GetBuffer(dmm, wait_meas_complete: bool = True) -> list[float]:
    """Read data points in the measurement buffer and clear it.
    Parameters
    ----------
    dmm : VISA Resource corresponding to the multimeter
    wait_meas_complete : boolean, default True
            If true the function waits for the multimeter to return to idle and uses the READ? command
            If false the function uses the R? function that return only data that are in the buffer
    Returns
    -------
    List of data points
    """
    buffer_str = ''
    if wait_meas_complete:
        time.sleep(4)  # 4 second delay to be sure previous measurement is OK
        read_ok = False
        while not read_ok:
            try:
                buffer_str = dmm.query('READ?')  # FETCh? or READ? have to wait for the end of the measurement
                read_ok = True
            except visa.errors.VisaIOError:
                print("Wait for measurement to complete")
    else:
        buffer_str = dmm.query('R?')

    # the returned string starts with: #nxxx where n is the number of digits of the number xxx which
    # represent the total length of the string. We need to remove that
    digits = int(buffer_str[1])
    return [float(e) for e in buffer_str[digits + 2:].strip().split(',')]


def AbortMeasure(dmm):
    dmm.write('ABORt')
    time.sleep(2)


def ConfigForDCVoltageMeasureAndStoreBuffer(dmm, **config):
    """Configures Siglent DMM for DC Voltage measurement.

     Parameters
     ----------
     dmm : VISA Resource corresponding to the multimeter
     config : Any Keywords for measurement configuration. Possible keys are :
        voltage_range, trig_count, trig_source, trig_delay, sample_count, nplc, auto_zero
     """
    cmd_buf = []
    cmd_buf.append(f'CONF:VOLT:DC {config.get("voltage_range", "AUTO")}')
    cmd_buf.append(f'TRIG:COUN {config.get("trig_count", "1")}')
    cmd_buf.append(f'TRIG:SOUR {config.get("trig_source", "IMM")}')
    cmd_buf.append(f'SAMP:COUN {config.get("sample_count", "1")}')
    cmd_buf.append(f'VOLT:DC:NPLC {config.get("nplc", "1")}')
    cmd_buf.append(f'VOLT:DC:AZ {config.get("auto_zero", "OFF")}')

    if 'trig_delay' in config:
        if config.get('trig_delay') is "AUTO":
            cmd_buf.append('TRIG:DEL:AUTO 1')   # auto delay between trigger and each measurement
        else:
            cmd_buf.append(f'TRIG:DEL {config.get("trig_delay"):.4E}')   # delay in seconds
    else:
        cmd_buf.append('TRIG:DEL:AUTO 1')

    SendCmd(dmm, cmd_buf, delay=0.05)


def ConfigForDCMeasure(dmm, measure_type: str = 'VOLT', **config):
    """Configures Siglent DMM for DC Current or Voltage measurement.

     Parameters
     ----------
     dmm : VISA Resource corresponding to the multimeter
     measure_type : voltage or current
     config : Any keywords for measurement configuration. Possible keys are :
        range, trig_count, trig_source, trig_delay, sample_count, nplc, auto_zero

        current range : {200uA|2mA|20mA|200mA|2A|10A|AUTO}，Default: AUTO
        voltage range : {200mV|2V|20V|200V|1000V|AUTO}，Default: AUTO
        nplc (SDM3065X models) :{100|10|1|0.5|0.05|0.005}，Default:10
             (SDM3055X models) :{10|1|0.3}，Default:10
     """
    dmm.write('*RST')  # Reset multimeter

    if measure_type.lower() in ['volt', 'voltage']:
        type = 'VOLTage'
    elif measure_type.lower() in ['curr', 'current']:
        type = 'CURRent'
    else:
        raise ValueError(f"Invalide DMM config : '{measure_type}'")

    cmd_buf = []
    cmd_buf.append(f'CONF:{type}:DC {config.get("range", "AUTO")}')         # Current range
    cmd_buf.append(f'{type}:DC:NPLC {config.get("nplc", "1")}')             # Default NPLC 1
    cmd_buf.append(f'{type}:DC:AZ {config.get("auto_zero", "OFF")}')        # Default auto-zero OFF
    cmd_buf.append(f'TRIG:COUN {config.get("trig_count", "1")}')            # Max trigger before returning to idle
    cmd_buf.append(f'TRIG:SOUR {config.get("trig_source", "IMM")}')         # immediate trigger (after INIT is sent)
    cmd_buf.append(f'SAMP:COUN {config.get("sample_count", "1")}')          # Number of measurement per trigger

    if 'trig_delay' in config:
        if config.get('trig_delay') is "AUTO":
            cmd_buf.append('TRIG:DEL:AUTO 1')   # auto delay between trigger and each measurement
        else:
            cmd_buf.append(f'TRIG:DEL {config.get("trig_delay"):.4E}')   # delay in seconds
    else:
        cmd_buf.append('TRIG:DEL:AUTO 1')

    SendCmd(dmm, cmd_buf, delay=0.05)


def TimeStamp():
    now = datetime.now()
    day = now.strftime("%d_%m_%Y")
    current_time = now.strftime("%H_%M_%S")
    print("Current Time =", current_time,day)
    return current_time+'-'+day


# ## rev3 19/11/2024 common for current & voltage
def StartMeasureAndStoreBufferDC(dmm):
    # Initiate measurement if Trigger immediate is set before
    SendCmd(dmm, ['INITiate'])


def StartLoggingDCvoltage(dmm, **config):
    # Configure DMM for DC voltage
    ConfigForDCVoltageMeasureAndStoreBuffer(dmm, **config)
    StartMeasureAndStoreBufferDC(dmm)  # Measure and Store in buffer


def StartLoggingDCcurrent(dmm, **config):
    # Configure DMM for DC current
    ConfigForDCCurrentMeasureAndStoreBuffer(dmm, **config)
    StartMeasureAndStoreBufferDC(dmm)  # Measure and Store in buffer
  
# ------------------ End functions DMM



# -------------------------------------------------
# PART 5: Functions for uController Phase Shift
# -------------------------------------------------
def SweepPhaseShift(Board,PhaseInit,PhaseFinal,step):
    
    for phase_shift_value in range(PhaseInit, PhaseFinal, step):  # Example values from 0 to 170 with a step of 10
      message1 = Board.sendCommand("PHASE_SHIFT", "LEG2", phase_shift_value)
      print(f"Sent command with phase shift: {phase_shift_value}, message: {message1}")
      # Return to init Phase between each step ?
      #message1 = Board.sendCommand("PHASE_SHIFT", "LEG2", PhaseInit)
      #print(f"Sent command with phase shift: {phase_shift_value}, message: {message1}")
      # Thermal COOLDOWN
      # time.sleep(delay3)

    for phase_shift_value_down in range(PhaseFinal, PhaseInit-step, -step):  # Example values from 0 to 170 with a step of 10
      message1 = Board.sendCommand("PHASE_SHIFT", "LEG2", phase_shift_value_down)
      print(f"Sent command with phase shift: {phase_shift_value_down}, message: {message1}")
      # Return to init Phase between each step ?
      #message1 = Board.sendCommand("PHASE_SHIFT", "LEG2", PhaseInit)
      #print(f"Sent command with phase shift: {phase_shift_value}, message: {message1}")
      # Thermal COOLDOWN
      # time.sleep(delay3)


def repeat_get_line(shield, num_times):
    """
    Calls shield.getLine() and prints the result the specified number of times.

    Args:
        shield: The object that has the getLine() method (e.g., Shield).
        num_times (int): The number of times to call getLine() and print the result.
    """
    for _ in range(num_times):
        message = shield.getLine()
        print(message)

# Example usage:
# repeat_get_line(Shield, 5)  # Calls Shield.getLine() 5 times and prints each message








# -------------------------------------------------
# PART 6: Functions for HV power supply
# -------------------------------------------------
    
def OutputChange(smu,State):
    cmd1 = 'OUTPut:STATe '+State
    smu.write(cmd1)
    time.sleep(delay)
    

def VoltageShutDown(source,voltage,VoltageLimit):
    if float(voltage) >= VoltageLimit:
        OutputChange(source,'OFF')
    time.sleep(delay)
    
def CurrentShutDown(source,current,CurrentLimit):
    if float(current) >= CurrentLimit:
        OutputChange(source,'OFF')
    time.sleep(delay)

def VoltageRampUp(source,voltage,delay,step_value,start_value = 0):
    cmd1 = 'VOLTage:MODE FIX'
    source.write(cmd1)
    z = np.arange(start_value,voltage+step_value,step_value)
    for x in z:
        cmd2 = 'VOLTage:LEV '+str(x)
        source.write(cmd2)
        time.sleep(delay)
    time.sleep(delay)

def VoltageRampUpAndSweepPhase(source,voltage,delay,step_value,Board,PhaseInit,PhaseFinal,step,start_value = 0):
    cmd1 = 'VOLTage:MODE FIX'
    source.write(cmd1)
    z = np.arange(start_value,voltage+step_value,step_value)
    for x in z:
        cmd2 = 'VOLTage:LEV '+str(x)
        source.write(cmd2)
        time.sleep(delay)
    time.sleep(delay)
    SweepPhaseShift(Board,PhaseInit,PhaseFinal,step) # SWEEP PHASE SHIFT of microcontroller
    
def VoltageRampDown(source,voltage,delay,step_value,end_value):
    cmd1 = 'VOLTage:MODE FIX'
    source.write(cmd1)
    z = np.arange(voltage, end_value, step_value)
    for x in z:
        cmd2 = 'VOLTage:LEV '+str(x)
        source.write(cmd2)
        time.sleep(delay)
    time.sleep(delay)
    
def CheckVoltage(source):
    cmd1 = 'MEASure:VOLTage?'
    result = str(source.query(cmd1))
    return(result)
    time.sleep(delay)

def CheckCurrent(source):
    cmd1 = 'MEASure:CURRent?'
    result = str(source.query(cmd1))
    return(result)
    time.sleep(delay)
    

def DCSweepVoltageSource():
    global rm
    #print(args)

    #Shield_ports = find_devices.find_shield_device_ports(shield_vid, shield_pid)
    #print(Shield_ports)
    #Shield = Shield_Device(shield_port= Shield_ports[0], shield_type='TWIST')

    #TDK Lambda #1 in USB
    TDKLambda = rm.open_resource(HVpowerSupply, query_delay=0.5)
    #TDKLambda = rm.open_resource('ASRL27::INSTR', query_delay=0.5)
    #TDKLambda = rm.open_resource('ASRL6::INSTR', query_delay=0.5)
    TDKLambda.write('INSTrument:NSELect 1') # MANDATORY, at least once: Select ADDRESS prior to other functions
    TDKLambda.write('VOLTage:LEV 0')
    time.sleep(delay)
    OutputChange(TDKLambda,'ON')
    time.sleep(delay)
    #VoltageRampUp(TDKLambda,VoltageWrite,timestep)
    VoltageRampUpAndSweepPhase(TDKLambda,VoltageWrite,timestep,voltage_step,Shield,PhaseInit,PhaseFinal,PhaseStep)
    time.sleep(delay)
    voltageRead = CheckVoltage(TDKLambda)
    time.sleep(delay)
    currentRead = CheckCurrent(TDKLambda)
    time.sleep(delay)
    print(voltageRead)
    print(currentRead)
    VoltageShutDown(TDKLambda,voltageRead,VoltageLimit)
    time.sleep(delay)
    # CurrentShutDown(TDKLambda,currentRead,CurrentLimit)
    time.sleep(delay)
    VoltageRampDown(TDKLambda,VoltageWrite,timestep,-voltage_step,-voltage_step)
    time.sleep(delay)
    TDKLambda.write('VOLTage:LEV 0') # Just to be sure: Voltage 0V
    time.sleep(delay)
    OutputChange(TDKLambda, 'OFF')
    time.sleep(delay)
    TDKLambda.close()   # Close DMM resource session (ResourceManager is still alive !)
    time.sleep(delay)
   
    #rm.visalib._registry.clear()

# -------------------End Functions Power Supply    




 


# -------------------------------------------------
# PART 7: MAIN function
# -------------------------------------------------

def main():
    leg_to_test = "LEG1"                               #leg to be tested in this script
    reference_names = ["V1","V2","VH","I1","I2","IH"]  #names of the sensors of the board

    shield_vid = 0x2fe3
    shield_pid = 0x0101

    Shield_ports = find_devices.find_shield_device_ports(shield_vid, shield_pid)
    print(Shield_ports)

    Shield = Shield_Device(shield_port=Shield_ports[0], shield_type='TWIST')

    try:

      # ---------------HARDWARE IN THE LOOP PV EMULATOR CODE ------------------------------------
    ##  message1 = Shield.sendCommand("IDLE")
    ##  print(message1)
    ##
    ##  message = Shield.sendCommand( "BUCK", "LEG1", "OFF")
    ##  print(message)
    ##
    ##  message = Shield.sendCommand( "BUCK", "LEG2", "OFF")
    ##  print(message)

        message = Shield.sendCommand("LEG","LEG1","ON")
        print(message)

        message = Shield.sendCommand("LEG","LEG2","ON")
        print(message)

        message = Shield.sendCommand("POWER_ON")
        print(message)

        message = Shield.sendCommand("DUTY","LEG1",DutyPWM) # Initial duty cycle is 48.5%, to compensate dead time
        print(message)

        message = Shield.sendCommand("DUTY","LEG2",DutyPWM) # Initial duty cycle is 48.5%, to compensate dead time
        print(message)

    ##  for dead_time_value in range(100, 300, 50):
    ##      message1 = Shield.sendCommand("DEAD_TIME_RISING", "LEG1", dead_time_value)
    ##      message1 = Shield.sendCommand("DEAD_TIME_FALLING", "LEG1", dead_time_value)
    ##      message1 = Shield.sendCommand("DEAD_TIME_RISING", "LEG2", dead_time_value)
    ##      message1 = Shield.sendCommand("DEAD_TIME_FALLING", "LEG2", dead_time_value)
    ##      print(f"Sent command with phase shift: {dead_time_value}, message: {message1}")

    ##
    ##  for frequency_value in range(50000, 150000, 10000):  # Example values from 0 to 170 with a step of 10
    ##      message1 = Shield.sendCommand("FREQUENCY", "LEG1", frequency_value)
    ##      print(f"Sent command with frequency: {frequency_value}, message: {message1}")

        message1 = Shield.sendCommand("FREQUENCY", "LEG1", frequencyPWM) # 100 kHz switching freq


        message = Shield.sendCommand("DEAD_TIME_RISING","LEG2",DeadTimePWM) # 300 ns deadtime
        message = Shield.sendCommand("DEAD_TIME_RISING","LEG1",DeadTimePWM) # 300 ns deadtime
        print(message)

        message = Shield.sendCommand("DEAD_TIME_FALLING","LEG2",DeadTimePWM) # 300 ns deadtime
        message = Shield.sendCommand("DEAD_TIME_FALLING","LEG1",DeadTimePWM) # 300 ns deadtime
        print(message)


        message1 = Shield.sendCommand("PHASE_SHIFT","LEG2",InitialPhaseShiftPWM) # Initial phase shift is 15°
        print(message1)

        # ------------------------------------------
        # MAIN Test sequence
        #
        # START LOGGING
        #list_instruments()
        # DMM3065_current = auto_detect_device(DMMforCurrent)
        # DMM3065_voltage = auto_detect_device(DMMforVoltage)
        DMM3065_current = openSiglentDMM(DMMforCurrent)  # !!! CONFIGURE UNIQUE IDs BEFORE RUN
        DMM3065_voltage = openSiglentDMM(DMMforVoltage)

        # configure current and voltage DMM with external trigger
        # maximum 20 measured points, 150us delay before measurement
        # and NPLC = 1 (20ms)
        ConfigForDCMeasure(DMM3065_current, measure_type='current', range=0.2, trig_source='EXT',
                           trig_count=20, trig_delay=150e-6, nplc=1, sample_count=5)
        ConfigForDCMeasure(DMM3065_voltage,  measure_type='voltage', range=60, trig_source='EXT',
                           trig_count=20, trig_delay=150e-6, nplc=1, sample_count=5)

        DMM3065_current.write('INITiate')
        DMM3065_voltage.write('INITiate')

        tmarkDMM = TimeStamp()
        #time.sleep(1)

        # Start DC Voltage SWEEP
        DCSweepVoltageSource()

        # Return to init Phase
        message1 = Shield.sendCommand("PHASE_SHIFT", "LEG2", InitialPhaseShiftPWM)
        print(message1)

        #Turn OFF PWM signals
        message = Shield.sendCommand( "LEG", "LEG1", "OFF")
        print(message)
        ##
        message = Shield.sendCommand( "LEG", "LEG2", "OFF")
        print(message)

        # READ BUFFER
        voltage = GetBuffer(DMM3065_voltage, wait_meas_complete=False)
        current = GetBuffer(DMM3065_current, wait_meas_complete=False)

        # SAVE in CSV
        ExportResultToCSV(voltage, tmarkDMM+'Voltage')
        ExportResultToCSV(current, tmarkDMM+'Current')

        # PLOT
        plt.figure(0)
        plt.plot(voltage, marker='o', linestyle='none')

        plt.figure(1)
        plt.plot(current, marker='o', linestyle='none')

        power = [u*i for u, i in zip(voltage, current)]
        plt.figure(1)
        plt.plot(current, marker='o', linestyle='none')
        plt.show()



    ##  for phase_shift_value in range(0, 170, 10):  # Example values from 0 to 170 with a step of 10
    ##      message1 = Shield.sendCommand("PHASE_SHIFT", "LEG2", phase_shift_value)
    ##      print(f"Sent command with phase shift: {phase_shift_value}, message: {message1}")
    ##
    ##  for phase_shift_value_down in range(160, 0, -10):  # Example values from 0 to 170 with a step of 10
    ##      message1 = Shield.sendCommand("PHASE_SHIFT", "LEG2", phase_shift_value_down)
    ##      print(f"Sent command with phase shift: {phase_shift_value}, message: {message1}")


    ##  repeat_get_line(Shield, 80)  # Calls Shield.getLine() 5 times and prints each message

    # ------------------------------------------
    # Return to Init PHASE and final state
    #
    finally:
      #message1 = Shield.sendCommand("PHASE_SHIFT","LEG2",InitialPhaseShiftPWM)
      #print(message1)
        if 'DMM3065_current' in globals():
            DMM3065_current.close()  # Close DMM resource session (ResourceManager is still alive !)
            print('Close DMM current')
        if 'DMM3065_voltage' in globals():
            DMM3065_voltage.close()  # Close DMM resource session (ResourceManager is still alive !)
            print('Close DMM current')

        rm.close()
        print('Job Done!')


if __name__ == "__main__":
    main()
    # list_instruments()
    # dmm = openSiglentDMM('SDM35HBD7R1671', query_delay=0.01)
    # print(dmm.resource_info.resource_name)
    # dmm.write('*RST')
    # dmm.write('INITiate')