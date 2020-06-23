# -*- coding: utf-8 -*-
"""

Created on Mon Mar 30 12:18:19 2020

@author: Ricardo Bustos-Ramirez
"""

import sys
import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv

GLOBAL_TOUT =  100000 # IO time out in milliseconds

switcherWaveformType = {
    1: "RAW",           # One data point in each time bucket w/no interpolation.
    2: "AVERAGE",       # Average of the first n hits in a time bucket, where n is the value in the count portion of the preamble.
    3: "VHISTOGRAM",    # Data is a vertical histogram. Histograms are transferred using the LONGLONG format.
    4: "HHISTOGRAM",    # Data is a horizontal histogram. Histograms are transferred using the LONGLONG format.
    5: "NOT USED",
    6: "INTERPOLATE",   # Last data point in each time bucket is stored, and additional data points between the acquired data points are filled by interpolation.
    7: "NOT USED",
    8: "NOT USED",
    9: "DIGITAL",       # Data consists of digital pod or bus values for each time bucket.
    10: "PDETECT"       # Data consists of two data points in each time bucket: the minimum values and maximum values.
}

switcherWaveformFormat = {
    0: "ASCII",         # ASCII format.
    1: "BYTE",          # BYTE format.
    2: "WORD",          # WORD format.
    3: "LONG",          # LONG format.
    4: "LONGLONG",      # LONGLONG format.
    5: "FLOAT"          # FLOAT format.
}

switcherWaveformCoupling = {
    0: "AC",            # AC coupling.
    1: "DC",            # DC coupling.
    2: "DCFIFTY",       # DC fitfy coupling.
    3: "LFREJECT"       # LF reject coupling.
}

switcherWaveformUnits = {
    0: "UNKNOWN",       # UNKKOWN units.
    1: "V",             # VOLT units.
    2: "s",             # SECOND units.
    3: "CONSTANT",      # CONSTANT units.
    4: "A",             # AMPERE units.
    5: "dB"             # DECIBEL units.
}

class DCA():
    """This class controls the high-speed data communication analyzer (DCA).
    
    The current script controls the DCA for capturing data and saving it to a CSV file.
    
    Typical usage example:
        DCA = DCA()
        print(DCA.list)
        DCA.connect('GPIB0::7::INSTR')
        #    DCA.check_channel()
        filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Reference material'
        fileName  = 'DCAtest.txt'
        #    DCA.save_waveform(filePath, fileName)
        DCA.acquire_waveform()
    
    Attributes:
        connected: boolean
            Connection state of the GPIB controller.
        bool_sweep: boolean
            If this attribute is True, the DCA is sweeping continuously.
        idn: str
            Instrument identifier as a complete string.
        idnMfg: str
            Instrument manufacturer (e.g. Agilent, Tektronix).
        idnModel: str
            Instrument model number.
        idnSn: str
            Instrument serial number.
        idnFw: str
            Instrument firmware version number.
        scopeGeneration: str
            Instrument generation (e.g. IV not X type scope)       
        timeArray: array
            Time vector, x-axis values of a captured trace after DCA.acquire_waveform(). 
        waveformArray: array
            Voltage vector, y-axis values of a captured trace after DCA.acquire_waveform().
            
    """
    def __init__(self,Port=None): 
        self.connected = False
        self.bool_sweep = False
        
#        self.start_wl = '900.00'
#        self.stop_wl = '1100.00'
#        self.span_wl = '200.00'
#        self.rbw_wl = '0.1'
#        self.sampling_points = '1001'
#        self.range = 'SNHD'
#        self.average = '1'
#        self.sensitivity = 'None'
#        self.reference_lvl = '-00'
#        
#        self.waveform = np.empty((0,1), dtype=np.float64)
#        self.wavelength = np.empty((0,1), dtype=np.float64)
        self.parent=self
        self.list_devices()
        self.idn='IDN'
        self.idnMfg = 'XX'
        self.idnModel = 'XX'
        self.idnSn = 'XX'
        self.idnFw = 'XX'
        self.scopeGeneration = 'XX'
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
        
        self.timeArray = []
        self.waveformArray = []
    
    def list_devices(self):
        """This method list the devices in the VISA manager.
        """
        try:
            self.rm = pyvisa.ResourceManager()
            self.list = self.rm.list_resources()
        except:
            print("Couldn't find resource manager")
                
    def connect(self, device):
        """
        Parameters
        ----------
        device: str
            Address of the device (DCA).
        """
        try:
