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

    def setOfcBlocked(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def setOfcAllPass(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.pass_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadDispersionProfile(self, OfcDispersion):
        fileProfile = self.filePathWS + '\\' + OfcDispersion + 'ps-nm.wsp'
        profileName = OfcDispersion + 'ps-nm'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setDispersionProfile(self, OfcDispersion):
        profileName = OfcDispersion + 'ps-nm'
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.load_profile_to_waveshaper(profileName)
        self.wvmngr.disconnect_from_waveshaper()
    
    def closePorts(self):
        self.osaManager.close()
        self.tdsManager.close()
    
    def calculate_bandwidth_and_tlp(self):
        opticalBandwidth = self.maskCalc.get_optical_spectrum_bandwidth()
        return opticalBandwidth
    
    def calculate_dispersion_and_pulse_width(self, fileArray, tauPerNmArray):
        filePath = self.filePathTds
        acValues = self.maskCalc.get_autocorrelation_values_from_file_array(fileArray, tauPerNmArray, filePath)
        return acValues

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
    input("Press Enter to continue...")
#    tauPerNmArray = [-10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10]
#    tauPerNmArray = [-10, -5, 0, 5, 10]
    fileArray = []
    for tauPerNm in tauPerNmList:
        tauPerNmStr = str(tauPerNm)
        print('OFC Dispersion: ' + tauPerNmStr + ' ps/nm')
#        input("Press Enter to continue...")
        ofcFileName = fileBaseline + tauPerNmStr + 'ps-nm.csv'
        masterOfcMngr.createLinearChirpMask(fileNameOsa, tauPerNm)
        masterOfcMngr.loadDispersionProfile(tauPerNmStr)
        masterOfcMngr.setDispersionProfile(tauPerNmStr)
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
    (opticalBandwidth, transformLimitedPulsePs) = masterOfcMngr.calculate_bandwidth_and_tlp()
    print(opticalBandwidth, transformLimitedPulsePs)
    timesTlp = [x*0.7071/transformLimitedPulsePs for x in acValues[0]]
    plt.plot(tauPerNmList, timesTlp)
    plt.show()
#    masterOfcMngr.closePorts()
        

    
    
    
    