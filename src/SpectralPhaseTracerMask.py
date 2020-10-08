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
from matplotlib import cm
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
#        self.osaManager.connect(self.osaGpibAddress)
        self.tdsManager.connect(self.tdsGpibAddress)
    
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
        self.osaManager.plot_waveform()

    def saveTdsSpectrum(self, fileName):
        self.tdsManager.connect(self.tdsGpibAddress)
        self.tdsManager.set_osc_state('STOP')
        print("TDS Stopped...")
        time.sleep(5)
        self.tdsManager.set_osc_state('RUN')
        print("TDS Running...")
        time.sleep(20)
        print("TDS Acquiring...")
        self.tdsManager.acquire_waveform()
        self.tdsManager.save_csv(self.filePathTds + '\\' + fileName)
#        self.osaManager.close()
        # Print captured spectrum
        self.tdsManager.plot_waveform()
        
    def plot_quadratic_and_cubic_nested_plot(self, quadraticDispersionPs2List, cubicDispersionPs3List, acValues2D3D, centralFrequencyOffset):
#        x = np.array(cubicDispersionPs3List)
#        y = np.array(quadraticDispersionPs2List)
        Z = np.array(acValues2D3D)
        # 3D plot
        """
        fig = plt.figure()
#        fig, ax = plt.subplots(figsize=(6,6))
        ax = fig.gca(projection='3d')
        X, Y = np.meshgrid(x, y)
        surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.set_xlabel('Cubic dispersion (ps^3)')
        ax.set_ylabel('Quadratic dispersion (ps^2)')
        ax.set_zlabel('Pulsewidth (ps)');
        plt.show()
        """
        # Annotated heatmap
        fig, ax = plt.subplots(figsize=(6,6))
        im = ax.imshow(Z)
        # Show all ticks
        ax.set_xticks(np.arange(len(cubicDispersionPs3List)))
        ax.set_yticks(np.arange(len(quadraticDispersionPs2List)))
        # label them with list entries
        ax.set_xticklabels(cubicDispersionPs3List)
        ax.set_yticklabels(quadraticDispersionPs2List)
        # Rotate tick labels and alignment
        plt.setp(ax.get_xticklabels(), rotation = 45, ha = "right", rotation_mode = "anchor")
        # Loop over data dimensions and create text annotations.
        for i in range(len(quadraticDispersionPs2List)):
            for j in range(len(cubicDispersionPs3List)):
                currentPulsewidth = round(Z[i, j], 3)
                text = ax.text(j, i, currentPulsewidth, ha = "center", va = "center", color = "w")
        ax.set_title("Pulsewidth in [ps] of D_{2} and D_{3}")
        fig.tight_layout()
        plt.show()
        
        # Calculate minimum pulsewidth and quadratic and cubic values for it.
        minPulsewidthList = []
        minCubicDispersionPs3List = []
        
        for i in range(len(quadraticDispersionPs2List)):
            localMinPulsewidth = min(acValues2D3D[i])
            minPulsewidthList.append(localMinPulsewidth)
            minCubicPulsewidthIndex = acValues2D3D[i].index(localMinPulsewidth)
            minCubicDispersionPs3List.append(cubicDispersionPs3List[minCubicPulsewidthIndex])
        minPulsewidth = min(minPulsewidthList)
        minQuadraticPulsewidthIndex = minPulsewidthList.index(minPulsewidth)
        minQuadraticDispersionPs2 = quadraticDispersionPs2List[minQuadraticPulsewidthIndex]
        minCubicDispersionPs3 = minCubicDispersionPs3List[minQuadraticPulsewidthIndex]
        
        print("Minimum pulsewidth: " + str(minPulsewidth) + " ps.")
        print("Minimum pulsewidth quadratic term: " + str(minQuadraticDispersionPs2) + " ps^2.")
        print("Minimum pulsewidth cubic term: " + str(minCubicDispersionPs3) + " ps^3.")
        
        return (im, text, minPulsewidth, minQuadraticDispersionPs2, minCubicDispersionPs3)
    
    def createLinearChirpAndCubicPhaseMask(self, fileNameOsa, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3):
        # Read file and create mask array
        fileName = self.filePathOsa + '\\' + fileNameOsa
        self.maskCalc.set_optical_spectrum_from_file(fileName)
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(quadraticDispersionPs2) + 'ps2' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.maskCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, self.filePathWS, profileName)

    def createModifiedPhaseMaskFromCurrentMask(self, axialModeOffset, spectralPhaseDelta):
        profileName = 'current' + str(axialModeOffset) + 'AxMo' + str(spectralPhaseDelta) + 'rad.wsp'
        self.maskCalc.set_modified_spectral_phase_mask_from_waveshaper_spectral_phase(axialModeOffset, spectralPhaseDelta, self.filePathWS, profileName)

    def setOfcBlocked(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def setOfcAllPass(self):
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.pass_all()
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadDispersionProfile(self, centralFrequencyOffset, quadraticDispersionPs2, cubicDispersionPs3):
        fileProfile = self.filePathWS + '\\' + str(centralFrequencyOffset) + 'AxMo' + str(quadraticDispersionPs2) + 'ps2' + str(cubicDispersionPs3) + 'ps3.wsp'
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(quadraticDispersionPs2) + 'ps2' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setDispersionProfile(self, centralFrequencyOffset, quadraticDispersionPs2, cubicDispersionPs3):
        profileName = str(centralFrequencyOffset) + 'AxMo' + str(quadraticDispersionPs2) + 'ps2' + str(cubicDispersionPs3) + 'ps3.wsp'
        self.wvmngr.connect_to_waveshaper()
        self.wvmngr.block_all()
        self.wvmngr.load_profile_to_waveshaper(profileName)
        self.wvmngr.disconnect_from_waveshaper()
    
    def loadModifiedDispersionProfile(self, axialModeOffset, spectralPhaseDelta):
        fileProfile = self.filePathWS + '\\' + 'current' + str(axialModeOffset) + 'AxMo' + str(spectralPhaseDelta) + 'rad.wsp'
        profileName = 'current' + str(axialModeOffset) + 'AxMo' + str(spectralPhaseDelta) + 'rad.wsp'
        self.wvmngr.load_profile_from_file(fileProfile, profileName)

    def setModifiedDispersionProfile(self, axialModeOffset, spectralPhaseDelta):
        profileName = 'current' + str(axialModeOffset) + 'AxMo' + str(spectralPhaseDelta) + 'rad.wsp'
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
    
    def calculate_dispersion_and_pulse_width(self, fileArray, dispersionParameter):
        filePath = self.filePathTds
        acValues = self.maskCalc.get_autocorrelation_values_from_file_array(fileArray, dispersionParameter, filePath)
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

    def set_dispersion_profile_and_save_autocorrelation_trace(self, fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3):
        print('OFC Dispersion: ' + str(quadraticDispersionPs2) + ' [ps^2], ' + str(cubicDispersionPs3) + ' [ps^3], offset from central frequency: ' + str(centralFrequencyOffset) + ' axial modes.')
#        input("Press Enter to continue...")
        shgAcFileName = fileNameShg + str(quadraticDispersionPs2) + 'ps2' + str(cubicDispersionPs3) + 'ps3' + str(centralFrequencyOffset) + 'offset.csv'

        self.createLinearChirpAndCubicPhaseMask(fileNameOsa, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3)
        self.loadDispersionProfile(centralFrequencyOffset, quadraticDispersionPs2, cubicDispersionPs3)
        self.setDispersionProfile(centralFrequencyOffset, quadraticDispersionPs2, cubicDispersionPs3)
#        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'A')
        self.saveTdsSpectrum(shgAcFileName)
        return shgAcFileName
    
    def set_modified_dispersion_profile_and_save_autocorrelation_trace(self, fileNameShg, axialModeOffset, spectralPhaseDelta):
        """
        The method starts from the current spectral phase mask applied in the waveshaper by method:
        + set_dispersion_profile_and_save_autocorrelation_trace
            + createLinearChirpAndCubicPhaseMask
                + maskCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum
                    + maskCalc.set_waveshaper_spectral_phase
        Or this method through the following path:
        + set_modified_dispersion_profile_and_save_autocorrelation_trace
            + createModifiedPhaseMaskFromCurrentMask
                + maskCalc.set_modified_spectral_phase_mask_from_waveshaper_spectral_phase
                    + maskCalc.set_waveshaper_spectral_phase
        """
        print('OFC axial mode offset: ' + str(axialModeOffset) + ', spectral phase delta: ' + str(spectralPhaseDelta) + ' [rad].')
#        input("Press Enter to continue...")
        shgAcFileName = fileNameShg + 'modified' + str(axialModeOffset) + 'ax-mod' + str(spectralPhaseDelta) + 'rad.csv'
        self.createModifiedPhaseMaskFromCurrentMask(axialModeOffset, spectralPhaseDelta)
        self.loadModifiedDispersionProfile(self, axialModeOffset, spectralPhaseDelta)
        self.setModifiedDispersionProfile(axialModeOffset, spectralPhaseDelta)
#        masterOfcMngr.saveOsaSpectrum(ofcFileName, 'A')
        self.saveTdsSpectrum(shgAcFileName)
        return shgAcFileName
    
    def sweep_quadratic_dispersion_parameter(self, fileNameOsa, tauPerNm, initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamples, cubicDispersionPs3, centralFrequencyOffset):
        quadraticDispersionPs2Array = np.linspace(initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamples)
        quadraticDispersionPs2List = [round(x,3) for x in quadraticDispersionPs2Array]
        print(quadraticDispersionPs2List)
#        input("Press Enter to continue...")
        fileArrayQuadratic = []
        for quadraticDispersionPs2 in quadraticDispersionPs2List:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3)
            fileArrayQuadratic.append(shgAcFileName)     
        acValues = self.calculate_dispersion_and_pulse_width(fileArrayQuadratic, quadraticDispersionPs2List)
        minPulsewidth = min(acValues[0])
        maxPulsePeak = max(acValues[1])
        indexMinPulseWidth = acValues[0].index(minPulsewidth)
        indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
        quadraticDispersionMinPulsewidth = quadraticDispersionPs2List[indexMinPulseWidth]
        quadraticDispersionMaxPulsePeak = quadraticDispersionPs2List[indexMaxPulsePeak]
        print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(quadraticDispersionMinPulsewidth) + "ps^2")
        print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(quadraticDispersionMaxPulsePeak) + "ps^2")
        return (acValues, quadraticDispersionPs2List, minPulsewidth, maxPulsePeak, quadraticDispersionMinPulsewidth, quadraticDispersionMaxPulsePeak)

    def sweep_cubic_dispersion_parameter(self, fileNameOsa, tauPerNm, quadraticDispersionPs2, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples, centralFrequencyOffset):
        cubiConstantArray = np.linspace(initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples)
        cubicDispersionPs3List = [round(x,4) for x in cubiConstantArray]
        print(cubicDispersionPs3List)
