# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:52:45 2019

@author: Ricardo Bustos Ramirez
"""

import matplotlib.pyplot as plt
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog

class DispersionCalculator():
    """This class calculates the mask for harmonic injection locking.
    
    Attributes
    ----------
    wsPhase: int
        Phase values of the waveshaper in radians.
    wsPort: int
        Output port of the waveshaper (usually 1).
    wavelength: list
        List that contains the current wavelength values of the optical spectrum (from OSA) used to generate mask.
        .. math:: \lambda_{opt}=[\lambda_{opt,0},\lambda_{opt,1},...,\lambda_{opt,N-1},\lambda_{opt,N}]
    spectrum: list
        List that contains the current output values of the optical spectrum (from OSA) used to generate mask.
        .. math:: A_{opt}=[A_{opt,0},A_{opt,1},...,A_{opt,N-1},A_{opt,N}]
    freq_sep: int
        Nominal repetition rate of the EOM comb used to generate mask, currently 30 GHz.
    freq_sep: float
        Nominal repetition rate in wavelength at 1550 nm, currently 0.24 nm.
    combline_spectrum: list
        List containing the spectral values of the peaks of the comb lines of the optical spectrum used to generate mask.
        .. math:: A_{OFC}=[]
    """
    def __init__(self):
        self.wsPhase = []
        self.wsPort = []
        self.header = []
        self.wavelength = []
        self.spectrum = []
        self.freq_sep = 10 # 10 GHz
        self.wavelength_sep = 0.08 # Equivalent nm to 10 GHz at 1550 nm
        # Spectrum points for mask
        self.combline_spectrum = []
        self.combline_wavelength = []
        self.combline_frequency = []
        self.c0 = 299792458  # Light speed in m/s
        self.frequency_offset = 192.682-192.63 # Difference between waveshaper and OSA
        self.frequency_waveshaper = []
        self.spectrum_waveshaper = []
        self.max_wavelength = 0#max(self.wavelength)
        self.min_wavelength = 0#min(self.wavelength)            
        self.len_wavelength = 0#len(self.wavelength)
        self.wavelength_span = 0#self.max_wavelength - self.min_wavelength
        self.max_spectrum = 0#max(self.spectrum)
        self.min_spectrum = 0#min(self.spectrum)            
        self.len_spectrum = 0#len(self.spectrum)
        self.spectrum_span = 0#self.max_spectrum - self.min_spectrum
    
    def printMask(self):
        """This method prints the frequency and attenuation array in a Finisar 1000M compatible format.
        
        The method prints the frequency and corresponding spectral output as:
        
            192.637 00.000  0.000   1
            192.647 00.000  0.000   1
            192.657 50.000  0.432   1
            ...
            
        Where the last two values are the spectral phase (usually 0) and output port (usually 1).
        
        Parameters
        ----------
        frequency_waveshaper: list
            Mask frequency values (in THz).
        spectrum_waveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        for w, x, y, z  in zip(self.frequency_waveshaper,self.spectrum_waveshaper, self.wsPhase, self.wsPort):
            if abs(x) < 10:
                print("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}".format(w,x,y,z))
            else:
                print("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}".format(w,x,y,z))
   
    def saveMask(self,filePath,fileName):
        """This method saves in a WSP file the frequency and attenuation array in a Finisar 1000M compatible format.
        
        The method saves a WSP file that contains the frequency and corresponding spectral output as:
        
            192.637 00.000  0.000   1
            192.647 00.000  0.000   1
            192.657 50.000  0.432   1
            ...
            
        Where the last two values are the spectral phase (usually 0) and output port (usually 1).
        
        Parameters
        ----------
        filePath: str
            Path for saving the file.
        fileName: str
            Mask file name.
        frequency_waveshaper: list
            Mask frequency values (in THz).
        spectrum_waveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        fileWriter = open(filePath + '\\' + fileName, 'w')
        for w, x, y, z in zip(self.frequency_waveshaper, self.spectrum_waveshaper, self.wsPhase, self.wsPort):
            if abs(x) < 10:
                fileWriter.write("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
            else:
                fileWriter.write("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
        fileWriter.close()  
    
    def plotMaskAndOriginal(self):
        plt.plot(self.wavelength, self.spectrum,'b')
        plt.plot(self.combline_wavelength, self.combline_spectrum,'ro')
        plt.axis([min(self.wavelength), max(self.wavelength), max([min(self.spectrum),-80]), max(self.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
    
    def read_csv(self, fileName):
        with open(fileName, 'r') as fileReader:
            self.csvReader = csv.reader(fileReader, delimiter ='\t')
            for row in self.csvReader:
                if(len(row) > 1):
#                separated_row = row[0].split(',')
#                my_array = np.asarray(separated_row)
#                self.wavelength.append(float(my_array[0]))
#                self.spectrum.append(float(my_array[-1]))
                    self.wavelength.append(float(row[0]))
                    self.spectrum.append(float(row[1]))
                else:
                    self.header.append(row)
            # Define useful constants for mask calculation
            self.max_wavelength = max(self.wavelength)
            self.min_wavelength = min(self.wavelength)            
            self.len_wavelength = len(self.wavelength)
            self.wavelength_span = self.max_wavelength - self.min_wavelength
            self.max_spectrum = max(self.spectrum)
            self.min_spectrum = min(self.spectrum)            
            self.len_spectrum = len(self.spectrum)
            self.spectrum_span = self.max_spectrum - self.min_spectrum       
            
    def createMaskArray(self):        
        section_wavelength = self.wavelength_span/self.wavelength_sep
#        print(section_wavelength)
        index_frep_span = int(self.len_wavelength/section_wavelength)
#        print(index_frep_span)
        spectrum_max_index = self.spectrum.index(self.max_spectrum)
#        print(self.spectrum[spectrum_max_index])
        if int((spectrum_max_index%index_frep_span)-(index_frep_span/2)) > 0:
            initial_index = int((spectrum_max_index%index_frep_span)-(index_frep_span/2))
        else:
            initial_index = int((spectrum_max_index%index_frep_span)+(index_frep_span/2))
#        print(initial_index)
#        print(self.wavelength[initial_index])
        # Make sure is only an even number of comblines
        section_wavelength = int(section_wavelength)
#        print(section_wavelength)
        for i in range(section_wavelength):
#            print(i)
            sub_spectrum = self.spectrum[initial_index+i*index_frep_span:initial_index+(i+1)*index_frep_span]
            self.combline_spectrum.append(max(sub_spectrum))
            max_index = initial_index + i*index_frep_span + sub_spectrum.index(self.combline_spectrum[i])
            self.combline_wavelength.append(self.wavelength[max_index])
        for x in self.combline_wavelength:
            self.combline_frequency.append(((self.c0/(x*1e-9))*1e-12)-self.frequency_offset)
        self.combline_frequency.sort()
#        print(self.combline_frequency) 
    
    def createWaveshaperMask(self):
        """This method creates a flat mask for the spectrum.
        
        This method creates two lists:
        
        1. frequency_waveshaper: List with frequency values centered at axial mode (stored in frequency_waveshaper) peaks +/- waveshaper minimum step size.        
        2. spectrum_waveshaper: List with corresponding spectral values that attenuate to create a flat spectral output (using value stored in combline_spectrum).        
        .. math:: f_{WS}=[f_{0}-4\Delta_{WS},f_{0}-2\Delta_{WS},f_{0}-\Delta_{WS} ,f_{0}+\Delta_{WS} ,...,f_{N-1}-\Delta_{WS} ,f_{N-1}+\Delta_{WS} ,f_{N}-\Delta_{WS} ,f_{N}+\Delta_{WS} ,f_{N}+2\Delta_{WS},f_{N}+4\Delta_{WS}]        
        .. math:: A_{WS}=[             50 dB,             50 dB,A_{0}-min\{A_{n}\},A_{0}-min\{A_{n}\},...,A_{N-1}-min\{A_{n}\},A_{N-1}-min\{A_{n}\},A_{N}-min\{A_{n}\},A_{N}-min\{A_{n}\},             50 dB,             50 dB]
        """

        for x in self.combline_frequency:
            self.frequency_waveshaper.append(x)
        
        self.frequency_waveshaper.sort()
    #    print(self.frequency_waveshaper)
        
        for x in self.combline_spectrum:
            self.spectrum_waveshaper.append(x)
        print(self.spectrum_waveshaper)

    def createWaveshaperMaskWithThreshold(self, minThreshold = -30.00):
        """This method creates a flat mask for the spectrum with a threshold for minimum values.
        
        This method creates two lists:
        
        1. frequency_waveshaper: List with frequency values centered at axial mode (stored in frequency_waveshaper).        
        2. spectrum_waveshaper: List with corresponding spectral values with a threshold limit (using value stored in combline_spectrum).        
        .. math:: f_{WS}=[f_{0}-4\Delta_{WS},f_{0}-2\Delta_{WS},f_{0}-\Delta_{WS} ,f_{0}+\Delta_{WS} ,...,f_{N-1}-\Delta_{WS} ,f_{N-1}+\Delta_{WS} ,f_{N}-\Delta_{WS} ,f_{N}+\Delta_{WS} ,f_{N}+2\Delta_{WS},f_{N}+4\Delta_{WS}]        
        .. math:: A_{WS}=[             50 dB,             50 dB,A_{0}-min\{A_{n}\},A_{0}-min\{A_{n}\},...,A_{N-1}-min\{A_{n}\},A_{N-1}-min\{A_{n}\},A_{N}-min\{A_{n}\},A_{N}-min\{A_{n}\},             50 dB,             50 dB]
        """
        # Now we are going to make the mask for the waveshaper       
        delta_waveshaper = 0.005    # Delta/2 between points in the waveshaper

        for x in self.combline_frequency:
            self.frequency_waveshaper.append(x)
        
        self.frequency_waveshaper.sort()
    #    print(frequency_waveshaper)
        for x in self.combline_spectrum:
            if x >= minThreshold:
                self.spectrum_waveshaper.append(x)
            else: # If value is below threshold just eliminate it.
                self.spectrum_waveshaper.append(50)
    
    def setWaveshaperSpectralPhase(self):
        # Temporary fix.
        len_optical_spectrum = len(self.frequency_waveshaper)
        for x in range(len_optical_spectrum):
            self.wsPhase.append(0)
    
    def setWaveshaperPort(self):
        # Temporary fix.
        len_optical_spectrum = len(self.frequency_waveshaper)
        for x in range(len_optical_spectrum):
            self.wsPort.append(0)

if __name__ == "__main__":
    
    dispCalc = DispersionCalculator()

    root = tk.Tk()
    root.withdraw()
    
    fileName = filedialog.askopenfilename()
    
    dispCalc.read_csv(fileName)
    dispCalc.createMaskArray()
    dispCalc.plotMaskAndOriginal()

    dispCalc.createWaveshaperMask()
    dispCalc.setWaveshaperSpectralPhase()
    dispCalc.setWaveshaperPort()
    
    filePath = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python\\DCF-MLL-PIC'
    # Save flat etalon response
    dispCalc.printMask()
    fileName = 'MLL-PIC-10GHz.wsp'
    dispCalc.saveMask(filePath,fileName)