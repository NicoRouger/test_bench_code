#!/usr/bin/env python3
#
#  Oscilloscope.py
#
#  Copyright (C) 2023  Author1, Author2, Author3, Author4, Author5
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Class to interface with an oscilloscope using PyVISA.
#
#  Author1:
#  Author2:
#  Author3:
#  Author4:
#  Author5:

import pyvisa
import csv
import matplotlib.pyplot as plt

class Oscilloscope:
    """
    A class to interface with an oscilloscope using PyVISA.
    """
    def __init__(self, scope_address):
        """
        Initialize the oscilloscope object with a given address.

        :param scope_address: The address of the oscilloscope, e.g. 'USB0::0x0699::0x0522::C062816::INSTR'
        """
        self.scope_address = scope_address
        self.rm = pyvisa.ResourceManager()
        self.scope = self.rm.open_resource(self.scope_address)
        self.config_scope()

    def config_scope(self,
                      ch1_scale=0.5,
                      ch1_position=-3.2,
                      horizontal_scale=2e-4,
                      horizontal_position=10,
                      trigger_level=0.5,
                      trigger_slope='RISe',
                      trigger_coupling='NOISErej',
                      trigger_mode='AUTO',
                      data_source='CH1',
                      data_encoding='ASCii',
                      preamble_encoding='ASCii',
                      bytes_per_sample=2):
        """
        Configure the settings of the oscilloscope.

        :param ch1_scale: Scale of channel 1, defaults to 0.5
        :param ch1_position: Position of channel 1, defaults to -3.2
        :param horizontal_scale: Scale of the horizontal axis, defaults to 2e-4
        :param horizontal_position: Position of the horizontal axis, defaults to 10
        :param trigger_level: Level of the trigger, defaults to 0.5
        :param trigger_slope: Slope of the trigger, defaults to 'RISe'
        :param trigger_coupling: Coupling of the trigger, defaults to 'NOISErej'
        :param trigger_mode: Mode of the trigger, defaults to 'AUTO'
        :param data_source: Source of the data, defaults to 'CH1'
        :param data_encoding: Encoding of the data, defaults to 'ASCii'
        :param preamble_encoding: Encoding of the preamble, defaults to 'ASCii'
        :param bytes_per_sample: Number of bytes per sample, defaults to 2
        """
        self.scope.write('*CLS')     # clear the queue
        self.scope.write('CLEAR')
        self.scope.write('MEASUrement:DELETEALL')            # Delete all measurements
        self.scope.write('DISplay:WAVEView1:CH1:STATE ON')   # Enable Ch1
        self.scope.write(f'CH1:SCAle {ch1_scale}')                    # Set ch1 vertical scale to 0.5V/div
        self.scope.write(f'CH1:POSition {ch1_position}')                # Set ch1 vertical position to -3.2 div
        self.scope.write(f'HORizontal:SCAle {horizontal_scale}')            # Set horizontal scale to 200ns/div
        self.scope.write(f'HORizontal:POSition {horizontal_position}')           # Time ref at 10% of the screen
        self.scope.write('TRIGger:A:EDGE:SOUrce CH1')        # Trigger on ch1
        self.scope.write(f'TRIGger:A:LEVel:CH1 {trigger_level}')          # Set trigger level at 1V on ch1
        self.scope.write(f'TRIGger:A:EDGE:SLOpe {trigger_slope}')        # Trigger on rising edge
        self.scope.write(f'TRIGger:A:EDGE:COUPling {trigger_coupling}') # Noise reject coupling mode
        self.scope.write(f'TRIGger:A:MODe {trigger_mode}')              # Trigger mode auto
        self.scope.write(f'DATa:SOUrce {data_source}')                  # Set ch1 as data source
        self.scope.write(f'DATa:ENCdg {data_encoding}')                 # Set data ASCII encoding
        self.scope.write(f'WFMOutpre:ENCdg {preamble_encoding}')            # Preamble encoded in ASCII
        self.scope.write(f'WFMOutpre:BYT_Nr {bytes_per_sample}')               # 2 bytes per sample

    def get_data(self):
        """
        Get the data from the oscilloscope.

        :return: A tuple of two lists, the first list contains the time stamps and the second list contains the corresponding voltage values.
        """
        ymult = float(self.scope.query('WFMOutpre:YMUlt?').strip('\n'))

        yzero = float(self.scope.query('WFMOutpre:YZEro?').strip('\n'))
        xincr = float(self.scope.query('WFMOutpre:XINcr?').strip('\n'))
        ptoff = int(self.scope.query('WFMOutpre:PT_Off?').strip('\n'))
        xoff = ptoff*xincr

        wfm_str = self.scope.query("CURVe?")
        frames = wfm_str.splitlines()[0].split(";")

        data = [int(b)*ymult+yzero for b in frames[0].split(",")]
        time = [i*xincr-xoff for i in range(len(data))]

        return (time, data)

    def save_data_to_csv(self, file_name):
        """
        Save the data from the oscilloscope to a CSV file.

        :param file_name: The name of the CSV file to be created.
        """
        time, data = self.get_data()

        with open(file_name, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Time (s)", "Voltage (V)"])
            csvwriter.writerows(zip(time, data))

    def print_data(self):
        """
        Print the data from the oscilloscope to the console.
        """
        time, data = self.get_data()

        for i in range(len(data)):
            print(f'{time[i]:.4f}, {data[i]:.4f}')

    def plot_data(self):
        """
        Plot the data from the oscilloscope using matplotlib.
        """
        time, data = self.get_data()

        plt.plot(time, data)
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.grid()
        plt.show()

    def send_query(self, query):
        """
        Send a query to the oscilloscope and return the response.

        Args:
            query (str): The query to send to the oscilloscope.

        Returns:
            str: The response from the oscilloscope.
        """
        response = self.oscilloscope.query(query)
        return response

    def __del__(self):
        """
        Close the connection to the oscilloscope when the object is deleted.
        """
        self.scope.close()
