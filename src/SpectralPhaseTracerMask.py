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
    
    def createLinearChirpMask(self, fileNameOsa, tauPerNm):
        # Read file and create mask array
        fileName = self.filePathOsa + '\\' + fileNameOsa
        self.maskCalc.set_optical_spectrum_from_file(fileName)
        profileName = str(tauPerNm) + 'ps-nm.wsp'
        self.maskCalc.set_quadratic_spectral_phase_mask_from_acquired_spectrum(tauPerNm, self.filePathWS, profileName)

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


if __name__ == "__main__":
    
    # Take Original EOM Comb
#    fileName = 'OEW_SOA-max_FPE_EDFAmax_1PM-IM-29.9286GHz-10dBm-0.31V_SOA_150mA_EDFA_350mW_1000mSMF_100m-HNLF-ND_Att-30mW_WS' + '.csv
#    fileName = 'Test-OEW_SOA-max_FPE_EDFAmax_1PM-IM-30GHz-10dBm-1.31V_SOA_EDFA_1200mW_1000mSMF_100m-HNLF-ND_Att-100mW_WS' + '.csv'
    fileNameOsa = 'DCF-MLL-Test.csv'
    masterOfcMngr = MllOpticalFrequencyCombManager()
    masterOfcMngr.setOfcAllPass()
    masterOfcMngr.saveOsaSpectrum(fileNameOsa, 'A')
    
#     Save harmonic OFC master
    fileNameShg = 'DCF_MLL_PIC_'

    initialDispersion = 0
    endDispersion = 5
    tauPerNmArray = np.linspace(initialDispersion, endDispersion, 26)
    tauPerNmList = [round(x,2) for x in tauPerNmArray]
    print(tauPerNmList)
    input("Press Enter to continue...")
    fileArrayQuadratic = []
    cubicDispersionPs3 = 0.0
    centralFrequencyOffset = 0
    for tauPerNm in tauPerNmList:
        shgAcFileName = masterOfcMngr.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, cubicDispersionPs3)
        fileArrayQuadratic.append(shgAcFileName)        
    acValues = masterOfcMngr.calculate_dispersion_and_pulse_width(fileArrayQuadratic, tauPerNmList)
    minPulsewidth = min(acValues[0])
    maxPulsePeak = max(acValues[1])
    indexMinPulseWidth = acValues[0].index(minPulsewidth)
    indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
    dispersionMinPulsewidth = tauPerNmList[indexMinPulseWidth]
    dispersionMaxPulsePeak = tauPerNmList[indexMaxPulsePeak]
    print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(dispersionMinPulsewidth) + "ps/nm")
    print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(dispersionMaxPulsePeak) + "ps/nm")
    (opticalBandwidthNm, transformLimitedPulsePs) = masterOfcMngr.calculate_bandwidth_and_tlp()
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], tauPerNmList, "ps/nm")

#    masterOfcMngr.closePorts()
    
#    masterOfcMngr.setDispersionProfile(str(dispersionMinPulsewidth))

    initialCubicDispersionPs3 = -1
    endCubicDispersionPs3 = 1
    cubiConstantArray = np.linspace(initialCubicDispersionPs3, endCubicDispersionPs3, 101)
    cubicDispersionPs3List = [round(x,4) for x in cubiConstantArray]
    print(cubicDispersionPs3List)
    input("Press Enter to continue...")
    fileArrayCubic = []
    for cubicDispersionPs3 in cubicDispersionPs3List:
        shgAcFileName = masterOfcMngr.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, dispersionMinPulsewidth, cubicDispersionPs3)
        fileArrayCubic.append(shgAcFileName)
    acValues2 = masterOfcMngr.calculate_dispersion_and_pulse_width(fileArrayCubic, cubicDispersionPs3List)
    minPulsewidth2 = min(acValues2[0])
    maxPulsePeak2 = max(acValues2[1])
    indexMinPulseWidth2 = acValues2[0].index(minPulsewidth2)
    indexMaxPulsePeak2 = acValues2[1].index(maxPulsePeak2)
    cubicPhaseMinPulsewidth = cubicDispersionPs3List[indexMinPulseWidth2]
    cubicPhaseMaxPulsePeak = cubicDispersionPs3List[indexMaxPulsePeak2]

    print("Min pulsewidth: " + str(minPulsewidth2) + " [ps] at: " + str(cubicPhaseMinPulsewidth) + " [ps^3]")
    print("Max pulse peak: " + str(maxPulsePeak2) + " [V] at: " + str(cubicPhaseMaxPulsePeak) + " [ps^3]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues2[0], cubicDispersionPs3List, "ps^3")
        
    masterOfcMngr.setDispersionProfile(centralFrequencyOffset, dispersionMinPulsewidth, cubicPhaseMinPulsewidth)        
    
    initialCentralFrequencyOffset = -20
    endCentralFrequencyOffset = 20
    centralFreqOffsetArray = np.linspace(initialCentralFrequencyOffset, endCentralFrequencyOffset, 41)
    centralFreqOffsetList = [int(x) for x in centralFreqOffsetArray]
    print(centralFreqOffsetList)
    input("Press Enter to continue...")
    fileArrayOffset = []
    for centralFrequencyOffset in centralFreqOffsetList:
        shgAcFileName = masterOfcMngr.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, dispersionMinPulsewidth, cubicPhaseMinPulsewidth)
        fileArrayOffset.append(shgAcFileName)
    acValues3 = masterOfcMngr.calculate_dispersion_and_pulse_width(fileArrayOffset, centralFreqOffsetList)
    minPulsewidth3 = min(acValues3[0])
    maxPulsePeak3 = max(acValues3[1])
    indexMinPulseWidth3 = acValues3[0].index(minPulsewidth3)
    indexMaxPulsePeak3 = acValues3[1].index(maxPulsePeak3)
    centralFreqOffsetMinPulsewidth = centralFreqOffsetList[indexMinPulseWidth3]
    centralFreqOffsetMaxPulsePeak = centralFreqOffsetList[indexMaxPulsePeak3]

    print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(dispersionMinPulsewidth) + " [ps/nm]")
    print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(dispersionMaxPulsePeak) + " [ps/nm]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], tauPerNmList, "ps/nm")
    
    print("Min pulsewidth: " + str(minPulsewidth2) + " [ps] at: " + str(cubicPhaseMinPulsewidth) + " [ps^3]")
    print("Max pulse peak: " + str(maxPulsePeak2) + " [V] at: " + str(cubicPhaseMaxPulsePeak) + " [ps^3]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues2[0], cubicDispersionPs3List, "ps^3")
    
    print("Min pulsewidth: " + str(minPulsewidth3) + " [ps] at: " + str(centralFreqOffsetMinPulsewidth) + " [axial modes]")
    print("Max pulse peak: " + str(maxPulsePeak3) + " [V] at: " + str(centralFreqOffsetMaxPulsePeak) + " [axial modes]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues3[0], centralFreqOffsetList, "axial-modes")
        
    masterOfcMngr.setDispersionProfile(centralFreqOffsetMinPulsewidth, dispersionMinPulsewidth, cubicPhaseMinPulsewidth)        
    
    