#            self.ser=serial.Serial(self.port,self.baud,bytesize=self.bytesize, 
#                                   timeout = self.timeout, stopbits = self.stopbits,
#                                   parity = self.parity, rtscts=self.rtscts)
#            if self.ser.isOpen():
#                self.print_message('Connected to laser ' + self.name + ' on port ' + self.port)
#                self.connected = True
            
            self.handle = self.rm.open_resource(device)

            self.print_message('connected to...')
            self.idn = str(self.handle.query("*IDN?"))
#            print(self.idn)
            self.idn = self.idn.split(',')
            self.idnMfg = self.idn[0]      # Manufacturer
            self.idnModel = self.idn[1]    # Model number
            self.idnSn = self.idn[2]       # Serial number
            self.idnFw = self.idn[3]       # FW
            print(self.idnMfg + '\nModel: ' + self.idnModel, '\nSerial number: ' + self.idnSn + '\nFW: ' + self.idnFw)
            self.connected = True
            
            self.print_message('setting parameters')
            
            scopeTypeCheck = list(self.idnModel)
            if scopeTypeCheck[3] == "-" or scopeTypeCheck[1] == "9":
                self.scopeGeneration = "IVX"
                print('IVX type scope')
            else:
                self.scopeGeneration = "IVnotX"
                print('IV not X type scope')
            self.set_params()
#            self.send_cmd("REN")
#            time.sleep(1)
            
        except Exception as e:
            self.print_message(e)
            self.print_message(' Couldn\'t connect to ' + device)
            sys.exit() # From InfiniiVision Script
            
    def set_params(self):
        if self.connected:
#            self.handle.write('STAWL'+self.start_wl + ', STPWL'+self.stop_wl +
#                              ', RESOLN'+self.resolution + ', AVG'+self.average +
#                              ', SMPL'+ self.sampling_points + ', ' + self.range)