#        input("Press Enter to continue...")
        fileArrayCubic = []
        for cubicDispersionPs3 in cubicDispersionPs3List:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3)
            fileArrayCubic.append(shgAcFileName)     
        acValues = self.calculate_dispersion_and_pulse_width(fileArrayCubic, cubicDispersionPs3List)
        minPulsewidth = min(acValues[0])
        maxPulsePeak = max(acValues[1])
        indexMinPulseWidth = acValues[0].index(minPulsewidth)
        indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
        cubicDispersionMinPulsewidth = cubicDispersionPs3List[indexMinPulseWidth]
        cubicDispersionMaxPulsePeak = cubicDispersionPs3List[indexMaxPulsePeak]
        print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(cubicDispersionMinPulsewidth) + " [ps^3]")
        print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(cubicDispersionMaxPulsePeak) + " [ps^3]")
        return (acValues, cubicDispersionPs3List, minPulsewidth, maxPulsePeak, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak)

    def sweep_central_frequency_offset_dispersion_parameter(self, fileNameOsa, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples):
        centralFrequencyOffsetArray = np.linspace(initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples)
        centralFrequencyOffsetList = [int(x) for x in centralFrequencyOffsetArray]
        print(centralFrequencyOffsetList)
#        input("Press Enter to continue...")
        fileArrayOffset = []
        for centralFrequencyOffset in centralFrequencyOffsetList:
            shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3)
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
    
    def sweep_axial_mode_quadratic_and_cubic_dispersion_parameter(self, fileNameOsa, tauPerNm, initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamplesQuadratic, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamplesCubic, initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamplesCentralFrequencyOffset):
        centralFrequencyOffsetArray = np.linspace(initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamplesCentralFrequencyOffset)
        centralFrequencyOffsetList = [int(x) for x in centralFrequencyOffsetArray]
        print(centralFrequencyOffsetList)
