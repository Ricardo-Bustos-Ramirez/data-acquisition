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

GLOBAL_TOUT =  100000 # IO time out in milliseconds

class TDS():
    def __init__(self,Port=None): 
        self.connected = False
        self.bool_sweep = False

        self.parent=self
        self.list_devices()
        self.idn='IDN'
        self.idnMfg = 'XX'
        self.idnModel = 'XX'
        self.idnOscFwVersionNum = 'XX'
        self.idnModFwVersionNum = 'XX'
        
        self.numAvg = '0'
        self.channelBandwidth = ['0','0']                                       # Full bandwidth of oscilloscope
        self.channelCoupling = ['0','0']                                        # For a 2 channel oscilloscope
        self.channelInvert = ['0','0']                                          # Channel inversion
        self.channelPosition = ['0','0']                                        # DC position of channel
        self.channelProbe = ['0','0']                                           # Channel probe
        self.channelScale = ['0','0']                                           # Channel scale
        self.channelVolts = ['0','0']                                           # Channel Volts multiplier
        
        self.waveformChannel = 'XX'
        self.waveformCoupling = 'XX'
        self.waveformVerScale = 'XX'
        self.waveformHorScale = 'XX'
        self.waveformSamplePoints = 'XX'
        self.waveformMode = 'XX'   
        self.timeArray = []
        self.waveformArray = []
            
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
#            self.idn = self.idn.split(',')
#            self.idnMfg = self.idn[0]                                           # Manufacturer
#            self.idnModel = self.idn[1]                                         # Model number
#            self.idnOscFwVersionNum = self.idn[3].split(' ')[1].split(':')[1]   # Oscilloscope firmware version number
#            self.idnModFwVersionNum = self.idn[3].split(' ')[2].split(':')[2]   # Module firmware version number
#            self.idnModType = self.idn[3].split(' ')[2].split(':')[1]           # Module type
#            print(self.idnMfg + '\nModel: ' + self.idnModel, '\nOscilloscope FW: ' + self.idnOscFwVersionNum 
#                  + '\nModel FW: ' + self.idnModFwVersionNum + '\nModule type: ' + self.idnModType)
            self.connected = True
            
            self.print_message('setting parameters')
            self.set_params()
            
        except Exception as e:
            self.print_message(e)
            self.print_message(' Couldn\'t connect to: ' + device)
            sys.exit() # From InfiniiVision Script
    
    def get_measurement_params(self):
        self.handle.write("DCL")
    
    def set_params(self):
        self.handle.timeout = GLOBAL_TOUT
        ## Clear the instrument bus
        self.handle.clear()

        ## Clear any previously encountered errors
        self.handle.write("*CLS")
        self.handle.write("HEADER OFF")
#        print("Initial parameters set.")
    
    def get_number_averages(self):
        self.numAvg = int(self.handle.query("ACQuire:NUMAVg?"))
        return self.numAvg
        
    def set_number_averages(self, numAvg):
        if numAvg == 4 or 16 or 64 or 128:
            self.handle.write("ACQuire:NUMAVg " + str(numAvg))
            print('Number of averages: ' + str(numAvg) + ' set')
        else:
            print('Incorrect number of averages: ' + str(numAvg))
    
    def get_osc_state(self):
        print(self.handle.query("ACQuire:MODE?"))
        oscNumState = self.handle.query("ACQuire:STATE?")
        print('Oscilloscope state: ' + oscNumState)
        if oscNumState == '0\n':
            self.oscState = 'STOP'
        elif  oscNumState == '1\n':
            self.oscState = 'RUN'
        else:
            self.oscState = 'ERROR'
        return self.oscState
    
    def set_osc_state(self, oscState): # RUN or STOP
        if oscState != 0:#'RUN' or 'STOP':
