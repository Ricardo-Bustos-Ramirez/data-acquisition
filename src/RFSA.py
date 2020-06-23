# -*- coding: utf-8 -*-
"""
Created on Sat Jan 26 15:59:17 2019

@author: st452223
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 16:46:27 2018

@author: st452223
"""

import visa
import time
import numpy as np
import datetime
import matplotlib.pyplot as plt
import csv

GLOBAL_TOUT =  100000   # IO time out in milliseconds
START_FREQUENCY = 100   # HP8566B start frequency limit
STOP_FREQUENCY = 22e9   # HP8566B stop frequency limit

switcherFrequencyMultiplier = {
    0: "HZ",    # 1e0 Hz: Hz.
    1: "Kz",    # 1e3 Hz: kHz.
    2: "MZ",    # 1e6 Hz: MHz.
    3: "GZ",    # 1e9 Hz: GHz.
}

switcherFrequencyMultiplierReverse = {
    "HZ": 1e0,    # 1e0 Hz: Hz.
    "KZ": 1e3,    # 1e3 Hz: kHz.
    "MZ": 1e6,    # 1e6 Hz: MHz.
    "GZ": 1e9,    # 1e9 Hz: GHz.
}

class RFSA():
    def __init__(self,Port=None): 
        self.connected = False
        self.bool_sweep = False
        
        # freqs are in MHz
        self.start_freq = 0
        self.stop_freq = 200
        self.center_freq = 100
        self.span        = 200
        self.list_devices()
    
    
    def list_devices(self):
        try:
            self.rm = visa.ResourceManager()
            self.list = self.rm.list_resources()
        except:
            print("couldn't find resource manager")
                
    def connect(self, device): 
        try:
#            self.ser=serial.Serial(self.port,self.baud,bytesize=self.bytesize, 
#                                   timeout = self.timeout, stopbits = self.stopbits,
#                                   parity = self.parity, rtscts=self.rtscts)
#            if self.ser.isOpen():
#                self.print_message('Connected to laser ' + self.name + ' on port ' + self.port)
            self.connected = True
            self.handle = self.rm.open_resource(device)
            self.print_message('Hopefully connected to RFSA')
            print(self.handle)
#            self.handle.write("*CLS")
            self.set_params()
        except Exception as e:
            self.print_message(e)
            self.print_message(' Couldn\'t connect')
            
    def set_params(self):
        if self.connected:
#            self.send_cmd('OUTPUT 718; "*FA%dMZ;"' %(self.start_freq))
#            self.send_cmd('OUTPUT 718; "*FB%dMZ;"' %self.stop_freq)
#            self.handle.write('STAWL'+self.start_wl + ', STPWL'+self.stop_wl +
#                              ', RESOLN'+self.resolution + ', AVG'+self.average +
#                              ', SMPL'+ self.sampling_points + ', ' + self.range)

#            self.handle.write()
            self.handle.timeout = GLOBAL_TOUT
            ## Clear the instrument bus. This command resets the HPIB bus so we have to skip it
#            self.handle.clear() 

            ## Clear any previously encountered errors
            self.handle.write("*CLS")            
            
    def close(self):
        self.rm.close()
        self.print_message('Connection to RFSA closed')
        
    def send_cmd(self, cmd):     
        self.handle.write(cmd)
    
    def convert_number_to_frequency_command(self, frequencyNumber):
        """This method converts a frequency number into a string that the RFSA will recognize.
        
        Parameters
        ----------
        frequencyNumber: float
            Frequency in a numeric format in Hz. e.g. 5.213e9
        
        Returns
        -------
        frequencyCommand: str
            Frequency in a string format compatible with RFSA. e.g. "5.213GZ"
        """
#        print("Frequency number:", frequencyNumber)
        frequencyMultiplierIndex = 0
        while frequencyNumber > 1e3:
            frequencyMultiplierIndex = frequencyMultiplierIndex + 1
            frequencyNumber = frequencyNumber/1e3
        frequencyMultiplier = switcherFrequencyMultiplier.get(frequencyMultiplierIndex, "XX")
        if frequencyMultiplier == "XX":
            print("Invalid frequency multiplier: " + str(frequencyMultiplierIndex))
        frequencyCommand = str(frequencyNumber) + frequencyMultiplier
        print(frequencyCommand)
        return frequencyCommand
    
    def convert_frequency_command_to_number(self, frequencyCommand):
        """This method converts a frequency command from the RFSA into a float number in Hz.
        
        Parameters
        ----------
        frequencyCommand: str
            Frequency in a string format compatible with RFSA. e.g. "5213000000"
        
        Returns
        -------
        frequencyNumber: float
            Frequency in a numeric format in Hz. e.g. 5.213e9

        """
#        print("Frequency command:", frequencyCommand)
        try:
            frequencyNumber = float(frequencyCommand)
        except:
            "Entered frequency command is not compatible with RFSA."    
            frequencyNumber = 100e9
        return frequencyNumber

    
    def set_start_frequency(self, startFrequency):
        """This method sets the start frequency for the RFSA.
        
        This method sets the start frequency from the HP8566B using FA command.
        
        Parameters
        ----------
        startFrequency: float
            Start frequency in Hz.
        """
        if startFrequency >= START_FREQUENCY:
            stopFrequency = self.get_stop_frequency()
            if startFrequency < stopFrequency:
                startFrequencyCommand = self.convert_number_to_frequency_command(startFrequency)
                self.handle.write('FA ' + startFrequencyCommand)
            else:
                print("Start frequency", startFrequency, "Hz, higher than stop frequency", stopFrequency, "Hz.")
        else:
            print("Start frequency", startFrequency, "Hz, outside of RFSA limits.")
    
    def get_start_frequency(self):
        """This method gets the start frequency for the RFSA.
        
        This method gets the start frequency from the HP8566B using FA? command.
        
        Returns
        -------
        startFrequency: float
            Start frequency in Hz.
        """
        startFrequencyCommand = self.handle.query('FA?')