#            self.handle.write()
            self.handle.timeout = GLOBAL_TOUT
            ## Clear the instrument bus
            self.handle.clear()

            ## Clear any previously encountered errors
            self.handle.write("*CLS")
            self.handle.write("SYSTEM:HEADER OFF")
    
    def check_channel(self):
        self.handle.write(":TIMebase:SCALe 100 NS") # Set timescale to something fast so we do not have to wait too long
        er = str(self.handle.query("SYST:ERR?"))
        self.handle.write(":TIMebase:POSition 0")
        self.handle.write(":TRIGger:MODE EDGE") # Set trigger type to edge
        self.handle.write(":TRIGger:EDGE:SOURce LINE") # Set trigger source to LINE, so there is ANYTHING to trigger on ; triggers gets set below, so ok to leave this alone
        self.handle.query("*OPC?") # 
        self.handle.write(":SINGle") # Do a :SINGle to fill up the memory and check the memory size (this is not a proper synchronization, but will work here)
        time.sleep(.5)
    
    def set_waveform_parameters(self, wvfFormat, wvfCoupling, xDisplayRange, yDisplayRange, xUnits, yUnits, wvfPoints, wvfType, wvfCount):
        """This function sets the waveform parameters captured with the WAVEFORM:PREAMBLE command, to be saved with the waveform.
        ----------
        Parameters
        ----------
        wvfCoupling: int
            Input coupling of the waveform in numeric value
        xDisplayRange: float
            X-axis duration of the waveform, usually in [s]
        yDisplayRange: float
            Y-axis range of the waveform, usually in [V]
        wvfPoints: int
            Number of data points or data pairs contained in the waveform.
        wvfType: int
            Numeric value that describes how the waveform was acquired.
        wvfCount: int
            For average, is the fewest number of hits for all time buckets, for RAW and INTERPOLATE is 0 or 1.
        """
        self.waveformChannel = "CHANNEL 1"
        self.waveformFormat = switcherWaveformFormat.get(wvfFormat, "Invalid waveform format: " + str(wvfFormat))
        self.waveformCoupling = switcherWaveformCoupling.get(wvfCoupling, "Invalid waveform input coupling: " + str(wvfCoupling))
        self.waveformHorScale = xDisplayRange
        self.waveformVerScale = yDisplayRange
        self.waveformXUnits = switcherWaveformUnits.get(xUnits, "Invalid X-Axis unit type: " + str(xUnits))
        self.waveformYUnits = switcherWaveformUnits.get(yUnits, "Invalid Y-Axis unit type: " + str(yUnits))
        self.waveformSamplePoints = wvfPoints
        self.waveformMode = switcherWaveformType.get(wvfType, "Invalid waveform type: " + str(wvfType))
        self.waveformAverageCount = wvfCount
        print("Waveform parameters \nSource: " + self.waveformChannel + "\nCoupling: " + self.waveformCoupling +
              "\nVertical scale: " + str(self.waveformVerScale) + " " + self.waveformYUnits  + 
              "\nHorizontal scale: " + str(self.waveformHorScale) + " " + self.waveformXUnits +
              "\nSample points: " + str(self.waveformSamplePoints) + "\nAcquisition mode: " + self.waveformMode +
              "\nAverage count: " + str(self.waveformAverageCount))

    def set_waveform_values(self, waveformAscii, xOrigin, xIncr, xReference, yOrigin, yIncr, yReference):
        """
        Description
        -----------
        This function sets the waveform parameters captured with the WAVEFORM:PREAMBLE command, to be saved with the waveform.
        ----------
        Parameters
        ----------
        wvfCoupling: int
            Input coupling of the waveform in numeric value
        xDisplayRange: float
            X-axis duration of the waveform, usually in [s]
        yDisplayRange: float
            Y-axis range of the waveform, usually in [V]
        wvfPoints: int
            Number of data points or data pairs contained in the waveform.
        wvfType: int
            Numeric value that describes how the waveform was acquired.
        wvfCount: int
            For average, is the fewest number of hits for all time buckets, for RAW and INTERPOLATE is 0 or 1.
        """
        waveformAscii = waveformAscii.split(',')
        print(len(waveformAscii))
        waveformTime = []
        waveformVolts = []
        y = 0
        n = 0
        for y in waveformAscii:
            y = float(y)
            waveformTime.append(  xOrigin + xIncr * ( n - xReference ) )
            waveformVolts.append( yOrigin + yIncr * ( y - yReference ) )            
            n = n + 1
        self.timeArray = np.array(waveformTime)
        self.waveformArray = np.array(waveformVolts)     
    
    def get_waveform_time(self):
        return self.timeArray
    
    def get_waveform_volts(self):
        return self.waveformArray

    def acquire_waveform(self):
        self.handle.write(":WAVEFORM:FORMAT ASCII:ACQUIRE:AVERAGE ON:ACQUIRE:COUNT 8:ACQUIRE:POINTS  1024:MEAS:CLE:WAVEFORM:SOURCE CHANNEL1:DIGITIZE CHANNEL1")
        time.sleep(1)
        dcaStatus = self.handle.query("*OPC?")
        print("DCA status: " + dcaStatus)
        time.sleep(1)
        waveformParameters = self.handle.query(":WAVEFORM:PREAMBLE?")
        print('Waveform parameters: ' + waveformParameters)
        waveformParameters = waveformParameters.split(",")
        
        wvfFormat = int(waveformParameters[0])              # Waveform format (e.g: 0 - ASCII)
        wvfType = int(waveformParameters[1])                # Waveform type (e.g: 1 - RAW, 2 - AVERAGE)
        wvfPoints = int(waveformParameters[2])              # Number of data points (e.g: 1024)
        wvfCount = int(waveformParameters[3])               # Average count (e.g: 8)
        xIncr = float(waveformParameters[4])                # Duration between data points in X axis (e.g: 9.765625e-10 [s])
        xOrigin = float(waveformParameters[5])              # X-axis value of the first data point (e.g. 2.4e-8 [s])
        xReference = float(waveformParameters[6])           # Data points associated with the X origin (e.g: 0)
        yIncr = float(waveformParameters[7])                # Duration between data points in Y axis (e.g: 8.4e-2 [V])
        yOrigin = float(waveformParameters[8])              # Y-axis value of the first data point (e.g. 9e-12 [V])
        yReference = float(waveformParameters[9])           # Data points associated with the Y origin (e.g: 0)
        wvfCoupling = int(waveformParameters[10])           # Channel coupling (e.g: 0 - AC coupling, 1 - DC coupling, 2 - DC-50 coupling)
        xDisplayRange = float(waveformParameters[11])       # X-axis duration of displayed waveform (e.g. 1e-6 [s])
        xDisplayOrigin = float(waveformParameters[12])      # X-axis value at the edge of the display (e.g. 2.4e-8 [s])
        yDisplayRange = float(waveformParameters[13])       # Y-axis voltage/range of displayed waveform (e.g. 8e-2 [V])
        yDisplayOrigin = float(waveformParameters[14])      # Y-axis value at the center of the display (e.g. 0e0 [V])
        wvfDate = waveformParameters[15].replace('"','')    # String containing the date in the format DD MMM YYYY (e.g. 01 JAN 1997)
        wvfTime = waveformParameters[16].replace('"','')    # String containing the time in the format HH:MM:SS:TT (e.g. 09:54:55:89)
        frameModel = waveformParameters[17].replace('"','') # String contianing the model # and (:) serial # (e.g. 86100C:MY43490127)
        wvfAcqMode = int(waveformParameters[19])            # Acquisition sampling mode of the waveform (e.g. 0 - High resolution)
        wvfCompletion = int(waveformParameters[20])         # Percent of time buckets that are complete for the waveform (e.g. 0 - 100)
        xUnits = int(waveformParameters[21])                # X-axis units (e.g. 2 - SECOND units)
        yUnits = int(waveformParameters[22])                # Y-axis units (e.g. 1 - VOLT units)
        maxBwLimit = float(waveformParameters[23])          # Estimated maximum bandwidth of the source waveform (e.g. 50e9 [Hz])
        minBwLimit = float(waveformParameters[24])          # Estimated minimum bandwidth of the source waveform (e.g. 0 [Hz])
        
        waveformAscii = self.handle.query(":WAVEFORM:DATA?")
        self.set_waveform_parameters(wvfFormat, wvfCoupling, xDisplayRange, yDisplayRange, xUnits, yUnits, wvfPoints, wvfType, wvfCount)
        self.set_waveform_values(waveformAscii, xOrigin, xIncr, xReference, yOrigin, yIncr, yReference)
        plt.plot(self.get_waveform_time(), self.get_waveform_volts(), 'b')
    
        
    def save_waveform(self, filePath, fileName):
        TYPE = "ASCiixy" # "CSV" or "ASCiixy" or "BINary"
        self.handle.write(':SAVE:FILename "' + str(fileName) + '"')
        self.handle.write(":SAVE:WAVeform:FORMat " + str(TYPE))
        
        self.handle.write(":SAVE:WAVeform:LENGth 1000")
        
        print("Now saving waveforms to file.\n")
        
        self.handle.query("*CLS;*OPC?") # Clear all registers before issuing the command to save the data; this is necessary so we can properly determine when the scope is done saving data.
        self.handle.write(':SAVE:WAVeform:STARt "' +  str(filePath) + '\\' + str(fileName) + '"')
        
        ## First definite IOC and IOF criterion:
        IO_COMPLETE_BIT = 13 #  the IOC bit is bit-weigh 13 in the Operation Event Register
        IO_COMPLETE_MASK = 1<< IO_COMPLETE_BIT # << is a left shift; 1<<13 = 8192 = 2 raised to 13;
        IO_COMPLETE = 1 << IO_COMPLETE_BIT
        IO_NOT_COMPLETE = 0
        
        IO_FAIL_BIT = 14 #  the IOC bit is bit-weigh 14 in the Operation Event Register
        IO_FAIL_MASK = 1<< IO_FAIL_BIT # << is a left shift; 1<<14 = 16384 = 2 raised to 14;
        IO_FAIL = 1<< IO_FAIL_BIT
        IO_NOT_FAIL = 0
        
        ## Define IOF and IOC initial states:
        IOC_STATUS = 0
        IOF_STATUS = 0
        
        self.handle.query(":OPER:EVENt?")
        ## Begin checking for IO_Status
        while IOF_STATUS ==  IO_NOT_FAIL and IOC_STATUS == IO_NOT_COMPLETE: # Note there is no time qualification here... it should just eventually be done, or fail... eventually.
            Status = int(self.handle.query(":OPER:EVENt?")) # DO NOT use :OPERation
            IOC_STATUS = Status & IO_COMPLETE_MASK # A bitwise and of Status IO_COMPLETE_MASK
            IOF_STATUS = Status & IO_FAIL_MASK
            if IOF_STATUS == IO_FAIL:
                print("FAILED saving waveforms to USB stick.\n")
                print("Check that a USB stick is inserted and that you can manually save a file to the USB tick.  If not, try a different USB stick.\n")
                print("Aborting script and properly closing scope.\n")
                self.handle.clear() # Clear scope communications interface
                self.handle.close() # Close communications interface to scope
                sys.exit()
            if IOC_STATUS == IO_COMPLETE: # you need to do this last. If you were to remvoe the USB stick whiel it is saving, it will say that the IO operation is both failed and done...
                print("Done saving waveforms to USB stick.\n")
                break # Break out of while loop to avoid the wait time below
            time.sleep(0.1) # Pause 100 ms to prevent excessive queries (probably ok to go faster)
        
        ##############################################################################################################################################################################
        ##############################################################################################################################################################################
        ## Done - cleanup
        ##############################################################################################################################################################################
        ##############################################################################################################################################################################
        
        self.handle.clear() # Clear scope communications interface
        self.handle.close() # Close communications interface to scope