#            self.oscState = oscState
            self.handle.write("ACQuire:STATE " + oscState)      
    
    def get_channel_bandwidth(self, channelNumber):
        if channelNumber == 1 or 2:
            channelBandwidthState = self.handle.query("CH" + str(channelNumber) + ":BANdwidth?")
            print('CH' + str(channelNumber) + ' bandwidth state: ' + channelBandwidthState)
            if channelBandwidthState == 'OFF\n':
                self.channelBandwidth[channelNumber-1] = 'OFF'      # 20 MHz
            elif channelBandwidthState == 'ON\n':
                self.channelBandwidth[channelNumber-1] = 'ON'       # Full oscilloscope bandwidth
            else:
                self.channelBandwidth[channelNumber-1] = '0'
                print('Invalid CH' + str(channelNumber) + ' state: ' + channelBandwidthState)
        else:
            print('Invalid channel number: ' + str(channelNumber))           
    
    def set_channel_bandwidth(self, channelNumber, channelBandwidthState):
        if channelNumber == 1 or 2:
            if channelBandwidthState == 'ON' or 'OFF':
                self.handle.write("CH" + str(channelNumber) + ":BANdwidth " + channelBandwidthState)
            else:
                print('Invalid CH' + str(channelNumber) + ' state: ' + channelBandwidthState)
        else:
            print('Invalid channel number: ' + str(channelNumber))
    
    def get_channel_coupling(self, channelNumber):
        if channelNumber == 1 or 2:
            channelCoupling = self.handle.query("CH" + str(channelNumber) + ":COUPling?")
            print('CH' + str(channelNumber) + ' coupling: ' + channelCoupling)
            if channelCoupling == 'DC\n':
                self.channelBandwidth[channelNumber-1] = 'DC'       # DC coupling
            elif channelCoupling == 'AC\n':
                self.channelBandwidth[channelNumber-1] = 'AC'       # AC coupling
            elif channelCoupling == 'GND\n':
                self.channelBandwidth[channelNumber-1] = 'GND'      # Ground coupling, only a flat ground-level waveform
            else:
                self.channelCoupling[channelNumber-1] = '0'
                print('Invalid CH' + str(channelNumber) + ' coupling: ' + channelCoupling)
        else:
            print('Invalid channel number: ' + str(channelNumber))
        return self.channelBandwidth[channelNumber-1]
    
    def set_channel_coupling(self, channelNumber, channelCoupling):
        if channelNumber == 1 or 2:
            if channelCoupling == 'DC' or 'AC' or 'GND':
                self.handle.write("CH" + str(channelNumber) + ":COUPLing " + channelCoupling)
            else:
                print('Invalid CH' + str(channelNumber) + ' coupling: ' + channelCoupling)
        else:
            print('Invalid channel number: ' + str(channelNumber))

    def get_channel_scale(self, channelNumber):
        if channelNumber == 1 or 2:
            channelPosition = self.handle.query("CH" + str(channelNumber) + ":SCAle?")
#            print('CH' + str(channelNumber) + ' scale: ' + channelPosition + ' V/div')
            self.channelPosition[channelNumber-1] = float(channelPosition)      # DC coupling
        else:
            print('Invalid channel number: ' + str(channelNumber))
        return self.channelPosition[channelNumber-1]
    
    def set_channel_scale(self, channelNumber, channelScale):
        if channelNumber == 1 or 2:
            if isinstance(channelScale, float):
                if abs(channelScale) <= 5 and abs(channelScale) >= 2e-3:            # 2mV/div < x < 5 V/div
                    self.handle.write("CH" + str(channelNumber) + ":SCAle " + str(channelScale))
                else:
                    print('Invalid CH' + str(channelNumber) + ' scale, outside limits: ' + str(channelScale))
            else:
                print('Invalid CH' + str(channelNumber) + ' scale type: ' + str(type(channelScale)))
        else:
            print('Invalid channel number: ' + str(channelNumber))
    
    def get_channel_position(self, channelNumber):
        if channelNumber == 1 or 2:
            channelPosition = self.handle.query("CH" + str(channelNumber) + ":POSITION?")