#        print(tauPerNmList)
#        input("Press Enter to continue...")
        minPulsewidthList = []
        minQuadraticDispersionPs2List = []
        minCubicDispersionPs3List = []
        for centralFrequencyOffset in centralFrequencyOffsetList:
            (acValues1, quadraticDispersionPs2List, minPulsewidth, maxPulsePeak, quadraticDispersionMinPulsewidth, quadraticDispersionMaxPulsePeak) = self.sweep_quadratic_dispersion_parameter(fileNameOsa, tauPerNm, initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamplesQuadratic, cubicDispersionPs3, centralFrequencyOffset)
            (acValues2, cubicDispersionPs3List, minPulsewidth, maxPulsePeak, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak) = self.sweep_cubic_dispersion_parameter(fileNameOsa, tauPerNm, quadraticDispersionMinPulsewidth, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamplesCubic, centralFrequencyOffset)
            minQuadraticDispersionPs2List.append(quadraticDispersionMinPulsewidth)
            minCubicDispersionPs3List.append(cubicDispersionMinPulsewidth) 
            minPulsewidthList.append(minPulsewidth)            
        x = np.array(centralFrequencyOffsetList)
        y1 = np.array(minQuadraticDispersionPs2List)
        y2 = np.array(minCubicDispersionPs3List)
        y3 = np.array(minPulsewidthList)
        
        plt.plot(x,y1)
        plt.xlabel('Central axual mode offset')
        plt.ylabel('Quadratic dispersion (ps^2)')        
        plt.show()
        plt.plot(x,y2)
        plt.xlabel('Central axual mode offset')
        plt.ylabel('Cubic dispersion (ps^3)')
        plt.show()
        plt.plot(x,y3)
        plt.xlabel('Central axual mode offset')
        plt.ylabel('Minimum pulsewidth (ps)')
        plt.show()        
        
        return (centralFrequencyOffsetList, minQuadraticDispersionPs2List, minCubicDispersionPs3List, minPulsewidthList)
    
    def sweep_quadratic_and_cubic_dispersion_parameter(self, fileNameOsa, tauPerNm, initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamplesQuadratic, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamplesCubic, centralFrequencyOffset):
        quadraticDispersionPs2Array = np.linspace(initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamplesQuadratic)
        quadraticDispersionPs2List = [round(x,3) for x in quadraticDispersionPs2Array]