#        print("FA?", startFrequencyCommand)
        self.startFrequency = self.convert_frequency_command_to_number(startFrequencyCommand)
        return self.startFrequency

    def set_stop_frequency(self, stopFrequency):
        """This method sets the stop frequency for the RFSA.
        
        This method sets the stop frequency from the HP8566B using FB command.
        
        Parameters
        ----------
        stopFrequency: float
            Stop frequency in Hz.
        """
        if startFrequency <= STOP_FREQUENCY:
            startFrequency = self.get_start_frequency()
            if stopFrequency > startFrequency:
                stopFrequencyCommand = self.convert_number_to_frequency_command(stopFrequency)
                self.handle.write('FB ' + stopFrequencyCommand)
            else:
                print("Stop frequency", stopFrequency, "Hz, lower than start frequency", startFrequency, "Hz.")
        else:
            print("Stop frequency", stopFrequency, "Hz, outside of RFSA limits.")
    
    def get_stop_frequency(self):
        """This method gets the stop frequency for the RFSA.
        
        This method gets the stop frequency from the HP8566B using FA? command.
        
        Returns
        -------
        startFrequency: float
            Stop frequency in Hz.
        """
        stopFrequencyCommand = self.handle.query('FB?')
#        print("FB?", stopFrequencyCommand)
        self.stopFrequency = self.convert_frequency_command_to_number(stopFrequencyCommand)
        return self.stopFrequency
  
    def get_spectrum(self):
        """This method acquires the waveform stored in trace A and saves it in spectrum and freqs.
        """
        # stop continuous measurements and draw trace A
#        self.send_cmd('IP;LF;')
#        self.send_cmd('OUTPUT 718; "CF%dMZ;SP%dMZ;S2;TS;"' %(self.center_freq, self.span))
#        self.send_cmd('CF98MZ;SP40MZ;S2;TS;')
#        self.send_cmd('S2;TS;')
       # self.send_cmd('OUTPUT 718; "*FA%dMZ;*FB%dMZ;S2;TS;"' %(self.start_freq, self.start_freq))
#        self.send_cmd('OUTPUT 718; "O1;TA"')
#        self.send_cmd('SNGLS')                          # Single sweep
        self.centralFrequency = self.handle.query('CF?')     # Central frequency query
#        frequencySpan = self.handle.query('SP?')        # Span
        self.resolutionBandwidth = self.handle.query('RB?')  # Resolution bandwidth
        self.videoBandwidth = self.handle.query('VB?')       # Video bandwidth
        startFrequency = self.get_start_frequency()     # Obtain trace start frequency
        stopFrequency = self.get_stop_frequency()       # Obtain trace start frequency
        traceA = self.handle.query('TA')                # Query waveform from trace A

#        Testing labels
#        print(type(traceA))
#        print(startFrequency)
#        print(stopFrequency)
#        print("RBW:", self.resolutionBandwidth, "Hz")
#        print("VBW:", self.videoBandwidth, "Hz")
#        print("Central frequency:", self.centralFrequency, "Hz")
        self.spectrum = np.array([float(k) for k in traceA.splitlines()])
        self.freqs    = np.linspace(startFrequency, stopFrequency, len(self.spectrum))

    def save_csv(self, fileName):
        try:
            with open(fileName, 'w',newline='') as fileWriter:
                self.csvWriter = csv.writer(fileWriter, delimiter = '\t')
                now_ = datetime.datetime.now()
                timestamp = now_.strftime('%m/%d/%Y %H:%M hrs')
                self.csvWriter.writerow([timestamp])
#                self.csvWriter.writerow(["Reference Level: " + self.reference_lvl + " (dB)"])
#                self.csvWriter.writerow(["Sensitivity: " + self.sensitivity])
                self.csvWriter.writerow(["Resolution bandwidth: " + self.resolutionBandwidth + " (Hz)"])
                self.csvWriter.writerow(["Video bandwidth: " + self.videoBandwidth + " (Hz)"])
                self.csvWriter.writerow(["Cental frequency: " + self.centralFrequency + " (Hz)"])
#                self.csvWriter.writerow(["Span: " + self.span_wl + " (nm)"])
#                self.csvWriter.writerow(["Wavelength (nm) Amplitude (dB)"])
                for (x,y) in zip(self.freqs, self.spectrum):
                    self.csvWriter.writerow(('{0:.3f}'.format(x),'{0:.3f}'.format(y)))
        except:
            self.close()
            print("Error while saving " + fileName + " file")
        
    def print_message(self, msg):
        if __name__ == "__main__":
            print(msg)

    def plot_waveform(self):
        """Plot the acquired waveform after function get_spectrum().
        """
        frequencyArray = self.freqs
        spectrumArray = self.spectrum
        plt.plot(frequencyArray, spectrumArray,'b')
        plt.axis([min(frequencyArray), max(frequencyArray), min(spectrumArray), max(spectrumArray)])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Output (dB)')
        plt.show()

if __name__ == "__main__":
    RFSA = RFSA()
    print(RFSA.list)
    RFSA.connect('GPIB0::18::INSTR')
    RFSA.get_spectrum()

    print(RFSA.freqs)
    print(RFSA.spectrum)
    RFSA.close()

    RFSA.plot_waveform()
    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Test files'
    fileSubPathRfsa = 'RFSA'
    fileName = 'RFSA_' + 'Test_' + timestamp + '.csv '
    RFSA.save_csv(filePath + '\\' + fileSubPathRfsa + '\\' + fileName)
    

    