#            print('CH' + str(channelNumber) + ' position: ' + channelPosition)
            self.channelPosition[channelNumber-1] = float(channelPosition)       # DC coupling
        else:
            print('Invalid channel number: ' + str(channelNumber))
        return self.channelPosition[channelNumber-1]
    
    def set_channel_position(self, channelNumber, channelPosition):
        if channelNumber == 1 or 2:
            if isinstance(channelPosition, float):
                if abs(channelPosition) < abs(self.get_channel_scale(channelNumber)):
                    self.handle.write("CH" + str(channelNumber) + ":POSITION " + str(channelPosition))
                else:
                    print('Invalid CH' + str(channelNumber) + ' position, bigger than scale: ' + str(channelPosition))
            else:
                print('Invalid CH' + str(channelNumber) + ' position type: ' + str(type(channelPosition)))
        else:
            print('Invalid channel number: ' + str(channelNumber))
    
    def get_horizontal_parameters(self):
        horizontalParams = self.handle.query("HORizontal?")
        print(horizontalParams)
    
    def set_time_scale(self,timeScale):
        self.handle.write("HORizontal:DELay:SCAle " + str(timeScale))
    
    def set_waveform_parameters(self, waveformId):
#        print("Waveform ID: " + waveformId)
        waveformId = waveformId.split(",")
        self.waveformChannel = waveformId[0]
        self.waveformCoupling = waveformId[1]
        self.waveformVerScale = waveformId[2]
        self.waveformHorScale = waveformId[3]
        self.waveformSamplePoints = waveformId[4]
        self.waveformMode = waveformId[5]
#        print("Waveform parameters \nSource: " + self.waveformChannel + "\nCoupling: " + self.waveformCoupling +
#              "\nVertical scale: " + self.waveformVerScale + "\nHorizontal scale: " + self.waveformHorScale +
#              "\nSample points: " + self.waveformSamplePoints + "\nAcquisition mode: " + self.waveformMode)
    
    def get_waveform_channel(self):
        if self.waveformChannel != 'XX':
            return self.waveformChannel
        else:
            print('Waveform channel error.')
            return 'XX'

    def get_waveform_coupling(self):
        if self.waveformCoupling != 'XX':
            return self.waveformCoupling
        else:
            print('Waveform coupling error.')
            return 'XX' 
        
    def get_waveform_vertical_scale(self):
        if self.waveformVerScale != 'XX':
            return self.waveformVerScale
        else:
            print('Waveform vertical scale error.')
            return 'XX'

    def get_waveform_horizontal_scale(self):
        if self.waveformHorScale != 'XX':
            return self.waveformHorScale
        else:
            print('Waveform horizontal scale error.')
            return 'XX'

    def get_waveform_sample_points(self):
        if self.waveformSamplePoints != 'XX':
            return self.waveformSamplePoints
        else:
            print('Waveform sample points error.')
            return 'XX'

    def get_waveform_mode(self):
        if self.waveformMode != 'XX':
            return self.waveformMode
        else:
            print('Waveform mode error.')
            return 'XX'
        
    def set_waveform_values(self, waveformAscii, xZero, xIncrement, pointsOffset, yZero, yMultiplier, yOffset):
        waveformAscii = waveformAscii.split(',')
        print(len(waveformAscii))
        waveformTime = []
        waveformVolts = []
        y = 0
        n = 0
        for y in waveformAscii:
            y = int(y)
            waveformTime.append(  xZero + xIncrement  * ( n - pointsOffset) )
            waveformVolts.append( yZero + yMultiplier * ( y - yOffset     ) )            
            n = n + 1
        self.timeArray = np.array(waveformTime)
        self.waveformArray = np.array(waveformVolts)     
    
    def get_waveform_time(self):
        return self.timeArray
    
    def get_waveform_volts(self):
        return self.waveformArray
        
    def acquire_waveform(self):
        self.handle.write("DATA:ENCDG ASCIi")
        print(self.handle.query("DATA:ENCDG?"))
        self.handle.write("DATA:WIDth 2")
        waveformAscii = self.handle.query("CURVE?")
#        print(waveformAscii)
        waveformParameters = self.handle.query("WFMOutPre?")
        print('Waveform parameters: ' + waveformParameters)
        waveformParameters = waveformParameters.split(";")
