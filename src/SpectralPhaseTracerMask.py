# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 11:49:40 2019

@author: ri679647
"""

from src.DispersionCalculator import DispersionCalculator
from src.OSA import OSA as OSA6317B
from src.TDS import TDS as TDS210
from src.WaveShaperManager import WaveShaperManager
import time
#import datetime
import matplotlib.pyplot as plt
import numpy as np

class MllOpticalFrequencyCombManager():
    def __init__(self):
        self.osaGpibAddress = 'GPIB0::27::INSTR'
        self.tdsGpibAddress = 'GPIB0::5::INSTR'
        self.filePathOsa = 'H:\\Home\\UP\\Shared\\Ricardo\\DODOS\\DCF Characterization\\DCF OL paper\\SpectralPhase\\OSA'
        self.filePathTds = 'H:\\Home\\UP\\Shared\\Ricardo\\DODOS\\DCF Characterization\\DCF OL paper\\SpectralPhase\\SHG'        
        self.filePathWS = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2020\\Python\\DCF-MLL-PIC'
        self.osaManager = OSA6317B()
        self.tdsManager = TDS210()
        self.wvmngr = WaveShaperManager("ws1")
        self.maskCalc = DispersionCalculator()
        self.osaManager.connect(self.osaGpibAddress)
        self.tdsManager.connect(self.tdsGpibAddress)
    
    def saveOsaSpectrum(self, fileName, channel):
        self.osaManager.connect(self.osaGpibAddress)
#        self.osaManager.single_sweep()
        time.sleep(1)
        self.osaManager.get_span()
        self.osaManager.get_rbw()
        self.osaManager.get_sensitivity()
        self.osaManager.get_ref_lvl()
        self.osaManager.grab_spectrum(channel)
        self.osaManager.save_csv(self.filePathOsa + '\\' + fileName)
#        self.osaManager.close()
        # Print captured spectrum
        self.osaManager.plot_waveform()

    def saveTdsSpectrum(self, fileName):
        self.tdsManager.connect(self.tdsGpibAddress)
        self.tdsManager.set_osc_state('STOP')
        print("TDS Stopped...")
        time.sleep(1)
        self.tdsManager.set_osc_state('RUN')
        print("TDS Running...")
        time.sleep(10)
        print("TDS Acquiring...")
        self.tdsManager.acquire_waveform()
        self.tdsManager.save_csv(self.filePathTds + '\\' + fileName)
#        self.osaManager.close()
        # Print captured spectrum
        self.tdsManager.plot_waveform()
    
    def createLinearChirpAndCubicPhaseMask(self, fileNameOsa, centralFrequencyOffset, tauPerNm, cubicDispersionPs3):
        # Read file and create mask array
        fileName = self.filePathOsa + '\\' + fileNameOsa
        self.maskCalc.set_optical_spectrum_from_file(fileName)
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(tauPerNm) + 'ps-nm' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.maskCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(centralFrequencyOffset, tauPerNm, cubicDispersionPs3, self.filePathWS, profileName)

    def setOfcBlocked(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def setOfcAllPass(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.pass_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadDispersionProfile(self, centralFrequencyOffset, tauPerNm, cubicDispersionPs3):
        fileProfile = self.filePathWS + '\\' + str(centralFrequencyOffset) + 'AxMo' + str(tauPerNm) + 'ps-nm' + str(cubicDispersionPs3) + 'ps3.wsp'
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(tauPerNm) + 'ps-nm' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setDispersionProfile(self, centralFrequencyOffset, tauPerNm, cubicDispersionPs3):
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(tauPerNm) + 'ps-nm' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.load_profile_to_waveshaper(profileName)
        self.wvmngr.disconnect_from_waveshaper()
    
    def closePorts(self):
        self.osaManager.close()
        self.tdsManager.close()
    
    def calculate_bandwidth_and_tlp(self):
        opticalBandwidthAndTlp = self.maskCalc.get_optical_spectrum_bandwidth_and_tlp()
        return opticalBandwidthAndTlp
    
    def calculate_dispersion_and_pulse_width(self, fileArray, tauPerNmArray):
        filePath = self.filePathTds
        acValues = self.maskCalc.get_autocorrelation_values_from_file_array(fileArray, tauPerNmArray, filePath)
        return acValues
    
    def calculate_tlp_from_parameter_sweep(self, opticalBandwidthNm, transformLimitedPulsePs, opticalPulsewidthPsList, parameterSweep, parameterSweepUnits):
        print("Optical bandwidth: " + str(opticalBandwidthNm) + " nm.")
        print("Transform limited pulse: " + str(transformLimitedPulsePs) + " ps.")
        timesTlp = [x*0.7071/transformLimitedPulsePs for x in opticalPulsewidthPsList]
        plt.plot(parameterSweep, timesTlp)
        plt.axis([min(parameterSweep), max(parameterSweep), min(timesTlp)-0.1, max(timesTlp)+0.1])
        plt.xlabel('Dispersion ' + '[' + parameterSweepUnits + ']')
        plt.ylabel('TLP times (a.u.)')
        plt.show()
#        print("Minimum TLPx = " + min(timesTlp) + "at)
        return timesTlp

    def set_dispersion_profile_and_save_autocorrelation_trace(self, fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, cubicDispersionPs3):
        print('OFC Dispersion: ' + str(tauPerNm) + ' [ps/nm], ' + str(cubicDispersionPs3) + ' [ps^3], offset from central frequency: ' + str(centralFrequencyOffset) + ' axial modes.')
#        input("Press Enter to continue...")
        shgAcFileName = fileNameShg + str(tauPerNm) + 'ps-nm' + str(cubicDispersionPs3) + 'ps3.csv'
        self.createLinearChirpAndCubicPhaseMask(fileNameOsa, centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
        self.loadDispersionProfile(centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
        self.setDispersionProfile(centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
#        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'A')
        self.saveTdsSpectrum(shgAcFileName)
        return shgAcFileName
    
    def sweep_quadratic_dispersion_parameter(self, fileNameOsa, initialDispersion, endDispersion, numberOfSamples, cubicDispersionPs3, centralFreqOffset):
        tauPerNmArray = np.linspace(initialDispersion, endDispersion, numberOfSamples)
        tauPerNmList = [round(x,2) for x in tauPerNmArray]
        print(tauPerNmList)
#        input("Press Enter to continue...")
        fileArrayQuadratic = []
        for tauPerNm in tauPerNmList:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
            fileArrayQuadratic.append(shgAcFileName)     
        acValues = self.calculate_dispersion_and_pulse_width(fileArrayQuadratic, tauPerNmList)
        minPulsewidth = min(acValues[0])
        maxPulsePeak = max(acValues[1])
        indexMinPulseWidth = acValues[0].index(minPulsewidth)
        indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
        dispersionMinPulsewidth = tauPerNmList[indexMinPulseWidth]
        dispersionMaxPulsePeak = tauPerNmList[indexMaxPulsePeak]
        print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(dispersionMinPulsewidth) + "ps/nm")
        print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(dispersionMaxPulsePeak) + "ps/nm")
        return (acValues, tauPerNmList, minPulsewidth, maxPulsePeak, dispersionMinPulsewidth, dispersionMaxPulsePeak)

    def sweep_cubic_dispersion_parameter(self, fileNameOsa, tauPerNm, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples, centralFreqOffset):
        cubiConstantArray = np.linspace(initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples)
        cubicDispersionPs3List = [round(x,4) for x in cubiConstantArray]
        print(cubicDispersionPs3List)
#        input("Press Enter to continue...")
        fileArrayCubic = []
        for cubicDispersionPs3 in cubicDispersionPs3List:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
            fileArrayCubic.append(shgAcFileName)     
        acValues = self.calculate_dispersion_and_pulse_width(fileArrayCubic, cubicDispersionPs3List)
        minPulsewidth = min(acValues[0])
        maxPulsePeak = max(acValues[1])
        indexMinPulseWidth = acValues[0].index(minPulsewidth)
        indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
        cubicDispersionMinPulsewidth = cubicDispersionPs3List[indexMinPulseWidth]
        cubicDispersionMaxPulsePeak = cubicDispersionPs3List[indexMaxPulsePeak]
        print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(dispersionMinPulsewidth) + " [ps^3]")
        print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(dispersionMaxPulsePeak) + " [ps^3]")
        return (acValues, cubicDispersionPs3List, minPulsewidth, maxPulsePeak, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak)

    def sweep_central_frequancy_offset_dispersion_parameter(self, fileNameOsa, tauPerNm, cubicDispersionPs3, initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples):
        centralFrequencyOffsetArray = np.linspace(initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples)
        centralFrequencyOffsetList = [int(x) for x in centralFrequencyOffsetArray]
        print(centralFrequencyOffsetList)
#        input("Press Enter to continue...")
        fileArrayOffset = []
        for centralFrequencyOffset in centralFrequencyOffsetList:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
            fileArrayOffset.append(shgAcFileName)    
        acValues = self.calculate_dispersion_and_pulse_width(fileArrayOffset, centralFrequencyOffsetList)
        minPulsewidth = min(acValues[0])
        maxPulsePeak = max(acValues[1])
        indexMinPulseWidth = acValues[0].index(minPulsewidth)
        indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
        centralFreqOffsetMinPulsewidth = centralFrequencyOffsetList[indexMinPulseWidth]
        centralFreqOffsetMaxPulsePeak = centralFrequencyOffsetList[indexMaxPulsePeak]
        print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(centralFreqOffsetMinPulsewidth) + " [axial modes]")
        print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(centralFreqOffsetMaxPulsePeak) + " [axial modes]")
        return (acValues, centralFrequencyOffsetList, minPulsewidth, maxPulsePeak, centralFreqOffsetMinPulsewidth, centralFreqOffsetMaxPulsePeak)


if __name__ == "__main__":
    
    # Take Original EOM Comb
    fileNameOsa = 'DCF-MLL-Test.csv'
    masterOfcMngr = MllOpticalFrequencyCombManager()
    masterOfcMngr.setOfcAllPass()
    masterOfcMngr.saveOsaSpectrum(fileNameOsa, 'A')
#     Save harmonic OFC master
    fileNameShg = 'DCF_MLL_PIC_'
    tauPerNm = 0
    cubicDispersionPs3 = 0.0
    centralFrequencyOffset = 0
    masterOfcMngr.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, tauPerNm, cubicDispersionPs3, centralFrequencyOffset)
    (opticalBandwidthNm, transformLimitedPulsePs) = masterOfcMngr.calculate_bandwidth_and_tlp()

    initialDispersion = -10
    endDispersion = 10
    numberOfSamples = 101
    (acValues, tauPerNmList, minPulsewidth, maxPulsePeak, dispersionMinPulsewidth, dispersionMaxPulsePeak) = masterOfcMngr.sweep_quadratic_dispersion_parameter(fileNameOsa, initialDispersion, endDispersion, numberOfSamples, cubicDispersionPs3, centralFrequencyOffset)

    initialCubicDispersionPs3 = -1
    endCubicDispersionPs3 = 1
    numberOfSamples = 101
    (acValues2, cubicDispersionPs3List, minPulsewidth2, maxPulsePeak2, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak) = masterOfcMngr.sweep_cubic_dispersion_parameter(fileNameOsa, dispersionMinPulsewidth, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples, centralFrequencyOffset)
    
    initialCentralFrequencyOffset = -20
    endCentralFrequencyOffset = 20
    numberOfSamples = 3
    (acValues3, centralFrequencyOffsetList, minPulsewidth3, maxPulsePeak3, centralFreqOffsetMinPulsewidth, centralFreqOffsetMaxPulsePeak) = masterOfcMngr.sweep_central_frequancy_offset_dispersion_parameter(fileNameOsa, dispersionMinPulsewidth, cubicDispersionMinPulsewidth, initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples)

    print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(dispersionMinPulsewidth) + " [ps^3]")
    print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(dispersionMaxPulsePeak) + " [ps^3]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], tauPerNmList, "ps/nm")
    
    print("Min pulsewidth: " + str(minPulsewidth2) + " [ps] at: " + str(cubicDispersionMinPulsewidth) + " [ps^3]")
    print("Max pulse peak: " + str(maxPulsePeak2) + " [V] at: " + str(cubicDispersionMaxPulsePeak) + " [ps^3]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues2[0], cubicDispersionPs3List, "ps^3")
    
    print("Min pulsewidth: " + str(minPulsewidth3) + " [ps] at: " + str(centralFreqOffsetMinPulsewidth) + " [axial modes]")
    print("Max pulse peak: " + str(maxPulsePeak3) + " [V] at: " + str(centralFreqOffsetMaxPulsePeak) + " [axial modes]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues3[0], centralFrequencyOffsetList, "axial-modes")
        
    masterOfcMngr.setDispersionProfile(centralFreqOffsetMinPulsewidth, dispersionMinPulsewidth, cubicDispersionMinPulsewidth)        
    
    