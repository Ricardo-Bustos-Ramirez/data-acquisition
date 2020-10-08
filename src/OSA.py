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

import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv

class OSA():
    def __init__(self,Port=None):
        """
        Initialization process of OSA script
        """
        self.connected = False
        self.bool_sweep = False
        
        self.start_wl = '900.00'
        self.stop_wl = '1100.00'
        self.span_wl = '200.00'
        self.rbw_wl = '0.1'
        self.sampling_points = '1001'
        self.range = 'SNHD'
        self.average = '1'
        self.sensitivity = 'None'
        self.reference_lvl = '-00'
        
        self.waveform = np.empty((0,1), dtype=np.float64)
        self.wavelength = np.empty((0,1), dtype=np.float64)
        self.parent=self
        self.list_devices()
#        self.connect()
        
#        self.csv_ctl = csv()
        
#    def OSA_acquireDATA(self, ch='A'):
#        tmp = OSA.ask('LDAT'+ch)
#        time.sleep(0.2)
#        tmp2 = [float(k) for k in tmp.split(',')]
#        waveform = array(tmp2[1:])
#        tmp = OSA.ask('WDAT'+ch)
#        time.sleep(0.2)
#        tmp2 = [float(k) for k in tmp.split(',')]
#        wavelength = array(tmp2[1:])
#        return waveform, wavelength
#
#    def createFilename(self, sMeaningful):
#        timestamp = strftime("%Y-%m-%d_%H-%M-%S_", gmtime())
#        return timestamp + sMeaningful +'.npy'
    
    def list_devices(self):
        try:
            self.rm = pyvisa.ResourceManager()
            self.list = self.rm.list_resources()
        except:
            print("Couldn't find resource manager")
                
    def connect(self, device): 
        try:
#            self.ser=serial.Serial(self.port,self.baud,bytesize=self.bytesize, 
#                                   timeout = self.timeout, stopbits = self.stopbits,
#                                   parity = self.parity, rtscts=self.rtscts)
#            if self.ser.isOpen():
#                self.print_message('Connected to laser ' + self.name + ' on port ' + self.port)
#                self.connected = True
            
            self.handle = self.rm.open_resource(device)

            self.print_message('connected to')
            print(self.handle.query("*IDN?"))
            self.connected = True
            
            self.print_message('setting parameters')
#            self.set_params()
#            self.send_cmd("REN")
#            time.sleep(1)
            
        except Exception as e:
            self.print_message(e)
            self.print_message(' Couldn\'t connect')
            
    def set_params(self):
        if self.connected:
#            self.handle.write('STAWL'+self.start_wl + ', STPWL'+self.stop_wl +
#                              ', RESOLN'+self.resolution + ', AVG'+self.average +
#                              ', SMPL'+ self.sampling_points + ', ' + self.range)

#            self.handle.write()
            pass
                
    def close(self):
        
        self.handle.write("GTL")
        time.sleep(1)
        self.rm.close()
        self.print_message('Connection to OSA closed')
        
    def send_cmd(self, cmd):
        
        self.handle.write(cmd)
         
        response = self.handle.read_raw()
        return response
    
    def cont_sweep(self):

        self.bool_sweep = True
        self.handle.write("RPT")
    
    def single_sweep(self):

        self.bool_sweep = True
        self.handle.write("SGL")
        time.sleep(1)
        response = self.handle.query("SWEEP?")
        while response != "0\r\n":
            time.sleep(1)
            response = self.handle.query("SWEEP?")
#            print(response)
        self.bool_sweep = False

    def grab_spectrum(self, channel = 'A'):
            try:            
                tmp = self.handle.query('LDAT'+channel)
#                print(tmp)
                time.sleep(1)
                tmp2 = [float(k) for k in tmp.split(',')]
                self.waveform = np.array(tmp2[1:])
#                print(self.waveform)
            except ValueError:
                self.close()
                print('Acquisition error with spectrum values\r\n')
            
            try:                
                tmp = self.handle.query('WDAT'+channel)