#        print(tauPerNmList)
#        input("Press Enter to continue...")
        acValues2D3D = []
        for quadraticDispersionPs2 in quadraticDispersionPs2List:
            
            (acValues, cubicDispersionPs3List, minPulsewidth, maxPulsePeak, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak) = self.sweep_cubic_dispersion_parameter(fileNameOsa, tauPerNm, quadraticDispersionPs2, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamplesCubic, centralFrequencyOffset)
#            cubiConstantArray = np.linspace(initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamplesCubic)
#            cubicDispersionPs3List = [round(x,4) for x in cubiConstantArray]
#            print(cubicDispersionPs3List)
#            acValues1 = [x+tauPerNm for x in cubicDispersionPs3List]
#            acValues2 = [x-tauPerNm for x in cubicDispersionPs3List]
#            acValues = (acValues1, acValues2)
            acPulseWidthArray = acValues[0]
            acValues2D3D.append(acPulseWidthArray)     
        
        return (acValues2D3D, quadraticDispersionPs2List, cubicDispersionPs3List)
        
    
    def sweep_modified_spectral_phase_by_axial_mode(self, fileNameOsa, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, centralFrequencyOffset, initialAxialModeOffset, endAxialModeOffset, initSpectralPhaseDelta, endSpectralPhaseDelta, numberOfSamples):
        # Set initial frequency.
        shgAcFileName = self.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, centralFrequencyOffset, cubicDispersionPs3)
        # Check which axial modes we will sweep.    
        axialModeOffsetArray = np.arange(initialAxialModeOffset, endAxialModeOffset, 1)
        axialModeOffsetList = [int(x) for x in axialModeOffsetArray]
        # Check spectral phase delta
        spectralPhaseDeltaArray = np.linspace(initSpectralPhaseDelta, endSpectralPhaseDelta, numberOfSamples)
        spectralPhaseDeltaList = [round(x,3) for x in spectralPhaseDeltaArray]
        print(axialModeOffsetList)
        print(spectralPhaseDeltaList)
