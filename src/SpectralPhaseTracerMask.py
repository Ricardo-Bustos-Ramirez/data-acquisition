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
        time.sleep(10)
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

    def createLinearChirpAndCubicPhaseMask(self, fileNameOsa, tauPerNm, cubicConstant):
        # Read file and create mask array
        fileName = self.filePathOsa + '\\' + fileNameOsa
        self.maskCalc.set_optical_spectrum_from_file(fileName)
        profileName = str(tauPerNm) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
        self.maskCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(tauPerNm, cubicConstant, self.filePathWS, profileName)

    def setOfcBlocked(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def setOfcAllPass(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.pass_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadDispersionProfile(self, tauPerNm, cubicConstant):
        fileProfile = self.filePathWS + '\\' + str(tauPerNm) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
        profileName = str(tauPerNm) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setDispersionProfile(self, tauPerNm, cubicConstant):
        profileName = str(tauPerNm) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
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
        

if __name__ == "__main__":
    
    # Take Original EOM Comb
#    fileName = 'OEW_SOA-max_FPE_EDFAmax_1PM-IM-29.9286GHz-10dBm-0.31V_SOA_150mA_EDFA_350mW_1000mSMF_100m-HNLF-ND_Att-30mW_WS' + '.csv
#    fileName = 'Test-OEW_SOA-max_FPE_EDFAmax_1PM-IM-30GHz-10dBm-1.31V_SOA_EDFA_1200mW_1000mSMF_100m-HNLF-ND_Att-100mW_WS' + '.csv'
    fileNameOsa = 'DCF-MLL-Test.csv'
    masterOfcMngr = MllOpticalFrequencyCombManager()
    masterOfcMngr.setOfcAllPass()
    masterOfcMngr.saveOsaSpectrum(fileNameOsa, 'A')
    
#     Save harmonic OFC master
    fileBaseline = 'DCF_MLL_PIC_'

    initialDispersion = -10
    endDispersion = 10
    tauPerNmArray = np.linspace(initialDispersion, endDispersion, 101)
    tauPerNmList = [round(x,2) for x in tauPerNmArray]
    print(tauPerNmList)
#    input("Press Enter to continue...")
    fileArray = []
    cubicConstant = 0
    for tauPerNm in tauPerNmList:
        print('OFC Dispersion: ' + str(tauPerNm) + ' ps/nm, ' + str(cubicConstant) + ' [rad]^3.')
#        input("Press Enter to continue...")
        ofcFileName = fileBaseline + str(tauPerNm) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
        masterOfcMngr.createLinearChirpAndCubicPhaseMask(fileNameOsa, tauPerNm, cubicConstant)
        masterOfcMngr.loadDispersionProfile(tauPerNm, cubicConstant)
        masterOfcMngr.setDispersionProfile(tauPerNm, cubicConstant)
#        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'A')
        masterOfcMngr.saveTdsSpectrum(ofcFileName)
        fileArray.append(ofcFileName)        
    acValues = masterOfcMngr.calculate_dispersion_and_pulse_width(fileArray, tauPerNmList)
    minPulsewidth = min(acValues[0])
    maxPulsePeak = max(acValues[1])
    indexMinPulseWidth = acValues[0].index(minPulsewidth)
    indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
    dispersionMinPulsewidth = tauPerNmList[indexMinPulseWidth]
    dispersionMaxPulsePeak = tauPerNmList[indexMaxPulsePeak]
    print("Min pulsewidth: " + str(minPulsewidth) + " ps at: " + str(dispersionMinPulsewidth) + "ps/nm")
    print("Max pulse peak: " + str(maxPulsePeak) + " V at: " + str(dispersionMaxPulsePeak) + "ps/nm")
    (opticalBandwidthNm, transformLimitedPulsePs) = masterOfcMngr.calculate_bandwidth_and_tlp()
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], tauPerNmList, "ps/nm")

#    masterOfcMngr.closePorts()
    
#    masterOfcMngr.setDispersionProfile(str(dispersionMinPulsewidth))

    initialCubicConstant = -10
    endCubicConstant = 10
    cubiConstantArray = np.linspace(initialCubicConstant, endCubicConstant, 101)
    cubicConstantList = [round(x,2)*1e-6 for x in cubiConstantArray]
    print(cubicConstantList)
#    input("Press Enter to continue...")
    fileArrayCubic = []
    for cubicConstant in cubicConstantList:
        print('OFC Dispersion: '  + str(dispersionMinPulsewidth) + ' ps/nm, ' + str(cubicConstant) + ' [rad]^3')
#        input("Press Enter to continue...")
        ofcFileName = fileBaseline + str(dispersionMinPulsewidth) + 'ps-nm' + str(cubicConstant) + 'rad.wsp'
        masterOfcMngr.createLinearChirpAndCubicPhaseMask(fileNameOsa, dispersionMinPulsewidth, cubicConstant)
        masterOfcMngr.loadDispersionProfile(dispersionMinPulsewidth, cubicConstant)
        masterOfcMngr.setDispersionProfile(dispersionMinPulsewidth, cubicConstant)
#        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'A')
        masterOfcMngr.saveTdsSpectrum(ofcFileName)
        fileArrayCubic.append(ofcFileName)
    acValues2 = masterOfcMngr.calculate_dispersion_and_pulse_width(fileArrayCubic, cubicConstantList)
    minPulsewidth2 = min(acValues2[0])
    maxPulsePeak2 = max(acValues2[1])
    indexMinPulseWidth2 = acValues2[0].index(minPulsewidth2)
    indexMaxPulsePeak2 = acValues2[1].index(maxPulsePeak2)
    cubicPhaseMinPulsewidth = cubicConstantList[indexMinPulseWidth2]
    cubicPhaseMaxPulsePeak = cubicConstantList[indexMaxPulsePeak2]

    print("Min pulsewidth: " + str(minPulsewidth) + " ps at: " + str(dispersionMinPulsewidth) + " ps/nm")
    print("Max pulse peak: " + str(maxPulsePeak) + " V at: " + str(dispersionMaxPulsePeak) + " ps/nm")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], tauPerNmList, "ps/nm")
    
    print("Min pulsewidth: " + str(minPulsewidth2) + " ps at: " + str(cubicPhaseMinPulsewidth) + " [rad]^3")
    print("Max pulse peak: " + str(maxPulsePeak2) + " V at: " + str(cubicPhaseMaxPulsePeak) + " [rad]^3")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues2[0], cubicConstantList, "rad^3")
        
    masterOfcMngr.setDispersionProfile(dispersionMinPulsewidth, cubicPhaseMinPulsewidth)
    
    
    
    