#                print(tmp)
                time.sleep(1)
                tmp2 = [float(k) for k in tmp.split(',')]
                self.wavelength = np.array(tmp2[1:])
#                print(self.wavelength)
            except ValueError:
                self.close()
                print('Acquisition error with wavelength values\r\n')  
    
    def get_span(self):
        self.span_wl = self.handle.query("SPAN?")
        time.sleep(1)
        self.span_wl = self.span_wl.replace("\r","")
        self.span_wl = self.span_wl.replace("\n","") 
    
    def get_rbw(self):
        self.rbw_wl = self.handle.query("RESLN?")
        time.sleep(1)
        self.rbw_wl = self.rbw_wl.replace("\r","")
        self.rbw_wl = self.rbw_wl.replace("\n","") 

    def get_sensitivity(self):
        sensitivity_num = self.handle.query("SENS?")
        time.sleep(1)
        sensitivity_num = sensitivity_num.replace("\r","")
        sensitivity_num = sensitivity_num.replace("\n","")
        sensitivity_num = int(sensitivity_num)
        sensitivity_lvl = {
                1: 'HIGH1',
                2: 'HIGH2',
                3: 'HIGH3',
                4: 'NORM RANG HOLD',
                5: 'NORM RANG AUTO',
                6: 'MID'
                }
        self.sensitivity = sensitivity_lvl.get(sensitivity_num)
    
    def get_ref_lvl(self):
        self.reference_lvl = self.handle.query("REFL?")
        time.sleep(1)
        self.reference_lvl = self.reference_lvl.replace("\r","")
        self.reference_lvl = self.reference_lvl.replace("\n","")
        
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
                self.csvWriter.writerow(["Reference Level: " + self.reference_lvl + " (dB)"])
                self.csvWriter.writerow(["Sensitivity: " + self.sensitivity])
                self.csvWriter.writerow(["Resolution bandwidth: " + self.rbw_wl + " (nm)"])
                self.csvWriter.writerow(["Span: " + self.span_wl + " (nm)"])
                self.csvWriter.writerow(["Wavelength (nm) Amplitude (dB)"])
                for (x,y) in zip(self.wavelength, self.waveform):
                    self.csvWriter.writerow(('{0:.3f}'.format(x),'{0:.3f}'.format(y)))
        except:
            self.close()
            print("Error while saving " + fileName + " file")

    def plot_waveform(self):
        """Plot the acquired waveform after function grab_spectrum().
        """
        plt.plot(self.wavelength, self.waveform,'b')
        plt.axis([min(self.wavelength),max(self.wavelength),max([min(self.waveform),-90]),max(self.waveform)])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()

if __name__ == "__main__":
    OSA = OSA()
    OSA.connect('GPIB0::27::INSTR')
#    OSA.single_sweep()
    time.sleep(1)
    print('Now')
    OSA.get_span()
    OSA.get_rbw()
    OSA.get_sensitivity()
    OSA.get_ref_lvl()
    OSA.grab_spectrum('B')
    now_ = datetime.datetime.now()
    timestamp = now_.strftime("%Y-%m-%d_%H-%M")
    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\CW PDH Laser\\CW Homemade\\THz EOM Comb\\EOM Comb with CW-PDH\\OSA'
    fileName = 'llCW-FPE-PDH_PM-IM-30.001GHz-10dBm-1.16V_SOA_150mA_HWEDFA_680mW_1000mSMF_100m-HNLF-ND_Att-10mW_WS-AllPass_50-50-2' + '.csv '
#    np.savez(filename, wavelength=OSA.wavelength, waveform=OSA.waveform)
#    OSA.save_csv(filePath + '\\' + fileName)
    OSA.close()
    
    plt.plot(OSA.wavelength,OSA.waveform,'b')
    plt.axis([min(OSA.wavelength),max(OSA.wavelength),max([min(OSA.waveform),-90]),max(OSA.waveform)])
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Output (dB)')
    plt.show()