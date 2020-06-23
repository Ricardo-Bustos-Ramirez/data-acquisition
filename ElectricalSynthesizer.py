# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:40:47 2020

@author: ri679647
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 12:18:19 2020

@author: ri679647
"""

import sys
import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv
#import types

GLOBAL_TOUT =  100000   # IO time out in milliseconds
MIN_FREQ = 10e6         # Minimum possible frequency 10 MHz
MAX_FREQ = 40e9         # Maximum possible frequency 40 GHz

class ElectricalSynthesizer():
    def __init__(self,Port=None): 
        self.connected = False
        self.bool_sweep = False

        self.parent=self
        self.list_devices()
        self.idn='IDN'
        self.idnMfg = 'XX'
        self.idnModel = 'XX'
        self.idnSerial = 'XX'
        self.idnFwRevision = 'XX'
        
        self.psgFrequency = 'XX'
        self.powerAttenuation = 'XX'
           
    def list_devices(self):
        try:
            self.rm = pyvisa.ResourceManager()
            self.list = self.rm.list_resources()
        except:
            print("Couldn't find resource manager")
                
    def connect(self, device): 
        try:          
            self.handle = self.rm.open_resource(device)

            self.print_message('connected to...')
            self.idn = str(self.handle.query("*IDN?"))
            print(self.idn)
            self.idn = self.idn.split(',')
            self.idnMfg = self.idn[0]                                           # Manufacturer
            self.idnModel = self.idn[1]                                         # Model number
            self.idnSerialNumber = self.idn[2]                                  # Serial number
            self.idnFwRevision = self.idn[3]                                    # Firmware revision
            self.connected = True
#            
#            self.print_message('setting parameters')
#            self.set_params()
            
        except Exception as e:
            self.print_message(e)
            self.print_message(' Couldn\'t connect to: ' + device)
            sys.exit() # From InfiniiVision Script
    
    def reset_psg(self):
        self.handle.write("*RST")
    
    def get_measurement_params(self):
        self.handle.write("DCL")
    
    def set_params(self):
        self.handle.timeout = GLOBAL_TOUT
        ## Clear the instrument bus
        self.handle.clear()

        ## Clear any previously encountered errors
        self.handle.write("*CLS")
    
    def get_psg_frequency(self):
        self.psgFrequency = float(self.handle.query("FREQUENCY:FIXED?"))
        print('Output frequency: ' + str(self.psgFrequency) + ' Hz')
        return self.psgFrequency
    
    def set_psg_frequency(self, psgFrequency):
        if isinstance(psgFrequency, float):
            if psgFrequency >= MIN_FREQ and psgFrequency <= MAX_FREQ:
                self.handle.write("FREQUENCY:FIXED " + str(psgFrequency))
            else:
                print("Set frequency outside of PSG limits.")
        else:
            print("Invalid type for set frequency.")

    def get_psg_output_state(self):
        psgOutputNumState = self.handle.query("OUTPUT?")
        print("PSG output state: " + psgOutputNumState)
        if psgOutputNumState == '0\n':
            self.psgOutputState = 'OFF'
            print('PSG output is OFF.')
        elif psgOutputNumState == '1\n':
            self.psgOutputState = 'ON'
            print('PSG output is ON.')
        else:
            self.psgOutputState = 'XX'
            print('PSG output is an unknown state.')
        return self.psgOutputState
    
    def set_psg_output_state(self, psgState):
        self.handle.write("OUTPUT " + psgState)

    def get_power_attenuation(self):
        self.powerAttenuation = float(self.handle.query("POWER:ATTENUATION?"))
        print('Output attenuation: ' + str(self.powerAttenuation) + ' dB')
        return self.powerAttenuation
    
    def set_power_attenuation(self, powerAttenuation):        
        self.handle.write("POWER:ATTENUATION 10DB")# + powerAttenuation)
    
    def close(self):
        
        self.handle.write("*CLS")
        time.sleep(1)
        try:
            self.rm.close()
        except Exception as e:
            self.print_message(e)
            sys.exit() # From InfiniiVision Script                
        time.sleep(1)
        self.print_message('Connection to ' + self.idnMfg + ': ' + self.idnModel + ' closed')
        
    def send_cmd(self, cmd):
        
        self.handle.write(cmd)
         
        response = self.handle.read_raw()
        return response
    
    def print_message(self, msg):
        if __name__ == "__main__":
            print(msg)
   
    def save_csv(self, fileName):
        try:
            with open(fileName, 'w',newline='') as fileWriter:
                self.csvWriter = csv.writer(fileWriter, delimiter = '\t')
                now_ = datetime.datetime.now()
                timestamp = now_.strftime('%m/%d/%Y %H:%M hrs')
                self.csvWriter.writerow([timestamp])
                self.csvWriter.writerow(["Record length: " + self.get_waveform_sample_points()])
#                self.csvWriter.writerow(["Sample interval: " + self.sensitivity + " (sec)"])
#                self.csvWriter.writerow(["Trigger point: " + self.rbw_wl + " (samples)"])
                self.csvWriter.writerow(["Source: " + self.get_waveform_channel()])
#                self.csvWriter.writerow(["Vertical units: " + self.span_wl])
                self.csvWriter.writerow(["Vertical scale: " + self.get_waveform_vertical_scale()])
#                self.csvWriter.writerow(["Horizontal units: " + self.span_wl])
                self.csvWriter.writerow(["Horizontal scale: " + self.get_waveform_horizontal_scale()])
                self.csvWriter.writerow(["Acquisition mode: " + self.get_waveform_mode()])
#                self.csvWriter.writerow(["Number of averages: " + self.span_wl])
                self.csvWriter.writerow(["Time (s) Waveform (V)"])
                for (x,y) in zip(self.get_waveform_time(), self.get_waveform_volts()):
                    self.csvWriter.writerow(('{0:.12f}'.format(x),'{0:.12f}'.format(y)))
        except Exception as e:
            print(e)
            self.close()
            print("Error while saving " + fileName + " file")

if __name__ == "__main__":
    PSG = ElectricalSynthesizer()
    print(PSG.list)
    PSG.connect('GPIB0::19::INSTR')
    PSG.set_params()
    PSG.reset_psg()
    PSG.get_psg_frequency()
    PSG.set_psg_frequency(11.0125e9)
    PSG.get_psg_frequency()
#    PSG.set_power_attenuation('10DB')
    PSG.get_power_attenuation()
    PSG.get_psg_output_state()

    PSG.close()