# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 15:52:45 2019

@author: Ricardo Bustos Ramirez
"""

import matplotlib.pyplot as plt
from scipy import integrate
import csv
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog
import os

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
        spectralOutputFrequency = [x for x in self.spectrum]
        spectralOutputFrequency.reverse()
        frequencyTHz = [((self.c0/(x*1e-9))*1e-12)-self.frequencyOffset for x in self.wavelength]
        frequencyTHz.reverse()
        leftAxis.plot(comblineFrequency, comblineSpectrumFrequency, 'ro')
        leftAxis.plot(frequencyTHz, spectralOutputFrequency, 'r')
        leftAxis.axis([min(comblineFrequency), max(comblineFrequency), min(comblineSpectrumFrequency) - 5, max(comblineSpectrumFrequency) + 5])
        leftAxis.set_xlabel('Frequency (THz)')
        leftAxis.set_ylabel('Spectral output (dB)')
        rightAxis = leftAxis.twinx()
        rightAxis.plot(comblineFrequency, comblineSpectralPhase, 'bo')
        rightAxis.axis([min(comblineFrequency), max(comblineFrequency), min(comblineSpectralPhase) - np.pi, max(comblineSpectralPhase) + np.pi])
        rightAxis.set_xlabel('Frequency (THz)')
        rightAxis.set_ylabel('Spectral phase (rad)')
        plt.show()
        return (frequencyTHz, spectralOutputFrequency, comblineFrequency, comblineSpectrumFrequency, comblineSpectralPhase)

    def plot_autocorrelation_pulse(self):
        plt.plot(self.delayPs, self.shgIntensity,'b')
        plt.axis([min(self.delayPs), max(self.delayPs), min(self.shgIntensity), max(self.shgIntensity)])
        plt.xlabel('Delay (ps)')
        plt.ylabel('SHG intensity (a.u.)')
        plt.show()
    
    def plot_autocorrelation_values(self, acDispersionArray, acPulseWidthArray, acPulsePeakArray):
        fig, leftAxis = plt.subplots()
        leftAxis.plot(acDispersionArray, acPulseWidthArray, 'r')
        leftAxis.axis([min(acDispersionArray), max(acDispersionArray), min(acPulseWidthArray), max(acPulseWidthArray)])
        leftAxis.set_xlabel('Dispersion (ps/nm)')
        leftAxis.set_ylabel('AC pulse width (ps)')
        rightAxis = leftAxis.twinx()
        rightAxis.plot(acDispersionArray, acPulsePeakArray, 'b')
        rightAxis.axis([min(acDispersionArray), max(acDispersionArray), min(acPulsePeakArray)-0.1, max(acPulsePeakArray)+0.1])
        rightAxis.set_xlabel('Dispersion (ps/nm)')
        rightAxis.set_ylabel('AC pulse peak (V)')
        plt.show()        
    
    def read_csv_optical_spectrum(self, fileName):
        self.wavelength = []
        self.spectrum = []
        self.header = []
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
        self.timeOutput = []
        self.voltageOutput = []
        self.header = []
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
        self.delayPs = []
        self.shgIntensity = []
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
        self.comblineWavelength = []
        self.comblineSpectrumWavelength = []
        self.comblineFrequency = []
        self.comblineSpectrumFrequency = []
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
        self.frequencyWaveshaper = []
        
        for x in self.get_frequency_combline():
            self.frequencyWaveshaper.append(x)
            
#        print(self.spectrumWaveshaper)        
        self.lenWaveshaperValues = len(self.frequencyWaveshaper)
    
    def get_waveshaper_frequency(self):
        return self.frequencyWaveshaper
    
    def set_len_ws_values(self, lenWaveshaperValues):
        self.lenWaveshaperValues = lenWaveshaperValues
    
    def get_len_ws_values(self):
        return self.lenWaveshaperValues

    def set_waveshaper_attenuation(self, wsAttenuation):
        if len(wsAttenuation) == self.get_len_ws_values():
            self.wsAttenuation = wsAttenuation
    
    def set_waveshaper_attenuation_with_threshold(self, wsAttenuation, minThreshold):
        self.wsAttenuation = []
        
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
    
    def get_optical_spectrum_bandwidth_and_tlp(self):
        wavelength = self.get_wavelength_combline()
        comblineWavelength = self.get_spectrum_combline_wavelength()
        linearCombline = [math.pow(10, x/10) for x in comblineWavelength]
        maxLinearCombline = max(linearCombline)
        normalizedLinearCombline = [x/maxLinearCombline for x in linearCombline]
        wavelengthInterp = np.linspace(wavelength[0],wavelength[-1], 1000)
        spectrumInterp = np.interp(wavelengthInterp, wavelength, normalizedLinearCombline)
#        plt.plot(wavelengthInterp, spectrumInterp, 'r')
#        plt.show()
        i = 0
        while True:            
            if spectrumInterp[i] > 0.5:
                bandwidthValue1 = wavelengthInterp[i]
                break
            else:
                i = i + 1
        
        i = len(spectrumInterp) - 1
        while True:
            if spectrumInterp[i] > 0.5:
                bandwidthValue2 = wavelengthInterp[i]
                break
            else:
                i = i - 1
        opticalBandwidth = bandwidthValue2 - bandwidthValue1
        centralWavelengthIndex = linearCombline.index(maxLinearCombline)
        centralWavelength = wavelength[centralWavelengthIndex]
        frequencyBandwidth = 3e8*opticalBandwidth*1e-9/((centralWavelength*1e-9)**2)
        transformLimitedPulsePs = (0.441/frequencyBandwidth)*1e12
        return (opticalBandwidth, transformLimitedPulsePs)
        
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
    
    def get_autocorrelation_values(self, fileName, filePath):
        acFileNameArray = []
        acDispersionArray = []
        acPulseWidthArray = []
        acPulsePeakArray = []
        if os.path.isfile(fileName) == True:
            with open(fileName, "r", newline='') as fileReader:
                self.csvReader = csv.reader(fileReader, delimiter =',', lineterminator='\n')
                for row in self.csvReader:
                    acFileNameArray.append(filePath + "\\SHG\\" + str(row[0]) + ".csv")
                    acDispersionArray.append(float(row[11]))
        else:
            print("Index file does not exist.")
            
        for acDispersion,acFileName in zip(acDispersionArray, acFileNameArray):
            self.read_csv_optical_pulses(acFileName)
            timeOutput = self.get_time_output()
            voltageOutput = self.get_voltage_output()
            self.set_autocorrelation_values(timeOutput, voltageOutput)
#            self.plot_autocorrelation_pulse()
#            print("SHG pulse intensity autocorrelation width: " + str(self.get_autocorrelation_pulse_width()) + " ps")
#            print("SHG pulse intensity autocorrelation peak value: " + str(self.get_autocorrelation_peak_value()) + " V")
            acPulseWidthArray.append(self.get_autocorrelation_pulse_width())
            acPulsePeakArray.append(self.get_autocorrelation_peak_value())
            
        zippedListAcPulseWidth = zip(acDispersionArray, acPulseWidthArray)
        sortedZippedList = sorted(zippedListAcPulseWidth)        
        acPulseWidthArray = [pulsewidth for _, pulsewidth in sortedZippedList]
        
        zippedListAcPulsePeak = zip(acDispersionArray, acPulsePeakArray)
        sortedZippedList = sorted(zippedListAcPulsePeak)        
        acPulsePeakArray = [pulsewidth for _, pulsewidth in sortedZippedList]
        
        acDispersionArray = sorted(acDispersionArray)
        
        self.plot_autocorrelation_values(acDispersionArray, acPulseWidthArray, acPulsePeakArray)
        return (acPulseWidthArray, acPulsePeakArray)
    
    def get_autocorrelation_values_from_file_array(self, fileArray, dispersionArray, filePath):
        acFileNameArray = []
        acDispersionArray = []
        acPulseWidthArray = []
        acPulsePeakArray = []
        for x, y in zip(fileArray, dispersionArray):
            acFileNameArray.append(filePath + "\\" + str(x))
            acDispersionArray.append(float(y))
            
        for acDispersion,acFileName in zip(acDispersionArray, acFileNameArray):
            self.read_csv_optical_pulses(acFileName)
            timeOutput = self.get_time_output()
            voltageOutput = self.get_voltage_output()
            self.set_autocorrelation_values(timeOutput, voltageOutput)
#            self.plot_autocorrelation_pulse()
#            print("SHG pulse intensity autocorrelation width: " + str(self.get_autocorrelation_pulse_width()) + " ps")
#            print("SHG pulse intensity autocorrelation peak value: " + str(self.get_autocorrelation_peak_value()) + " V")
            acPulseWidthArray.append(self.get_autocorrelation_pulse_width())
            acPulsePeakArray.append(self.get_autocorrelation_peak_value())
            
        zippedListAcPulseWidth = zip(acDispersionArray, acPulseWidthArray)
        sortedZippedList = sorted(zippedListAcPulseWidth)        
        acPulseWidthArray = [pulsewidth for _, pulsewidth in sortedZippedList]
        
        zippedListAcPulsePeak = zip(acDispersionArray, acPulsePeakArray)
        sortedZippedList = sorted(zippedListAcPulsePeak)        
        acPulsePeakArray = [pulsewidth for _, pulsewidth in sortedZippedList]
        
        acDispersionArray = sorted(acDispersionArray)
        
        self.plot_autocorrelation_values(acDispersionArray, acPulseWidthArray, acPulsePeakArray)
        return (acPulseWidthArray, acPulsePeakArray)
    
    def create_quadratic_and_cubic_spectral_phase(self, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, comblineWavelength, comblineFrequency, comblineSpectrumWavelength, comblineSpectrumFrequency):
        # Spectrum points for mask

        indexMaxSpectrumWavelength = comblineSpectrumWavelength.index(max(comblineSpectrumWavelength))
        centralWavelength = comblineWavelength[indexMaxSpectrumWavelength - centralFrequencyOffset]
        tempGroupDelayDispersion = [(wavelength-centralWavelength)*tauPerNm for wavelength in comblineWavelength]
        groupDelayDispersion = [x for x in tempGroupDelayDispersion]
#        plt.plot(comblineWavelength, groupDelayDispersion,'r')
#        plt.xlabel('Wavelength (nm)')
#        plt.ylabel('Delay (ps)')
#        plt.show()
        
        groupDelayDispersionFrequency = [x for x in groupDelayDispersion]
        groupDelayDispersionFrequency.reverse()
#        plt.plot(comblineFrequency, groupDelayDispersionFrequency,'b')
#        plt.xlabel('Frequency (THz)')
#        plt.ylabel('Delay (ps)')
#        plt.show()

        quadraticSpectralPhasePsNm = -2*np.pi*integrate.cumtrapz(groupDelayDispersionFrequency, comblineFrequency, initial = 0)
        indexMaxSpectrumFrequency = comblineSpectrumFrequency.index(max(comblineSpectrumFrequency))
#        centralFrequency = comblineFrequency[comblineSpectrumFrequency]        
        quadraticSpectralPhasePsNm = quadraticSpectralPhasePsNm - quadraticSpectralPhasePsNm[indexMaxSpectrumFrequency]
        
        centralFrequencyThz = comblineFrequency[indexMaxSpectrumFrequency + centralFrequencyOffset]
        # Spectral phase calculated as: [(1/2)*k'' (ps^2)] * [2pi (f-f0 (THz))]^3 where k''' is given in ps^2/rad. Normal values around 1.27 [ps^2].
        quadraticSpectralPhase = [(1/2)*((2*np.pi)**2)*quadraticDispersionPs2*((x-centralFrequencyThz)**2) for x in comblineFrequency]
        # Spectral phase calculated as: [(1/6)*k''' (ps^3)] * [2pi (f-f0 (THz))]^3 where k''' is given in ps^3. Normal values around 0.015 [ps^3].
        cubicSpectralPhase = [(1/6)*((2*np.pi)**3)*cubicDispersionPs3*((x-centralFrequencyThz)**3) for x in comblineFrequency]
        # 1.0 ps/nm = 8 ps/THz => (8/(2*pi)) ps/(THz * rad) = 1.2732 ps/(THz * rad) = 1.2732 ps^2/rad ... aproximately.
        spectralPhase = [x + y + z for (x,y,z) in zip(quadraticSpectralPhasePsNm, quadraticSpectralPhase, cubicSpectralPhase)]
        
        plt.plot(comblineFrequency, spectralPhase, 'go')
        plt.xlabel('Frequency (THz)')
        plt.ylabel('Spectral phase (rad)')
        plt.show()
        return spectralPhase
    
    def modify_custom_spectral_phase(self, axialModeOffset, spectralPhaseDelta, comblineFrequency, comblineSpectralPhase):
        # Spectrum points for mask
        
        numberOfAxialModes = len(comblineSpectralPhase)
        numberOfSpectralPhaseComponents = len(comblineSpectralPhase)
        if numberOfAxialModes == numberOfSpectralPhaseComponents:
            if axialModeOffset <= numberOfSpectralPhaseComponents:
                currentSpectralPhase = comblineSpectralPhase[axialModeOffset]
                comblineSpectralPhase[axialModeOffset] = currentSpectralPhase + spectralPhaseDelta
            else:
                print("Axial mode specified exceeds spectral phase components.")
        else:
            print("Number of axial modes and spectral phase components do not match.")
        modifiedComblineSpectralPhase = comblineSpectralPhase
        return modifiedComblineSpectralPhase
    
    def set_optical_spectrum_from_file(self, fileName = None):
        if fileName == None:
            fileName = filedialog.askopenfilename()
    
        self.read_csv_optical_spectrum(fileName)
        wavelengthOutput = self.get_wavelength_output()
        spectrumOutput = self.get_spectrum_output()
        self.set_optical_spectrum_array(wavelengthOutput, spectrumOutput)
#        self.plot_mask_and_original()
    
    def set_autocorrelation_from_file(self, fileName = None):
        if fileName == None:
            fileName = filedialog.askopenfilename()
        
        self.read_csv_optical_pulses(fileName)
        timeOutput = self.get_time_output()
        voltageOutput = self.get_voltage_output()
        self.set_autocorrelation_values(timeOutput, voltageOutput)
        self.plot_autocorrelation_pulse()
        print("SHG pulse intensity autocorrelation width: " + str(self.get_autocorrelation_pulse_width()) + " ps")
        print("SHG pulse intensity autocorrelation peak value: " + str(self.get_autocorrelation_peak_value()) + " V")

    def set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(self, centralFrequencyOffset, tauPerNm, quadraticSpectralPhase, cubicDispersionPs3, filePath, fileName):
        comblineWavelength = self.get_wavelength_combline()
        comblineFrequency = self.get_frequency_combline()
        comblineSpectrumWavelength = self.get_spectrum_combline_wavelength()
        comblineSpectrumFrequency = self.get_spectrum_combline_frequency()
        
        if comblineWavelength == []:
            print("No spectrum has been stored from a file.")
        else:
            spectralPhase = self.create_quadratic_and_cubic_spectral_phase(centralFrequencyOffset, tauPerNm, quadraticSpectralPhase, cubicDispersionPs3, comblineWavelength, comblineFrequency, comblineSpectrumWavelength, comblineSpectrumFrequency)
                
            self.create_waveshaper_mask()
            wsAttenuation = []
            wsPhase = [x for x in spectralPhase]
            wsPort = []
            for i in range(self.get_len_ws_values()):
                wsAttenuation.append(0.000)
#                wsPhase.append(0.000)
                wsPort.append(1)
            self.set_waveshaper_attenuation(wsAttenuation)
            self.set_waveshaper_spectral_phase(wsPhase)
            self.set_waveshaper_port(wsPort)
            
#            Save spectral phase mask
#            self.print_mask()
            self.save_mask(filePath, fileName)
#            self.plot_waveshaper_mask()

    def set_modified_spectral_phase_mask_from_waveshaper_spectral_phase(self, axialModeOffset, spectralPhaseDelta, filePath, fileName):
        waveshaperFrequency = self.get_waveshaper_frequency()
        waveshaperSpectralPhase = self.get_waveshaper_spectral_phase()
        
        if waveshaperSpectralPhase == []:
            print("No spectral phase has been stored from a file.")
        else:
            spectralPhase = self.modify_custom_spectral_phase(axialModeOffset, spectralPhaseDelta, waveshaperFrequency, waveshaperSpectralPhase)

            wsAttenuation = []
            wsPhase = [x for x in spectralPhase]
            wsPort = []
            for i in range(self.get_len_ws_values()):
                wsAttenuation.append(0.000)
#                wsPhase.append(0.000)
                wsPort.append(1)
            self.set_waveshaper_attenuation(wsAttenuation)
            self.set_waveshaper_spectral_phase(wsPhase)
            self.set_waveshaper_port(wsPort)
            
#            Save spectral phase mask
#            self.print_mask()
            self.save_mask(filePath, fileName)
#            self.plot_waveshaper_mask()

if __name__ == "__main__":
    
    dispCalc = DispersionCalculator()

    root = tk.Tk()
    root.withdraw()
    filePath = "H:\\Home\\UP\\Shared\\Ricardo\\DODOS\\DCF Characterization\\DCF OL paper"
    
    fileName = filePath + "\\OSA\\" + "092220-DCF-MLL-PIC-Dispersion0.8psnm--0.1ps3--10AxMo-Python-PC6226.csv"
    dispCalc.set_optical_spectrum_from_file(fileName)
    fileName = filePath + "\\SHG\\" + "092220-DCF-MLL-PIC-Dispersion0.8psnm--0.1ps3--10AxMo-Python-PC6226.csv"
    dispCalc.set_autocorrelation_from_file(fileName)
    
    filePath = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python\\DCF-MLL-PIC'
    fileName = 'MLL-PIC-10GHz.wsp'
#    dispCalc.set_quadratic_spectral_phase_mask_from_acquired_spectrum(2.4, filePath, fileName)
    dispCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(-10, 1.0, 0.0, 0.0, filePath, fileName)
    dispCalc.set_modified_spectral_phase_mask_from_waveshaper_spectral_phase(15, np.pi, filePath, fileName)
    dispCalc.set_spectrum_combline_phase([-x for x in dispCalc.get_waveshaper_spectral_phase()])
    dispCalc.plot_spectral_output()
#
    """
    fileName = filedialog.askopenfilename()    
    acValues = dispCalc.get_autocorrelation_values(fileName, filePath)
    """
    
    
