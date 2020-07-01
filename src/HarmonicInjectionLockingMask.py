# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:49:40 2019

@author: ri679647
"""

from src.MaskCalculator import MaskCalculator
from src.OSA import OSA as OSA6317B
from src.WaveShaperManager import WaveShaperManager
import time
#import datetime
import matplotlib.pyplot as plt

class MasterOpticalFrequencyCombManager():
    def __init__(self):
        self.osaGpibAddress = 'GPIB0::27::INSTR'
        self.filePathOsa = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\OEWaves\\Python\\OSA'
        self.filePathWS = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python'
        self.osaManager = OSA6317B()
        self.wvmngr = WaveShaperManager("ws1")
        self.maskCalc = MaskCalculator()
        self.osaManager.connect(self.osaGpibAddress)
    
    def saveOsaSpectrum(self, fileName, channel):
        self.osaManager.connect(self.osaGpibAddress)
        self.osaManager.single_sweep()
        time.sleep(1)
        self.osaManager.get_span()
        self.osaManager.get_rbw()
        self.osaManager.get_sensitivity()
        self.osaManager.get_ref_lvl()
        self.osaManager.grab_spectrum(channel)
        self.osaManager.save_csv(self.filePathOsa + '\\' + fileName)
#        self.osaManager.close()
        # Print captured spectrum
        plt.plot(self.osaManager.wavelength, self.osaManager.waveform,'b')
        plt.axis([min(self.osaManager.wavelength),max(self.osaManager.wavelength),max([min(self.osaManager.waveform),-75]),max(self.osaManager.waveform)])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
    
    def createThzMask(self, fileNameOFC, minFreqSpacing, maxFreqSpacing):
        # Read file and create mask array
        self.maskCalc.read_csv(self.filePathOsa + '\\' + fileNameOFC)
        self.maskCalc.createMaskArray()
    
        plt.plot(self.maskCalc.wavelength, self.maskCalc.spectrum,'b')
        plt.plot(self.maskCalc.combline_wavelength, self.maskCalc.combline_spectrum,'ro')
        plt.axis([min(self.maskCalc.wavelength), max(self.maskCalc.wavelength), max([min(self.maskCalc.spectrum),-80]), max(self.maskCalc.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
        
        # Create 30 GHz flat mask
        self.maskCalc.createFlatMask()
        # Save flat mask
        self.maskCalc.printMask(self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        fileName = '30GHz-Spacing-Flat.wsp'
        self.maskCalc.saveMask(self.filePathWS, fileName, self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        self.maskCalc.plotMaskAndOriginal(self.maskCalc.spectrum_waveshaper)
        
        # Create harmonic masks
        self.maskCalc.createSetHarmonicMask(self.filePathWS, minFreqSpacing, maxFreqSpacing)
    
    def createArbThzMask(self, fileNameOFC, centralCombLine, minFreqSpacing, maxFreqSpacing):
        # Read file and create mask array
        self.maskCalc.read_csv(self.filePathOsa + '\\' + fileNameOFC)
        self.maskCalc.createMaskArray()
    
        plt.plot(self.maskCalc.wavelength, self.maskCalc.spectrum,'b')
        plt.plot(self.maskCalc.combline_wavelength, self.maskCalc.combline_spectrum,'ro')
        plt.axis([min(self.maskCalc.wavelength), max(self.maskCalc.wavelength), max([min(self.maskCalc.spectrum),-80]), max(self.maskCalc.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
        
        # Create 30 GHz flat mask
        self.maskCalc.createFlatMask()
        # Save flat mask
        self.maskCalc.printMask(self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        fileName = '30GHz-Spacing-Flat.wsp'
        self.maskCalc.saveMask(self.filePathWS, fileName, self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        self.maskCalc.plotMaskAndOriginal(self.maskCalc.spectrum_waveshaper)
        
        # Create harmonic masks
        self.maskCalc.createSetArbHarmonicMask(self.filePathWS, centralCombLine, minFreqSpacing, maxFreqSpacing)

    def create3ToneThzMask(self, fileNameOFC, minFreqSpacing, maxFreqSpacing):
        # Read file and create mask array
        self.maskCalc.read_csv(self.filePathOsa + '\\' + fileNameOFC)
        self.maskCalc.createMaskArray()
    
        plt.plot(self.maskCalc.wavelength, self.maskCalc.spectrum,'b')
        plt.plot(self.maskCalc.combline_wavelength, self.maskCalc.combline_spectrum,'ro')
        plt.axis([min(self.maskCalc.wavelength), max(self.maskCalc.wavelength), max([min(self.maskCalc.spectrum),-80]), max(self.maskCalc.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
        
        # Create 30 GHz flat mask
        self.maskCalc.createFlatMask()
        # Save flat mask
        self.maskCalc.printMask(self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        fileName = '30GHz-Spacing-Flat.wsp'
        self.maskCalc.saveMask(self.filePathWS, fileName, self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        self.maskCalc.plotMaskAndOriginal(self.maskCalc.spectrum_waveshaper)
        
        # Create harmonic masks
        self.maskCalc.createSet3ToneHarmonicMask(self.filePathWS, minFreqSpacing, maxFreqSpacing)
        
    def createMultiToneThzMask(self, fileNameOFC, minFreqSpacing, maxFreqSpacing, flatSpectrum, minThreshold):
        # Read file and create mask array
        self.maskCalc.read_csv(self.filePathOsa + '\\' + fileNameOFC)
        self.maskCalc.createMaskArray()
    
        plt.plot(self.maskCalc.wavelength, self.maskCalc.spectrum,'b')
        plt.plot(self.maskCalc.combline_wavelength, self.maskCalc.combline_spectrum,'ro')
        plt.axis([min(self.maskCalc.wavelength), max(self.maskCalc.wavelength), max([min(self.maskCalc.spectrum),-80]), max(self.maskCalc.spectrum)+5])
        plt.xlabel('Wavelength (nm)')
        plt.ylabel('Output (dB)')
        plt.show()
        
        # Create 30 GHz flat mask
        self.maskCalc.createFlatMaskWithThreshold(minThreshold)
        # Save flat mask
        self.maskCalc.printMask(self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        fileName = '30GHz-Spacing-Flat.wsp'
        self.maskCalc.saveMask(self.filePathWS, fileName, self.maskCalc.frequency_waveshaper, self.maskCalc.spectrum_waveshaper)
        self.maskCalc.plotMaskAndOriginal(self.maskCalc.spectrum_waveshaper)
        
        # Create harmonic masks
        self.maskCalc.createSetMultiToneHarmonicMask(self.filePathWS, minFreqSpacing, maxFreqSpacing, flatSpectrum)    
    
    def setOfcBlocked(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def setOfcAllPass(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.pass_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadHarmonicProfile(self, OfcFreqSpacing):
        fileProfile = self.filePathWS + '\\' + OfcFreqSpacing + 'GHz-Spacing.wsp'
        profileName = OfcFreqSpacing + 'GHz-Spacing'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setHarmonicProfile(self, OfcFreqSpacing):
        profileName = OfcFreqSpacing + 'GHz-Spacing'
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.load_profile_to_waveshaper(profileName)
        self.wvmngr.disconnect_from_waveshaper()
    
    def closePorts(self):
        self.osaManager.close()
        

if __name__ == "__main__":
    
    # Take Original EOM Comb
#    fileName = 'OEW_SOA-max_FPE_EDFAmax_1PM-IM-29.9286GHz-10dBm-0.31V_SOA_150mA_EDFA_350mW_1000mSMF_100m-HNLF-ND_Att-30mW_WS' + '.csv
#    fileName = 'Test-OEW_SOA-max_FPE_EDFAmax_1PM-IM-30GHz-10dBm-1.31V_SOA_EDFA_1200mW_1000mSMF_100m-HNLF-ND_Att-100mW_WS' + '.csv'
    fileName = 'OEW_FPE_EOM-29.934GHz_HNLF-ZD.csv'
    masterOfcMngr = MasterOpticalFrequencyCombManager()
    masterOfcMngr.setOfcAllPass()
    masterOfcMngr.saveOsaSpectrum(fileName, 'C')
    
#    Create Mask Array
    masterOfcMngr.createMultiToneThzMask(fileName, 60, 300, True, -30)
#    masterOfcMngr.createThzMask(fileName, 60, 300)
    
#     Save harmonic OFC master
    fileBaseline = 'OEW_FPE_EOM-29.934GHz_HNLF-ZD_WS_'
    ofcSpacingList = ['60','90','120','150','180','210','240','270','300']
#    ofcSpacingList20 = ['60','120','180']
    for ofcSpacing in ofcSpacingList:
        print('OFC Spacing: ' + ofcSpacing + ' GHz')
        input("Press Enter to continue...")
        ofcFileName = fileBaseline + ofcSpacing + 'GHz-Spacing.csv '
        masterOfcMngr.loadHarmonicProfile(ofcSpacing)
        masterOfcMngr.setHarmonicProfile(ofcSpacing)
        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'C')

    masterOfcMngr.closePorts()
        

    
    
    
    