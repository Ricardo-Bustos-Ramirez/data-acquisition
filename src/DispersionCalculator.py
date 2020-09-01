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
    comblineSpectrumWavelength: list
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
        self.comblineWavelength = []
        self.comblineSpectrumWavelength = []
        self.comblineFrequency = []
        self.comblineSpectrumFrequency = []
        self.comblineSpectralPhase = []
        self.c0 = 299792458                     # Light speed in m/s
        self.frequencyOffset = 192.682-192.63  # Difference between waveshaper and OSA
        self.frequencyWaveshaper = []
        self.wsAttenuation = []
        self.lenWaveshaperValues = 0
        self.maxWavelength = 0                 # max(self.wavelength)
        self.minWavelength = 0                 # min(self.wavelength)            
        self.lenWavelength = 0                 # len(self.wavelength)
        self.wavelengthSpan = 0                # self.maxWavelength - self.minWavelength
        self.maxSpectrum = 0                   # max(self.spectrum)
        self.minSpectrum = 0                   # min(self.spectrum)            
        self.lenSpectrum = 0                   # len(self.spectrum)
        self.spectrumSpan = 0                  # self.maxSpectrum - self.minSpectrum
        self.timeOutput = []
        self.voltageOutput = []
        self.delayPs = []
        self.shgIntensity = []
    
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
        spectrumWaveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        for w, x, y, z  in zip(self.frequencyWaveshaper,self.wsAttenuation, self.wsPhase, self.wsPort):
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
        spectrumWaveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        fileWriter = open(filePath + '\\' + fileName, 'w')
        for w, x, y, z in zip(self.frequencyWaveshaper, self.wsAttenuation, self.wsPhase, self.wsPort):
            if abs(x) < 10:
                fileWriter.write("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
            else:
                fileWriter.write("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}\r".format(w,x,y,z))
        fileWriter.close()  
    
    def plot_mask_and_original(self):
        plt.plot(self.wavelength, self.spectrum,'b')
        plt.plot(self.comblineWavelength, self.comblineSpectrumWavelength,'ro')
        plt.axis([min(self.wavelength), max(self.wavelength), max([min(self.spectrum),-80]), max(self.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
    
    def plot_waveshaper_mask(self):
        fig, leftAxis = plt.subplots()
        leftAxis.plot(self.frequencyWaveshaper, self.wsAttenuation, 'ro')
        leftAxis.axis([min(self.frequencyWaveshaper), max(self.frequencyWaveshaper), -10, 10])
        leftAxis.set_xlabel('Frequency (THz)')
        leftAxis.set_ylabel('Attenuation (dB)')
        rightAxis = leftAxis.twinx()
        rightAxis.plot(self.frequencyWaveshaper, self.wsPhase, 'bo')
        rightAxis.axis([min(self.frequencyWaveshaper), max(self.frequencyWaveshaper), min(self.wsPhase), max(self.wsPhase)])
        rightAxis.set_xlabel('Frequency (THz)')
        rightAxis.set_ylabel('Spectral phase (rad)')
        plt.show()
    
    def plot_spectral_output(self):
        fig, leftAxis = plt.subplots()
        comblineFrequency = self.get_frequency_combline()
        comblineSpectrumFrequency = self.get_spectrum_combline_frequency()
        comblineSpectralPhase = self.get_spectrum_combline_phase()
        leftAxis.plot(comblineFrequency, comblineSpectrumFrequency, 'ro')
        leftAxis.axis([min(comblineFrequency), max(comblineFrequency), min(comblineSpectrumFrequency) - 5, max(comblineSpectrumFrequency) + 5])
        leftAxis.set_xlabel('Frequency (THz)')
        leftAxis.set_ylabel('Spectral output (dB)')
        rightAxis = leftAxis.twinx()
        rightAxis.plot(comblineFrequency, self.wsPhase, 'bo')
        rightAxis.axis([min(comblineFrequency), max(comblineFrequency), min(comblineSpectralPhase) - 0.1 * np.pi, max(comblineSpectralPhase) + 0.1 * np.pi])
        rightAxis.set_xlabel('Frequency (THz)')
        rightAxis.set_ylabel('Spectral phase (rad)')
        plt.show()    

    def plot_autocorrelation_pulse(self):
        plt.plot(self.delayPs, self.shgIntensity,'b')
        plt.axis([min(self.delayPs), max(self.delayPs), min(self.shgIntensity), max(self.shgIntensity)])
        plt.xlabel('Delay (ps)')
        plt.ylabel('SHG intensity (a.u.)')
        plt.show()
    
    def read_csv_optical_spectrum(self, fileName):
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
    
    def get_wavelength_output(self):
        return self.wavelength
    
    def get_spectrum_output(self):
        return self.spectrum

    def read_csv_optical_pulses(self, fileName):
        with open(fileName, 'r') as fileReader:
            self.csvReader = csv.reader(fileReader, delimiter ='\t')
            for row in self.csvReader:
                if(len(row) > 1):
                    self.timeOutput.append(float(row[0]))
                    self.voltageOutput.append(float(row[1]))
                else:
                    self.header.append(row)
    
    def get_time_output(self):
        return self.timeOutput
    
    def get_voltage_output(self):
        return self.voltageOutput
    
    def set_autocorrelation_values(self, timeOutput, voltageOutput):
        # Define useful constants for SHG intensity autocorrelation
        maxVoltageOutput = max(voltageOutput)            
        for timeElement, voltageElement in zip(timeOutput, voltageOutput):
            self.delayPs.append(timeElement * 31.6 * 1e3)
            self.shgIntensity.append(voltageElement/maxVoltageOutput)
    
    def get_delay_ps(self):
        return self.delayPs
    
    def get_shg_intensity(self):
        return self.shgIntensity
            
    def set_optical_spectrum_array(self, wavelengthOutput, spectrumOutput):        
        section_wavelength = self.wavelengthSpan/self.wavelengthSep
#        print(section_wavelength)
        index_frep_span = int(self.lenWavelength/section_wavelength)
#        print(index_frep_span)
        spectrum_max_index = spectrumOutput.index(self.maxSpectrum)
#        print(spectrumOutput[spectrum_max_index])
        if int((spectrum_max_index%index_frep_span)-(index_frep_span/2)) > 0:
            initial_index = int((spectrum_max_index%index_frep_span)-(index_frep_span/2))
        else:
            initial_index = int((spectrum_max_index%index_frep_span)+(index_frep_span/2))
#        print(initial_index)
#        print(wavelengthOutput[initial_index])
        # Make sure is only an even number of comblines
        section_wavelength = int(section_wavelength)
#        print(section_wavelength)
        for i in range(section_wavelength):
#            print(i)
            sub_spectrum = spectrumOutput[initial_index+i*index_frep_span:initial_index+(i+1)*index_frep_span]
            self.comblineSpectrumWavelength.append(max(sub_spectrum))
            max_index = initial_index + i*index_frep_span + sub_spectrum.index(self.comblineSpectrumWavelength[i])
            self.comblineWavelength.append(wavelengthOutput[max_index])
        for x in self.comblineWavelength:
            self.comblineFrequency.append(((self.c0/(x*1e-9))*1e-12)-self.frequencyOffset)
        self.comblineFrequency.reverse()
        comblineTemp = [x for x in self.comblineSpectrumWavelength]
        comblineTemp.reverse()
        self.comblineSpectrumFrequency = comblineTemp
#        print(self.comblineFrequency)
    
    def get_wavelength_combline(self):
        return self.comblineWavelength
    
    def get_frequency_combline(self):
        return self.comblineFrequency
    
    def get_spectrum_combline_wavelength(self):
        return self.comblineSpectrumWavelength

    def get_spectrum_combline_frequency(self):
        return self.comblineSpectrumFrequency
    
    def set_spectrum_combline_phase(self, spectralPhase):
        if len(spectralPhase) == len(self.get_frequency_combline()):
            self.comblineSpectralPhase = spectralPhase
    
    def get_spectrum_combline_phase(self):
        return self.comblineSpectralPhase
    
    def create_waveshaper_mask(self):
        """This method creates a flat mask for the spectrum.
        
        This method creates two lists:
        
        1. frequencyWaveshaper: List with frequency values centered at axial mode (stored in frequencyWaveshaper) peaks +/- waveshaper minimum step size.        
        2. spectrumWaveshaper: List with corresponding spectral values that attenuate to create a flat spectral output (using value stored in comblineSpectrumWavelength).        
        .. math:: f_{WS}=[f_{0} ,f_{1}, ... , f_{N-1}, f_{N}]        
        .. math:: A_{WS}=[A_{0} ,A_{1}, ... , A_{N-1}, A_{N}]
        """

        for x in self.get_frequency_combline():
            self.frequencyWaveshaper.append(x)
            
#        print(self.spectrumWaveshaper)        
        self.lenWaveshaperValues = len(self.frequencyWaveshaper)
    
    def set_len_ws_values(self, lenWaveshaperValues):
        self.lenWaveshaperValues = lenWaveshaperValues
    
    def get_len_ws_values(self):
        return self.lenWaveshaperValues

    def set_waveshaper_attenuation(self, wsAttenuation):
        if len(wsAttenuation) == self.get_len_ws_values():
            self.wsAttenuation = wsAttenuation
    
    def set_waveshaper_attenuation_with_threshold(self, wsAttenuation, minThreshold):
        if len(wsAttenuation) == self.get_len_ws_values():
            for x, y in zip(self.get_spectrum_combline_frequency(), wsAttenuation):
                if x >= minThreshold:
                    self.wsAttenuation.append(y)
                else: # If value is below threshold just eliminate it.
                    self.wsAttenuation.append(50)
    
    def get_waveshaper_attenuation(self):
        return self.wsAttenuation
    
    def set_waveshaper_spectral_phase(self, wsPhase):
        if len(wsPhase) == self.get_len_ws_values():
            self.wsPhase = wsPhase
    
    def get_waveshaper_spectral_phase(self):
        return self.wsPhase
    
    def set_waveshaper_port(self, wsPort):
        if len(wsPort) == self.get_len_ws_values():
            self.wsPort = wsPort
    
    def get_waveshaper_port(self):
        return self.wsPort
    
    def get_autocorrelation_pulse_width(self):
        delayPs = self.get_delay_ps()
        shgIntensity = self.get_shg_intensity()
        i = 0
        while True:            
            if shgIntensity[i] > 0.5:
                pulsewidthValue1 = delayPs[i]
                break
            else:
                i = i + 1
        
        i = len(shgIntensity) - 1
        while True:
            if shgIntensity[i] > 0.5:
                pulsewidthValue2 = delayPs[i]
                break
            else:
                i = i - 1
        return pulsewidthValue2 - pulsewidthValue1
    
    def get_autocorrelation_peak_value(self):
        shgVoltageOutput = self.get_voltage_output()
        return max(shgVoltageOutput)
    

if __name__ == "__main__":
    
    dispCalc = DispersionCalculator()

    root = tk.Tk()
    root.withdraw()
    
    fileName = filedialog.askopenfilename()
    
    dispCalc.read_csv_optical_spectrum(fileName)
    wavelengthOutput = dispCalc.get_wavelength_output()
    spectrumOutput = dispCalc.get_spectrum_output()
    dispCalc.set_optical_spectrum_array(wavelengthOutput, spectrumOutput)
    dispCalc.plot_mask_and_original()
    
    fileName = filedialog.askopenfilename()
    dispCalc.read_csv_optical_pulses(fileName)
    timeOutput = dispCalc.get_time_output()
    voltageOutput = dispCalc.get_voltage_output()
    dispCalc.set_autocorrelation_values(timeOutput, voltageOutput)
    dispCalc.plot_autocorrelation_pulse()
    print("SHG pulse intensity autocorrelation width: " + str(dispCalc.get_autocorrelation_pulse_width()) + " ps")
    print("SHG pulse intensity autocorrelation peak value: " + str(dispCalc.get_autocorrelation_peak_value()) + " V")

    dispCalc.create_waveshaper_mask()
    wsAttenuation = []
    wsPhase = []
    wsPort = []
    for i in range(dispCalc.get_len_ws_values()):
        wsAttenuation.append(0.000)
        wsPhase.append(0.000)
        wsPort.append(1)
    dispCalc.set_waveshaper_attenuation(wsAttenuation)
    dispCalc.set_waveshaper_spectral_phase(wsPhase)
    dispCalc.set_waveshaper_port(wsPort)
    
    filePath = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python\\DCF-MLL-PIC'
    # Save flat etalon response
#    dispCalc.print_mask()
    fileName = 'MLL-PIC-10GHz.wsp'
    dispCalc.save_mask(filePath,fileName)

    dispCalc.plot_waveshaper_mask()
    dispCalc.set_spectrum_combline_phase([-x for x in dispCalc.get_waveshaper_spectral_phase()])
    dispCalc.plot_spectral_output()