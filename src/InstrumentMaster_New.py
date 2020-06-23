# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 12:36:00 2019

@author: ri679647
"""

# pip install -U pyvisa-py

#import RFSA
from src.OSA import OSA
from src.DCA import DCA
from src.TDS import TDS
from src.ElectricalSynthesizer import ElectricalSynthesizer
from src.RFSA import RFSA
import time
#import numpy as np
import datetime
import csv
import os

TDS_ACTIVE = False
OSA_ACTIVE = True
DCA_ACTIVE = False
RFSA_ACTIVE = False
PSG_ACTIVE = False

TESTING_MODE = False
SWEEP_SCOPE = False
INDEX_WRITE = True

if __name__ == "__main__":

    now_ = datetime.datetime.now()
    timestamp = now_.strftime("%Y-%m-%d_%H-%M")
    if TESTING_MODE:
        filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Test files'
        fileName = 'Test_'
        fileType = '.csv'
    else:
#        filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\300 GHz EOM Comb\\Master OFC'
        filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\300 GHz EOM Comb\\HIL-MLL'
        fileName = '061820-30GHz-03'
        fileType = '.csv'
        measuredDevice = "OFC" # Can be HIL-MLL, OFC & MLL
        rTec = 15       # Measured resistance of TEC for MLL-PIC (kOhm)
        iGain = 99.1    # Current in the gain section (mA)
        iPsNum = 2      # Phase shifter used.
        iPs = 62.5      # Current in asymmetric MZIs of DCF (PS3) that move the spectrum (mA)
        vSa = 4.01      # Reverse bias voltage in saturable absorber (V)
        vEam = 0.13     # Reverse bias voltage in intracavity EAM (V)
        ixSoa = 102     # Current in the external SOA (mA)
        pMllInj = 6.94  # Power measured in the monitor coupler (~10%) of the MLL-PIC injection locking port (uW)
        pMllOut = 70   # Power measured in the monitor coupler (~50%) of the autocorrelator EDFA of the MLL-PIC output port (uW)
        pOfcInj = 3.96   # Power measured in the monitor coupler (<50% )of the injected OFC power (uW)
        fRepSynth = 29.9589  # Driving frequency of the EOM comb that generates OFC (~3frep) in GHz
    
    if INDEX_WRITE:    
        if os.path.isfile(filePath + "\\" + "indexFile.csv") == False:
            with open(filePath + "\\" + "indexFile.csv", "w+", newline='') as fileWriter:
                csvWriter = csv.writer(fileWriter, delimiter = ',', lineterminator='\n')
                csvWriter.writerow(("File name", "Measured device", "TEC value (kOhm)", "Igain (mA)", "PS used", "Ips (mA)", "V_SA (V)", "V_EAM (V)", "IxSOA (mA)", "P_MLL-inj 10% (uW)", "P_MLL-out 1% (uW)", "P_OFC-inj 50% (uW)", "f_rep-EOM (GHz)"))
    
        with open(filePath + "\\" + "indexFile.csv", "a", newline='') as fileWriter:
            csvWriter = csv.writer(fileWriter, delimiter = ',', lineterminator='\n')
            csvWriter.writerow((fileName, measuredDevice, rTec, iGain, iPsNum, iPs, vSa, vEam, ixSoa, pMllInj, pMllOut, pOfcInj, fRepSynth))
        
    if RFSA_ACTIVE:
        RFSA_8566B = RFSA()
        RFSA_8566B.connect('GPIB0::18::INSTR')
        RFSA_8566B.get_spectrum()
        fileSubPathRfsa = 'RFSA'
        fileNameAddition = '-1MHz'
#        fileNameAddition = '-1MHz-HR'
#        fileNameAddition = '-10MHz'
#        fileNameAddition = '_AOM'
        RFSA_8566B.save_csv(filePath + '\\' + fileSubPathRfsa + '\\' + fileName + fileNameAddition + fileType)
        RFSA_8566B.plot_waveform()
        RFSA_8566B.close()

    if PSG_ACTIVE:
        PSG = ElectricalSynthesizer()
        PSG.connect('GPIB0::19::INSTR')
        PSG.set_psg_frequency(7.501e9)
        freqEo = str(PSG.get_psg_frequency())
        powerEo = str(PSG.get_power_attenuation())
        print('f_eo = ' + freqEo + ' Hz, Pout= ' + powerEo + ' dB\n')
        PSG.set_psg_output_state('OFF')
        print(PSG.get_psg_output_state())
        PSG.close()
    
    if OSA_ACTIVE:    
        OSA_243A = OSA()
        OSA_243A.connect('GPIB0::27::INSTR')
        OSA_243A.grab_spectrum('B')
        fileSubPathOsa = 'OSA'
        fileNameAddition = ''
        OSA_243A.save_csv(filePath + '\\' + fileSubPathOsa + '\\' + fileName + fileNameAddition + fileType)
        OSA_243A.plot_waveform()
    
    if DCA_ACTIVE:
        DCA_89100C = DCA()
        DCA_89100C.connect('GPIB0::7::INSTR')
        DCA_89100C.acquire_waveform()
        fileSubPathDca = 'SHG'
        fileNameAddition = ''
        DCA_89100C.save_csv(filePath + '\\' + fileSubPathDca + '\\' + fileName + fileNameAddition + fileType)
        DCA_89100C.plot_waveform()
    
    if TDS_ACTIVE:
        TDS210 = TDS()
        TDS210.connect('GPIB0::5::INSTR')
        if SWEEP_SCOPE:
            TDS210.set_osc_state('STOP')
            print("TDS Stopped...")
            time.sleep(5)
            TDS210.set_osc_state('RUN')
            print("TDS Running...")
            time.sleep(5)
            print("TDS Acquiring...")
        TDS210.acquire_waveform()
        fileSubPathTds = 'SHG'
        fileNameAddition = ''
        TDS210.save_csv(filePath + '\\' + fileSubPathTds + '\\' + fileName + fileNameAddition + fileType)
        TDS210.plot_waveform()
        TDS210.close()
    
    