#        input("Press Enter to continue...")
        for axialModeOffset in axialModeOffsetList:
            fileArraySpectralPhaseDelta = []
            for spectralPhaseDelta in spectralPhaseDeltaList:
                shgAcFileName = self.set_modified_dispersion_profile_and_save_autocorrelation_trace(fileNameShg, axialModeOffset, spectralPhaseDelta)
                fileArraySpectralPhaseDelta.append(shgAcFileName)    
            acValues = self.calculate_dispersion_and_pulse_width(fileArraySpectralPhaseDelta, spectralPhaseDeltaList)
            minPulsewidth = min(acValues[0])
            maxPulsePeak = max(acValues[1])
            indexMinPulseWidth = acValues[0].index(minPulsewidth)
            indexMaxPulsePeak = acValues[1].index(maxPulsePeak)
            spectralPhaseDeltaMinPulsewidth = centralFrequencyOffsetList[indexMinPulseWidth]
            spectralPhaseDeltaMaxPulsePeak = centralFrequencyOffsetList[indexMaxPulsePeak]
            print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(spectralPhaseDeltaMinPulsewidth) + " [rad], in axial mode offset: " + str(axialModeOffset))
            print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(spectralPhaseDeltaMaxPulsePeak) + " [rad], in axial mode offset: " + str(axialModeOffset))
        optimizedSpectralPhase = [-x for x in self.maskCalc.get_waveshaper_spectral_phase()]
#        self.maskCalc.set_spectrum_combline_phase(optimizedSpectralPhase)
        self.maskCalc.plot_spectral_output()
        return optimizedSpectralPhase
    
    def show_spectral_phase_on_spectrum(self, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, fileNameOsa):
        self.maskCalc.set_quadratic_and_cubic_spectral_phase_mask_from_acquired_spectrum(centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3, self.filePathOsa, fileNameOsa)
        self.maskCalc.set_spectrum_combline_phase([-x for x in self.maskCalc.get_waveshaper_spectral_phase()])    
        (frequencyTHz, spectralOutputFrequency, comblineFrequency, comblineSpectrumFrequency, comblineSpectralPhase) = self.maskCalc.plot_spectral_output()
        return (frequencyTHz, spectralOutputFrequency, comblineFrequency, comblineSpectrumFrequency, comblineSpectralPhase)