#        waveformId = waveformParameters[6].replace('"','')  # WFID
#        xIncrement = float(waveformParameters[8])           # XINcr
#        pointsOffset = float(waveformParameters[9])         # PT_Off
#        xZero = float(waveformParameters[10])               # XZERo
#        xUnit = waveformParameters[11].replace('"','')      # XUNit
#        yMultiplier = float(waveformParameters[12])         # YMUlt
#        yZero = float(waveformParameters[13])               # YZEro
#        yOffset = float(waveformParameters[14])             # YOFf
#        yUnit = waveformParameters[15].replace('"','')      # YUNit
##        print("\nXINcr: " + str(xIncrement) + "\nPT_Off: " + str(pointsOffset) + "\nXZEro: " + str(xZero) +
##              "\nXUNit: " + xUnit           + "\nYMUlt: "  + str(yMultiplier)  + "\nYZEro: " + str(yZero) + 
##              "\nYOFf: "  + str(yOffset)    + "\nYUNit: "  + yUnit)
#        waveformAscii = self.handle.query("CURVE?")
#        print(waveformAscii)
#        waveformAscii = self.handle.query("CURVE?")
#        print(waveformAscii)
        self.set_waveform_parameters(waveformId)
        self.set_waveform_values(waveformAscii, xZero, xIncrement, pointsOffset, yZero, yMultiplier, yOffset)
        plt.plot(self.get_waveform_time(), self.get_waveform_volts(), 'b')
    
    def close(self):
        try:
            self.handle.write("*CLS")
        except Exception as e:
            self.print_message(e)
            sys.exit() # From InfiniiVision Script                              
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

    def print_message(self, msg):
        if __name__ == "__main__":
            print(msg)
            
#    def get_measurement_parameters(channelNumber):
#        measurementParameters.append(self.get_)
    
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
    
    def plot_waveform(self):
        """Plot the acquired waveform after function acquire_waveform().
        """
        plt.plot(self.get_waveform_time(),self.get_waveform_volts(),'b')
        plt.axis([min(self.get_waveform_time()),max(self.get_waveform_time()),min(self.get_waveform_volts()),max(self.get_waveform_volts())])
        plt.xlabel('Time (sec)')
        plt.ylabel('Output (V)')
        plt.show()

if __name__ == "__main__":
    TDS = TDS()
    print(TDS.list)
    TDS.connect('GPIB0::4::INSTR')
#    TDS.get_measurement_params()
##    TDS.acquire_waveform()
#    TDS.get_channel_bandwidth(1)
##    TDS.set_channel_coupling(1,'DC\n')
#    TDS.get_channel_coupling(1)
#    TDS.set_osc_state('RUN')
#    TDS.get_osc_state()    
#    TDS.set_channel_position(1,-4.0E0)
#    TDS.get_channel_position(1)
#    TDS.set_channel_scale(1,1E0)
#    TDS.get_channel_scale(1)
#    TDS.get_horizontal_parameters()
#    TDS.set_time_scale(2.0E-6)
#    TDS.get_horizontal_parameters()
    TDS.acquire_waveform()
    TDS.save_csv("H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Test files\\TDS210.csv")
    time.sleep(10)
    TDS.close()
#    DCA.check_channel()
#    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Reference material'
#    fileName  = 'TDStest.txt'
#    DCA.save_waveform(filePath, fileName)
    
#    OSA.single_sweep()
#    time.sleep(1)
#    print('Now')
#    OSA.get_span()
#    OSA.get_rbw()
#    OSA.get_sensitivity()
#    OSA.get_ref_lvl()
#    OSA.grab_spectrum('B')
#    now_ = datetime.datetime.now()
#    timestamp = now_.strftime("%Y-%m-%d_%H-%M")
#    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\CW PDH Laser\\CW Homemade\\THz EOM Comb\\EOM Comb with CW-PDH\\OSA'
#    fileName = 'llCW-FPE-PDH_PM-IM-30.001GHz-10dBm-1.16V_SOA_150mA_HWEDFA_680mW_1000mSMF_100m-HNLF-ND_Att-10mW_WS-AllPass_50-50-2' + '.csv '
##    np.savez(filename, wavelength=OSA.wavelength, waveform=OSA.waveform)
##    OSA.save_csv(filePath + '\\' + fileName)
#    OSA.close()
#    
#    plt.plot(OSA.wavelength,OSA.waveform,'b')
#    plt.axis([min(OSA.wavelength),max(OSA.wavelength),max([min(OSA.waveform),-75]),max(OSA.waveform)])
#    plt.xlabel('Wavelength (nm)')
#    plt.ylabel('Output (dB)')
#    plt.show()