#        
        print("Done.")
                
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
                print(self.waveform)
            except ValueError:
                self.close()
                print('Acquisition error with spectrum values\r\n')
            
            try:                
                tmp = self.handle.query('WDAT'+channel)
#                print(tmp)
                time.sleep(1)
                tmp2 = [float(k) for k in tmp.split(',')]
                self.wavelength = np.array(tmp2[1:])
                print(self.wavelength)
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
#                self.csvWriter.writerow(["Record length: " + self.get_waveform_sample_points()])
##                self.csvWriter.writerow(["Sample interval: " + self.sensitivity + " (sec)"])
##                self.csvWriter.writerow(["Trigger point: " + self.rbw_wl + " (samples)"])
#                self.csvWriter.writerow(["Source: " + self.get_waveform_channel()])
##                self.csvWriter.writerow(["Vertical units: " + self.span_wl])
#                self.csvWriter.writerow(["Vertical scale: " + self.get_waveform_vertical_scale()])
##                self.csvWriter.writerow(["Horizontal units: " + self.span_wl])
#                self.csvWriter.writerow(["Horizontal scale: " + self.get_waveform_horizontal_scale()])
#                self.csvWriter.writerow(["Acquisition mode: " + self.get_waveform_mode()])
##                self.csvWriter.writerow(["Number of averages: " + self.span_wl])
                self.csvWriter.writerow(["Time (s) Waveform (V)"])
                for (x,y) in zip(self.get_waveform_time(), self.get_waveform_volts()):
                    self.csvWriter.writerow(('{0:.12f}'.format(x),'{0:.12f}'.format(y)))
        except:
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
    DCA = DCA()
    print(DCA.list)
    DCA.connect('GPIB0::4::INSTR')
#    DCA.check_channel()
    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Reference material'
    fileName  = 'DCAtest.csv'
#    DCA.save_waveform(filePath, fileName)
    DCA.acquire_waveform()
    DCA.plot_waveformwaveform()
#    DCA.save_csv(filePath + '\\' + fileName)
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