if __name__ == "__main__":
    # Take Original EOM Comb
    fileNameOsa = 'DCF-MLL-Test.csv'
#    fileNameOsa = "Master-OFC-30GHz.csv"
    masterOfcMngr = MllOpticalFrequencyCombManager()
    
    masterOfcMngr.setOfcAllPass()
#    masterOfcMngr.saveOsaSpectrum(fileNameOsa, 'B')
#     Save harmonic OFC master
    fileNameShg = 'DCF_MLL_PIC_'
    tauPerNm = -0.12                 # ps/nm equivalent to compensate for 6.5 m of SMF (anomalous dispersion 18 ps/nm*km) of fiber after MLL-PIC.
    quadraticDispersionPs2 = 0.0
    cubicDispersionPs3 = 0.0
    centralFrequencyOffset = 0
    masterOfcMngr.set_dispersion_profile_and_save_autocorrelation_trace(fileNameOsa, fileNameShg, centralFrequencyOffset, tauPerNm, quadraticDispersionPs2, cubicDispersionPs3)
    (opticalBandwidthNm, transformLimitedPulsePs) = masterOfcMngr.calculate_bandwidth_and_tlp()
    
#    Serialized central frequency offset, quadratic and cubic spectral phase.
#    input("Press Enter to continue (ps^2) 1...")
    initialQuadraticDispersionPs2 = -20.0
    endQuadraticDispersionPs2 = 20.0
    numberOfSamples = 11
    (acValues, quadraticDispersionPs2List, minPulsewidth, maxPulsePeak, quadraticDispersionMinPulsewidth, quadraticDispersionMaxPulsePeak) = masterOfcMngr.sweep_quadratic_dispersion_parameter(fileNameOsa, tauPerNm, initialQuadraticDispersionPs2, endQuadraticDispersionPs2, numberOfSamples, cubicDispersionPs3, centralFrequencyOffset)
    
#    input("Press Enter to continue (ps^3) 1...")
    initialCubicDispersionPs3 = -20
    endCubicDispersionPs3 = 20
    numberOfSamples = 11
    (acValues2, cubicDispersionPs3List, minPulsewidth2, maxPulsePeak2, cubicDispersionMinPulsewidth, cubicDispersionMaxPulsePeak) = masterOfcMngr.sweep_cubic_dispersion_parameter(fileNameOsa, tauPerNm, quadraticDispersionMinPulsewidth, initialCubicDispersionPs3, endCubicDispersionPs3, numberOfSamples, centralFrequencyOffset)
    
