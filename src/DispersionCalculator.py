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
    freqSep: int
        Nominal repetition rate of the EOM comb used to generate mask, currently 30 GHz.
    freqSep: float
        Nominal repetition rate in wavelength at 1550 nm, currently 0.24 nm.
    comblineSpectrum: list
        List containing the spectral values of the peaks of the comb lines of the optical spectrum used to generate mask.
        .. math:: A_{OFC}=[]
    """
    def __init__(self):
        self.wsPhase = []
        self.wsPort = []
        self.header = []
        self.wavelength = []
        self.spectrum = []
        self.freqSep = 10                      # f_rep = 10 GHz
        self.wavelengthSep = 0.08              # Equivalent nm to 10 GHz at 1550 nm
        # Spectrum points for mask
        self.comblineSpectrum = []
        self.comblineWavelength = []
        self.comblineFrequency = []
        self.c0 = 299792458                     # Light speed in m/s
        self.frequencyOffset = 192.682-192.63  # Difference between waveshaper and OSA
        self.frequencyWaveshaper = []
        self.spectrum_waveshaper = []
        self.lenWaveshaperValues = 0
        self.maxWavelength = 0                 # max(self.wavelength)
        self.minWavelength = 0                 # min(self.wavelength)            
        self.lenWavelength = 0                 # len(self.wavelength)
        self.wavelengthSpan = 0                # self.maxWavelength - self.minWavelength
        self.maxSpectrum = 0                   # max(self.spectrum)
        self.minSpectrum = 0                   # min(self.spectrum)            
        self.lenSpectrum = 0                   # len(self.spectrum)
        self.spectrumSpan = 0                  # self.maxSpectrum - self.minSpectrum
    
    def print_mask(self):
        """This method prints the frequency and attenuation array in a Finisar 1000M compatible format.
        
        The method prints the frequency and corresponding spectral output as:
        
            192.637 00.000  0.000   1
            192.647 00.000  0.000   1
            192.657 50.000  0.432   1
            ...
            
        Where the last two values are the spectral phase (usually 0) and output port (usually 1).
        
        Parameters
        ----------
        frequencyWaveshaper: list
            Mask frequency values (in THz).
        spectrum_waveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        for w, x, y, z  in zip(self.frequencyWaveshaper,self.spectrum_waveshaper, self.wsPhase, self.wsPort):
            if abs(x) < 10:
                print("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}".format(w,x,y,z))
            else:
                print("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}".format(w,x,y,z))
   
    def save_mask(self,filePath,fileName):
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
        frequencyWaveshaper: list
            Mask frequency values (in THz).
        spectrum_waveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        fileWriter = open(filePath + '\\' + fileName, 'w')
        for w, x, y, z in zip(self.frequencyWaveshaper, self.spectrum_waveshaper, self.wsPhase, self.wsPort):
            if abs(x) < 10:
                fileWriter.write("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
            else:
                fileWriter.write("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
        fileWriter.close()  
    
    def plot_mask_and_original(self):
        plt.plot(self.wavelength, self.spectrum,'b')
        plt.plot(self.comblineWavelength, self.comblineSpectrum,'ro')
        plt.axis([min(self.wavelength), max(self.wavelength), max([min(self.spectrum),-80]), max(self.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
    
    def plot_waveshaper_mask(self):
        fig, leftAxis = plt.subplots()
        leftAxis.plot(self.frequencyWaveshaper, self.spectrum_waveshaper, 'ro')
        leftAxis.axis([min(self.frequencyWaveshaper), max(self.frequencyWaveshaper), -60, 10])
        leftAxis.set_xlabel('Frequency (THz)')
        leftAxis.set_ylabel('Attenuation (dB)')
        rightAxis = leftAxis.twinx()
        rightAxis.plot(self.frequencyWaveshaper, self.wsPhase, 'bo')
        rightAxis.axis([min(self.frequencyWaveshaper), max(self.frequencyWaveshaper), min(self.wsPhase), max(self.wsPhase)])
        rightAxis.set_xlabel('Frequency (THz)')
        rightAxis.set_ylabel('Spectral phase (rad)')
        plt.show()
    
    def read_csv(self, fileName):
        with open(fileName, 'r') as fileReader:
            self.csvReader = csv.reader(fileReader, delimiter ='\t')
            for row in self.csvReader:
                if(len(row) > 1):
                    self.wavelength.append(float(row[0]))
                    self.spectrum.append(float(row[1]))
                else:
                    self.header.append(row)
            # Define useful constants for mask calculation
            self.maxWavelength  =  max(self.wavelength)
            self.minWavelength  =  min(self.wavelength)            
            self.lenWavelength  =  len(self.wavelength)
            self.wavelengthSpan =  self.maxWavelength - self.minWavelength
            self.maxSpectrum    =  max(self.spectrum)
            self.minSpectrum    =  min(self.spectrum)            
            self.lenSpectrum    =  len(self.spectrum)
            self.spectrumSpan   =  self.maxSpectrum - self.minSpectrum       
            
    def create_mask_array(self):        
        section_wavelength = self.wavelengthSpan/self.wavelengthSep
#        print(section_wavelength)
        index_frep_span = int(self.lenWavelength/section_wavelength)
#        print(index_frep_span)
        spectrum_max_index = self.spectrum.index(self.maxSpectrum)
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
            self.comblineSpectrum.append(max(sub_spectrum))
            max_index = initial_index + i*index_frep_span + sub_spectrum.index(self.comblineSpectrum[i])
            self.comblineWavelength.append(self.wavelength[max_index])
        for x in self.comblineWavelength:
            self.comblineFrequency.append(((self.c0/(x*1e-9))*1e-12)-self.frequencyOffset)
        self.comblineFrequency.sort()
#        print(self.comblineFrequency) 
    
    def create_waveshaper_mask(self):
        """This method creates a flat mask for the spectrum.
        
        This method creates two lists:
        
        1. frequencyWaveshaper: List with frequency values centered at axial mode (stored in frequencyWaveshaper) peaks +/- waveshaper minimum step size.        
        2. spectrum_waveshaper: List with corresponding spectral values that attenuate to create a flat spectral output (using value stored in comblineSpectrum).        
        .. math:: f_{WS}=[f_{0} ,f_{1}, ... , f_{N-1}, f_{N}]        
        .. math:: A_{WS}=[A_{0} ,A_{1}, ... , A_{N-1}, A_{N}]
        """

        for x in self.comblineFrequency:
            self.frequencyWaveshaper.append(x)
        
        self.frequencyWaveshaper.sort()
    #    print(self.frequencyWaveshaper)
        
        for x in self.comblineSpectrum:
            self.spectrum_waveshaper.append(x)
            
#        print(self.spectrum_waveshaper)        
        self.lenWaveshaperValues = len(self.spectrum_waveshaper)

    def create_waveshaper_mask_with_threshold(self, minThreshold = -30.00):
        """This method creates a flat mask for the spectrum with a threshold for minimum values.
        
        This method creates two lists:
        
        1. frequencyWaveshaper: List with frequency values centered at axial mode (stored in frequencyWaveshaper).        
        2. spectrum_waveshaper: List with corresponding spectral values with a threshold limit (using value stored in comblineSpectrum).        
        .. math:: f_{WS}=[f_{0} ,f_{1}, ... , f_{N-1}, f_{N}]        
        .. math:: A_{WS}=[A_{0} ,A_{1}, ... , A_{N-1}, A_{N}]
        """
        # Now we are going to make the mask for the waveshaper

        for x in self.comblineFrequency:
            self.frequencyWaveshaper.append(x)
        
        self.frequencyWaveshaper.sort()
    #    print(frequencyWaveshaper)
        for x in self.comblineSpectrum:
            if x >= minThreshold:
                self.spectrum_waveshaper.append(x)
            else: # If value is below threshold just eliminate it.
                self.spectrum_waveshaper.append(50)
                
#        print(self.spectrum_waveshaper)
        self.set_len_ws_values(len(self.spectrum_waveshaper))
    
    def set_len_ws_values(self, lenWaveshaperValues):
        self.lenWaveshaperValues = lenWaveshaperValues
    
    def get_len_ws_values(self):
        return self.lenWaveshaperValues
    
    def set_waveshaper_spectral_phase(self, wsPhase):
        if len(wsPhase) == self.get_len_ws_values():
            self.wsPhase = wsPhase
    
    def set_waveshaper_port(self, wsPort):
        if len(wsPort) == self.get_len_ws_values():
            self.wsPort = wsPort

if __name__ == "__main__":
    
    dispCalc = DispersionCalculator()

    root = tk.Tk()
    root.withdraw()
    
    fileName = filedialog.askopenfilename()
    
    dispCalc.read_csv(fileName)
    dispCalc.create_mask_array()
    dispCalc.plot_mask_and_original()

    dispCalc.create_waveshaper_mask()
    wsPhase = []
    wsPort = []
    for i in range(dispCalc.get_len_ws_values()):
        wsPhase.append(0.000)
        wsPort.append(1)
    dispCalc.set_waveshaper_spectral_phase(wsPhase)
    dispCalc.set_waveshaper_port(wsPort)
    
    filePath = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python\\DCF-MLL-PIC'
    # Save flat etalon response
    dispCalc.print_mask()
    fileName = 'MLL-PIC-10GHz.wsp'
    dispCalc.save_mask(filePath,fileName)

    dispCalc.plot_waveshaper_mask()