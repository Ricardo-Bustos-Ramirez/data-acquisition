# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 13:21:34 2019

@author: ri679647
"""

import matplotlib.pyplot as plt
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog

class OpticalDataManager():
    def __init__(self):
        self.fileName = ''
        self.xVar = []
        self.yVar = []
        self.header = []
        self.xArray = []
        self.yArray = []
        
    def read_csv(self, delimiterType, xCol, yCol):
        with open(self.fileName, 'r') as fileReader:
            if delimiterType == 'comma':
                self.csvReader = csv.reader(fileReader, delimiter = ',')
            elif delimiterType == 'tab':
                self.csvReader = csv.reader(fileReader, delimiter = '\t')
            else: 
                self.csvReader = csv.reader(fileReader)
            for row in self.csvReader:
                if len(row) >= 2:
                    self.xVar.append(float(row[xCol]))
                    self.yVar.append(float(row[yCol]))
                else:
                    self.header.append(row)
    
    def conv_to_array(self):
        self.xArray = np.asarray(self.xVar)
        self.yArray = np.asarray(self.yVar)
    
    def set_file_name(self):
        root = tk.Tk()
        root.withdraw()
        self.fileName = filedialog.askopenfilename()
    
class OpticalPulseDataManager(OpticalDataManager):
    def __init__(self, conversionFactor):
        OpticalDataManager.__init__(self)
        self.delayPsVar = []
        self.delayPsArray = []
        self.shgIntensityVar = []
        self.shgIntensityArray = []
        self.conversionFactor = conversionFactor
        self.FWHM = 0
    
    def variable_conversion(self):
        timePs = []
        timePsOffset = []
        normalizedOutput = []
        for xOutputValue in self.xVar:
            timePs.append(xOutputValue * self.conversionFactor * 1e3)
        maxOutput = max(self.yVar)
        for yOutputValue in self.yVar:
            normalizedOutput.append(yOutputValue/maxOutput)
        maxOutputIndex = normalizedOutput.index(1)
        for timePsValues in timePs:
            timePsOffset.append(timePsValues - timePs[maxOutputIndex])
        # Save variables
        self.delayPsVar = timePsOffset
        self.delayPsArray = np.asarray(self.delayPsArray)
        self.shgIntensityVar = normalizedOutput
        self.shgIntensityArray = np.asarray(self.shgIntensityVar)
    
    def calculate_FWHM(self):
        negativeFWHMvalues = []
        positiveFWHMvalues = []
#        for delayValue in self.delayPsVar:
#            if delayValue
    
            
if __name__ == "__main__":
    
#    print(filePath)

    pulseDataMngr = OpticalPulseDataManager(31.5)
    
    pulseDataMngr.set_file_name()
    pulseDataMngr.read_csv('comma', 3, 4)
    pulseDataMngr.variable_conversion()
    
    delayPs = pulseDataMngr.delayPsVar
    shgIntensityAU = pulseDataMngr.shgIntensityVar

    
    plt.plot(delayPs,shgIntensityAU,'b')
#    plt.plot(maskCalc.combline_wavelength,maskCalc.combline_spectrum,'ro')
    plt.axis([min(delayPs),max(delayPs),min([min(shgIntensityAU),-0.1]),max([max(shgIntensityAU),1.1])])
    plt.xlabel('Delay (ps)')
    plt.ylabel('SHG Intensity (a.u.)')
    plt.show() 