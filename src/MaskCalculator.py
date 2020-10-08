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

class MaskCalculator():
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
    def __init__(self, wsPhaseArray):
        self.wsPhase = wsPhaseArray
        self.wsPort = 1
        self.header = []
        self.wavelength = []
        self.spectrum = []
        self.freq_sep = 30 # 30 GHz
        self.wavelength_sep = 0.24 # Equivalent nm to 30 GHz at 1550 nm
#        self.spectrum_waveshaper_harmonic = []
        # Spectrum points for mask
        self.combline_spectrum = []
        self.combline_wavelength = []
        self.combline_frequency = []
        self.c0 = 299792458  # Light speed in m/s
        self.frequency_offset = 192.682-192.63 # Difference between waveshaper and OSA
        self.frequency_waveshaper = []
        self.spectrum_waveshaper = []
#        self.frequency_waveshaper_mask = []
#        self.spectrum_waveshaper_mask = []
    
    def printMask(self,frequency_waveshaper,spectrum_waveshaper):
        """This method prints the frequency and attenuation array in a Finisar 1000M compatible format.
        
        The method prints the frequency and corresponding spectral output as:
        
            192.637 00.000  0   1
            192.647 00.000  0   1
            192.657 50.000  0   1
            ...
            
        Where the last two values are the spectral phase (usually 0) and output port (usually 1).
        
        Parameters
        ----------
        frequency_waveshaper: list
            Mask frequency values (in THz).
        spectrum_waveshaper: list
            Mask attenuation values (in dB ranging 0-50).
        """
        for x, y, z in zip(frequency_waveshaper,spectrum_waveshaper, self.wsPhase):
            if abs(y) < 10:
                print("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}".format(x,y,z,self.wsPort))
            else:
                print("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}".format(x,y,z,self.wsPort))
   
    def saveMask(self,filePath,fileName,frequency_waveshaper_mask,spectrum_waveshaper_mask):
        """This method saves in a WSP file the frequency and attenuation array in a Finisar 1000M compatible format.
        
        The method saves a WSP file that contains the frequency and corresponding spectral output as:
        
            192.637 00.000  0   1
            192.647 00.000  0   1
            192.657 50.000  0   1
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
        for x, y, z in zip(frequency_waveshaper_mask,spectrum_waveshaper_mask,self.wsPhase):
            if abs(y) < 10:
                fileWriter.write("{0:.3f}\t0{1:.3f}\t{2:.3f}\t{3}\r".format(x,y,z,self.wsPort))
            else:
                fileWriter.write("{0:.3f}\t{1:.3f}\t{2:.3f}\t{3}\r".format(x,y,z,self.wsPort))
        fileWriter.close()
        
    
    def calculateHarmonicMask(self,spectrum_waveshaper,offset1,offset2):
        """This method calculates a mask for harmonic injection locking with two modes.
        
        A method to calculate a mask with two axial modes set by the offset values from the central axial mode.
        
        Parameters
        ----------
        spectrum_waveshaper: list
            Contains the waveshaper spectral values
        
        """
        spectrum_waveshaper_harmonic = []
        number_of_comblines = int((len(spectrum_waveshaper)/2)-2)
        center_combline = int(number_of_comblines/2) + 1
        center_combline = int(input("Is " + str(center_combline) + " the center combline? Input combline number: "))
        combline_1 = center_combline + offset1
        combline_2 = center_combline + offset2
        #    print(number_of_comblines)
        #    print(center_combline)
        for (i,x) in zip(range(len(spectrum_waveshaper)),spectrum_waveshaper):
            if (i == combline_1*2 or i == combline_1*2+1 or i == combline_2*2 or i == combline_2*2+1):
                spectrum_waveshaper_harmonic.append(x)
            else:
                spectrum_waveshaper_harmonic.append(50)
        spectrum_waveshaper_harmonic = [x-min(spectrum_waveshaper_harmonic) if x!=50 else x for x in spectrum_waveshaper_harmonic]
        return spectrum_waveshaper_harmonic

    def calculate3ToneHarmonicMask(self,spectrum_waveshaper,offset1,offset2):
        spectrum_waveshaper_harmonic = []
        number_of_comblines = int((len(spectrum_waveshaper)/2)-2)
        center_combline = int(number_of_comblines/2) + 1
        center_combline = int(input("Is " + str(center_combline) + " the center combline? Input combline number: "))
        combline_1 = center_combline + offset1
        combline_2 = center_combline + offset2
        #    print(number_of_comblines)
        #    print(center_combline)
        for (i,x) in zip(range(len(spectrum_waveshaper)),spectrum_waveshaper):
            if (i == combline_1*2 or i == combline_1*2+1 or i == combline_2*2 or i == combline_2*2+1):
                spectrum_waveshaper_harmonic.append(x)
            elif (i == center_combline*2 or i == center_combline*2+1):
                spectrum_waveshaper_harmonic.append(x) # To not take this value into account for minimum value.
            else:
                spectrum_waveshaper_harmonic.append(50)
        min_spectrum_waveshaper_harmonic = min(spectrum_waveshaper_harmonic)
        spectrum_waveshaper_harmonic = [x-min_spectrum_waveshaper_harmonic if x!=50 else x for x in spectrum_waveshaper_harmonic]
        #spectrum_waveshaper_harmonic = [0 if x==70 else x for x in spectrum_waveshaper_harmonic]
        return spectrum_waveshaper_harmonic
    
    def calculateMultiToneHarmonicMask(self, spectrum_waveshaper,offset,flatSpectrum):
        spectrum_waveshaper_harmonic = []
        number_of_comblines = int((len(spectrum_waveshaper)/2)-2)
        center_combline = int(number_of_comblines/2) + 1
        center_combline = int(input("Is " + str(center_combline) + " the center combline? Input combline number: "))
        combline = []
        print(len(spectrum_waveshaper)/2)
        for k in range(int(len(spectrum_waveshaper)/2-2)): # -2 comes from the two extra values that aren't axial modes
            if (k-center_combline)%offset == 0:
                combline.append(2*k)
                combline.append(2*k+1)
            else:
                pass
#        print(combline)
        for (i,x) in zip(range(len(spectrum_waveshaper)),spectrum_waveshaper):
            if i == 0 or i == 1 or i == len(spectrum_waveshaper)-2 or i == len(spectrum_waveshaper)-1:            
                spectrum_waveshaper_harmonic.append(50)
            elif (combline.count(i-2) == 1):
                if flatSpectrum == True:
                    spectrum_waveshaper_harmonic.append(x)
                else:
                    spectrum_waveshaper_harmonic.append(0)
            else:
                spectrum_waveshaper_harmonic.append(50)
        
        min_spectrum_waveshaper_harmonic = min(spectrum_waveshaper_harmonic)
        spectrum_waveshaper_harmonic = [x-min_spectrum_waveshaper_harmonic if x!=50 else x for x in spectrum_waveshaper_harmonic]
        #spectrum_waveshaper_harmonic = [0 if x==70 else x for x in spectrum_waveshaper_harmonic]
        return spectrum_waveshaper_harmonic
        
    
    def plotMaskAndOriginal(self,spectrum_waveshaper_mask):
        plt.plot(self.combline_frequency,self.combline_spectrum,'ro')
#        plot_number = []
        plot_number_mask = []
        for (x,y) in zip(self.spectrum_waveshaper,spectrum_waveshaper_mask):
#            plot_number.append(min(self.combline_spectrum)+x)
            plot_number_mask.append(-y)
#        plt.plot(self.frequency_waveshaper,plot_number,'b')
        plt.plot(self.frequency_waveshaper,plot_number_mask,'k')
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
        index_30GHz_span = int(self.len_wavelength/section_wavelength)
#        print(index_30GHz_span)
        spectrum_max_index = self.spectrum.index(self.max_spectrum)
#        print(self.spectrum[spectrum_max_index])
        if int((spectrum_max_index%index_30GHz_span)-(index_30GHz_span/2)) > 0:
            initial_index = int((spectrum_max_index%index_30GHz_span)-(index_30GHz_span/2))
        else:
            initial_index = int((spectrum_max_index%index_30GHz_span)+(index_30GHz_span/2))
#        print(initial_index)
#        print(self.wavelength[initial_index])
        # Make sure is only an even number of comblines
        section_wavelength = int(section_wavelength)
#        print(section_wavelength)
        if (section_wavelength % 2) == 0:
            section_wavelength -= 1
        for i in range(section_wavelength):
#            print(i)
            sub_spectrum = self.spectrum[initial_index+i*index_30GHz_span:initial_index+(i+1)*index_30GHz_span]
            self.combline_spectrum.append(max(sub_spectrum))
            max_index = initial_index + i*index_30GHz_span + sub_spectrum.index(self.combline_spectrum[i])
            self.combline_wavelength.append(self.wavelength[max_index])
        for x in self.combline_wavelength:
            self.combline_frequency.append(((self.c0/(x*1e-9))*1e-12)-self.frequency_offset)
        self.combline_frequency.sort()
        self.combline_spectrum.reverse()
    
    def createFlatMask(self):
        """This method creates a flat mask for the spectrum.
        
        This method creates two lists:
        
        1. frequency_waveshaper: List with frequency values centered at axial mode (stored in frequency_waveshaper) peaks +/- waveshaper minimum step size.        
        2. spectrum_waveshaper: List with corresponding spectral values that attenuate to create a flat spectral output (using value stored in combline_spectrum).        
        .. math:: f_{WS}=[f_{0}-4\Delta_{WS},f_{0}-2\Delta_{WS},f_{0}-\Delta_{WS} ,f_{0}+\Delta_{WS} ,...,f_{N-1}-\Delta_{WS} ,f_{N-1}+\Delta_{WS} ,f_{N}-\Delta_{WS} ,f_{N}+\Delta_{WS} ,f_{N}+2\Delta_{WS},f_{N}+4\Delta_{WS}]        
        .. math:: A_{WS}=[             50 dB,             50 dB,A_{0}-min\{A_{n}\},A_{0}-min\{A_{n}\},...,A_{N-1}-min\{A_{n}\},A_{N-1}-min\{A_{n}\},A_{N}-min\{A_{n}\},A_{N}-min\{A_{n}\},             50 dB,             50 dB]
        """
        # Now we are going to make the mask for the waveshaper       
        delta_waveshaper = 0.005    # Delta/2 between points in the waveshaper

        for x in self.combline_frequency:
            self.frequency_waveshaper.append(x-delta_waveshaper)
            self.frequency_waveshaper.append(x+delta_waveshaper)
        self.frequency_waveshaper.append(self.frequency_waveshaper[-1]+(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[-1]+(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[0]-(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[0]-(delta_waveshaper*4))
        
        self.frequency_waveshaper.sort()
    #    print(frequency_waveshaper)
        
        min_combline_spectrum = min(self.combline_spectrum)
        self.spectrum_waveshaper.append(50)
        self.spectrum_waveshaper.append(50)
        for x in self.combline_spectrum:
            self.spectrum_waveshaper.append(x-min_combline_spectrum)
            self.spectrum_waveshaper.append(x-min_combline_spectrum)
        self.spectrum_waveshaper.append(50)
        self.spectrum_waveshaper.append(50)

    def createFlatMaskWithThreshold(self, minThreshold = -30.00):
        """This method creates a flat mask for the spectrum with a threshold for minimum values.
        
        This method creates two lists:
        
        1. frequency_waveshaper: List with frequency values centered at axial mode (stored in frequency_waveshaper) peaks +/- waveshaper minimum step size.        
        2. spectrum_waveshaper: List with corresponding spectral values that attenuate to create a flat spectral output with a threshold limit (using value stored in combline_spectrum).        
        .. math:: f_{WS}=[f_{0}-4\Delta_{WS},f_{0}-2\Delta_{WS},f_{0}-\Delta_{WS} ,f_{0}+\Delta_{WS} ,...,f_{N-1}-\Delta_{WS} ,f_{N-1}+\Delta_{WS} ,f_{N}-\Delta_{WS} ,f_{N}+\Delta_{WS} ,f_{N}+2\Delta_{WS},f_{N}+4\Delta_{WS}]        
        .. math:: A_{WS}=[             50 dB,             50 dB,A_{0}-min\{A_{n}\},A_{0}-min\{A_{n}\},...,A_{N-1}-min\{A_{n}\},A_{N-1}-min\{A_{n}\},A_{N}-min\{A_{n}\},A_{N}-min\{A_{n}\},             50 dB,             50 dB]
        """
        # Now we are going to make the mask for the waveshaper       
        delta_waveshaper = 0.005    # Delta/2 between points in the waveshaper

        for x in self.combline_frequency:
            self.frequency_waveshaper.append(x-delta_waveshaper)
            self.frequency_waveshaper.append(x+delta_waveshaper)
        self.frequency_waveshaper.append(self.frequency_waveshaper[-1]+(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[-1]+(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[0]-(delta_waveshaper*2))
        self.frequency_waveshaper.append(self.frequency_waveshaper[0]-(delta_waveshaper*4))
        
        self.frequency_waveshaper.sort()
    #    print(frequency_waveshaper)
        min_combline_spectrum_with_limit = []
        for y in self.combline_spectrum:
            if y >= minThreshold:
                min_combline_spectrum_with_limit.append(y)
        min_combline_spectrum = min(min_combline_spectrum_with_limit)
        
        self.spectrum_waveshaper.append(50)
        self.spectrum_waveshaper.append(50)
        for x in self.combline_spectrum:
            if x >= minThreshold:
                self.spectrum_waveshaper.append(x-min_combline_spectrum)
                self.spectrum_waveshaper.append(x-min_combline_spectrum)
            else: # If value is below threshold just eliminate it.
                self.spectrum_waveshaper.append(50)
                self.spectrum_waveshaper.append(50)
        self.spectrum_waveshaper.append(50)
        self.spectrum_waveshaper.append(50)
    
    def createHarmonicMask(self, maskFilePath, maskFileName,combLineNumber):
        spectrum_waveshaper_harmonic = self.calculateHarmonicMask(self.spectrum_waveshaper,-combLineNumber,combLineNumber)
#           self.printMask(maskCalc.frequency_waveshaper,spectrum_waveshaper_60GHz)
#           maskFileName = '60GHz-Spacing.wsp'
        self.saveMask(maskFilePath,maskFileName,self.frequency_waveshaper,spectrum_waveshaper_harmonic)
        self.plotMaskAndOriginal(spectrum_waveshaper_harmonic)
        
    def createArbHarmonicMask(self, maskFilePath, maskFileName, combLineNumber1,combLineNumber2):
        spectrum_waveshaper_harmonic = self.calculateHarmonicMask(self.spectrum_waveshaper,combLineNumber1,combLineNumber2)
#           self.printMask(maskCalc.frequency_waveshaper,spectrum_waveshaper_60GHz)
#           maskFileName = '60GHz-Spacing.wsp'
        self.saveMask(maskFilePath,maskFileName,self.frequency_waveshaper,spectrum_waveshaper_harmonic)
        self.plotMaskAndOriginal(spectrum_waveshaper_harmonic)

    def create3ToneHarmonicMask(self, maskFilePath, maskFileName, combLineNumber):
        spectrum_waveshaper_harmonic = self.calculate3ToneHarmonicMask(self.spectrum_waveshaper,-combLineNumber,combLineNumber)
#           self.printMask(maskCalc.frequency_waveshaper,spectrum_waveshaper_60GHz)
#           maskFileName = '60GHz-Spacing.wsp'
        self.saveMask(maskFilePath,maskFileName,self.frequency_waveshaper,spectrum_waveshaper_harmonic)
        self.plotMaskAndOriginal(spectrum_waveshaper_harmonic)
    
    def createMultiToneHarmonicMask(self, maskFilePath, maskFileName, combLineNumber,flatSpectrum):
        spectrum_waveshaper_harmonic = self.calculateMultiToneHarmonicMask(self.spectrum_waveshaper,combLineNumber,flatSpectrum)
#           self.printMask(maskCalc.frequency_waveshaper,spectrum_waveshaper_60GHz)
#           maskFileName = '60GHz-Spacing.wsp'
        self.saveMask(maskFilePath,maskFileName,self.frequency_waveshaper,spectrum_waveshaper_harmonic)
        self.plotMaskAndOriginal(spectrum_waveshaper_harmonic)
    
    def createSetHarmonicMask(self, filePath, initSpacing, endSpacing):
        # Save 60 GHz comb
        initSpacingIndex = initSpacing // 60
        endSpacingIndex = endSpacing // 60
        for n in range(initSpacingIndex,endSpacingIndex+1):
            combSpacing = str(n*60)
            print(combSpacing + ' GHz Spacing')
            fileName = combSpacing  + 'GHz-Spacing.wsp'
            self.createHarmonicMask(filePath, fileName, n)      
    
    def createSetArbHarmonicMask(self, filePath, centralCombLine, initSpacing, endSpacing):
        # Save 60 GHz comb
        initSpacingIndex = initSpacing // 60
        endSpacingIndex = endSpacing // 60
        for n in range(initSpacingIndex,endSpacingIndex+1):
            combSpacing = str(n*60)
            print(combSpacing + ' GHz Spacing')
            fileName = combSpacing  + 'GHz-Spacing.wsp'
            harmonicCombNumber = centralCombLine + 2*n
            self.createArbHarmonicMask(filePath, fileName, harmonicCombNumber, centralCombLine)
    
    def createSet3ToneHarmonicMask(self, filePath, initSpacing, endSpacing):
        # Save 60 GHz comb
        initSpacingIndex = initSpacing // 60
        endSpacingIndex = endSpacing // 60
        for n in range(initSpacingIndex,endSpacingIndex+1):
            combSpacing = str(n*60)
            print(combSpacing + ' GHz Spacing')
            fileName = combSpacing  + 'GHz-Spacing.wsp'
            harmonicCombNumber = 2*n
            self.create3ToneHarmonicMask(filePath, fileName, harmonicCombNumber)
    
    def createSetMultiToneHarmonicMask(self, filePath, initSpacing, endSpacing, flatSpectrum):
        # Save 30 GHz comb
        initSpacingIndex = initSpacing // 30
        endSpacingIndex = endSpacing // 30
        for n in range(initSpacingIndex,endSpacingIndex+1):
            combSpacing = str(n*30)
            print(combSpacing + ' GHz Spacing')
            fileName = combSpacing  + 'GHz-Spacing.wsp'
            harmonicCombNumber = n
            self.createMultiToneHarmonicMask(filePath, fileName, harmonicCombNumber, flatSpectrum)        

if __name__ == "__main__":
    
    maskCalc = MaskCalculator()
    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\CW PDH Laser\\CW Homemade\\Enhanced WS Design\\EOM Comb\\OSA'
    fileName = filePath + '\\' + 'OSA_CW-FPE-PDHlocked_PM-PM-10dBm_SOA-450mA_WS-Pass_Att-0_50-50_2019-07-02_12-53.csv'
#    print(filePath)

    root = tk.Tk()
    root.withdraw()
    
    fileName = filedialog.askopenfilename()
    
    maskCalc.read_csv(fileName)
    maskCalc.createMaskArray()

    plt.plot(maskCalc.wavelength,maskCalc.spectrum,'b')
    plt.plot(maskCalc.combline_wavelength,maskCalc.combline_spectrum,'ro')
    plt.axis([min(maskCalc.wavelength),max(maskCalc.wavelength),max([min(maskCalc.spectrum),-80]),max(maskCalc.spectrum)+5])
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Output (dB)')
    plt.show() 

    maskCalc.createFlatMask()
    
    filePath = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2019\\CW 0.5THz Python'
    # Save flat etalon response
    maskCalc.printMask(maskCalc.frequency_waveshaper,maskCalc.spectrum_waveshaper)
    fileName = '30GHz-Spacing-Flat.wsp'
    maskCalc.saveMask(filePath,fileName,maskCalc.frequency_waveshaper,maskCalc.spectrum_waveshaper)
    maskCalc.plotMaskAndOriginal(maskCalc.spectrum_waveshaper)
    print("\r")
    
    # Save 60 GHz comb
    print('60 GHz Spacing')
    fileName = '60GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 1)

    # Save 120 GHz comb
    print('120 GHz Spacing')
    fileName = '120GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 2)

    # Save 180 GHz comb (red)
    print('180 GHz Spacing')
    fileName = '180GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 3)
    
    # Save 240 GHz comb (red)
    print('240 GHz Spacing')
    fileName = '240GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 4)

    # Save 300 GHz comb (red)
    print('300 GHz Spacing')
    fileName = '300GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 5)
    
    # Save 360 GHz comb (red)
    print('360 GHz Spacing')
    fileName = '360GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 6)

    # Save 420 GHz comb (red)
    print('420 GHz Spacing')
    fileName = '420GHz-Spacing.wsp'
    maskCalc.createHarmonicMask(filePath, fileName, 7)
#    
#    # Save 480 GHz comb (red)
#    print('480 GHz Spacing')
#    fileName = '480GHz-Spacing.wsp'
#    maskCalc.createHarmonicMask(filePath, fileName, 8)
#
#    # Save 540 GHz comb (red)
#    print('540 GHz Spacing')
#    fileName = '540GHz-Spacing.wsp'
#    maskCalc.createHarmonicMask(filePath, fileName, 9)


    
        
    
    
    