#    input("Press Enter to continue (axial modes) 1...")
    initialCentralFrequencyOffset = -10
    endCentralFrequencyOffset = 10
    numberOfSamples = 11
    (acValues3, centralFrequencyOffsetList, minPulsewidth3, maxPulsePeak3, centralFreqOffsetMinPulsewidth, centralFreqOffsetMaxPulsePeak) = masterOfcMngr.sweep_central_frequency_offset_dispersion_parameter(fileNameOsa, tauPerNm, quadraticDispersionMinPulsewidth, cubicDispersionMinPulsewidth, initialCentralFrequencyOffset, endCentralFrequencyOffset, numberOfSamples)
    
    print("Min pulsewidth: " + str(minPulsewidth) + " [ps] at: " + str(quadraticDispersionMinPulsewidth) + " [ps^2]")
    print("Max pulse peak: " + str(maxPulsePeak) + " [V] at: " + str(quadraticDispersionMinPulsewidth) + " [ps^2]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues[0], quadraticDispersionPs2List, "ps^2")
    
    print("Min pulsewidth: " + str(minPulsewidth2) + " [ps] at: " + str(cubicDispersionMinPulsewidth) + " [ps^3]")
    print("Max pulse peak: " + str(maxPulsePeak2) + " [V] at: " + str(cubicDispersionMaxPulsePeak) + " [ps^3]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues2[0], cubicDispersionPs3List, "ps^3")
    
    print("Min pulsewidth: " + str(minPulsewidth3) + " [ps] at: " + str(centralFreqOffsetMinPulsewidth) + " [axial modes]")
    print("Max pulse peak: " + str(maxPulsePeak3) + " [V] at: " + str(centralFreqOffsetMaxPulsePeak) + " [axial modes]")
    masterOfcMngr.calculate_tlp_from_parameter_sweep(opticalBandwidthNm, transformLimitedPulsePs, acValues3[0], centralFrequencyOffsetList, "axial-modes")
    
    masterOfcMngr.setDispersionProfile(centralFreqOffsetMinPulsewidth, quadraticDispersionMinPulsewidth, cubicDispersionMinPulsewidth)
    masterOfcMngr.show_spectral_phase_on_spectrum(centralFreqOffsetMinPulsewidth, 0.0, quadraticDispersionMinPulsewidth, cubicDispersionMinPulsewidth, fileNameOsa)
#    masterOfcMngr.setDispersionProfile(0, quadraticDispersionMinPulsewidth, 0.0)
    
    """
#    Nested quadratic and cubic dispersion profiles.
    centralFrequencyOffset = -2
    (acValues2D3D, quadraticDispersionPs2List, cubicDispersionPs3List) = masterOfcMngr.sweep_quadratic_and_cubic_dispersion_parameter(fileNameOsa, tauPerNm, 0, 4, 11, -1, 1, 11, centralFrequencyOffset)
    (im, text, minPulsewidth, minQuadraticDispersionPs2, minCubicDispersionPs3) = masterOfcMngr.plot_quadratic_and_cubic_nested_plot(quadraticDispersionPs2List, cubicDispersionPs3List, acValues2D3D, centralFrequencyOffset)
    masterOfcMngr.setDispersionProfile(centralFrequencyOffset, minQuadraticDispersionPs2, minCubicDispersionPs3)
    masterOfcMngr.show_spectral_phase_on_spectrum(centralFrequencyOffset, 0.0, minQuadraticDispersionPs2, minCubicDispersionPs3, fileNameOsa)
    """
    """
#    Nested central frequency offset with serialized quadratic and cubic profiles.
    (centralFrequencyOffsetList, minQuadraticDispersionPs2List, minCubicDispersionPs3List, minPulsewidthList) = masterOfcMngr.sweep_axial_mode_quadratic_and_cubic_dispersion_parameter(fileNameOsa, tauPerNm, 0, 4, 101, -1, 1, 101, -10, 10, 11)
    minPulsewidth = min(minPulsewidthList)
    minPulsewidthIndex = minPulsewidthList.index(minPulsewidth)    
    print("Minimum pulsewidth: " + str(minPulsewidth) + " ps.")
    print("Minimum pulsewidth axial mode offset: " + str(centralFrequencyOffsetList[minPulsewidthIndex]) + "axial modes.")
    print("Minimum pulsewidth quadratic term: " + str(minQuadraticDispersionPs2List[minPulsewidthIndex]) + " ps^2.")
    print("Minimum pulsewidth cubic term: " + str(minCubicDispersionPs3List[minPulsewidthIndex]) + " ps^3.")    
    masterOfcMngr.setDispersionProfile(centralFrequencyOffsetList[minPulsewidthIndex], minQuadraticDispersionPs2List[minPulsewidthIndex], minCubicDispersionPs3List[minPulsewidthIndex])
    masterOfcMngr.show_spectral_phase_on_spectrum(centralFrequencyOffsetList[minPulsewidthIndex], 0.0, minQuadraticDispersionPs2List[minPulsewidthIndex], minCubicDispersionPs3List[minPulsewidthIndex], fileNameOsa)
    """