# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 12:36:00 2019

@author: ri679647
"""

# pip install -U pyvisa-py

#import RFSA
from src.OSA import OSA
from src.CSA import CSA
from src.TDS import TDS
from src.ElectricalSynthesizer import ElectricalSynthesizer
from src.RFSA import RFSA
import time
#import numpy as np
import datetime
import csv
import os

TDS_ACTIVE = False
OSA_ACTIVE = False
CSA_ACTIVE = False
RFSA_ACTIVE = False
PSG_ACTIVE = False

TESTING_MODE = False
SWEEP_SCOPE = False
INDEX_WRITE = False

fileNameHilMll = "092820-300GHz-RHIL-MLL-6226-Ch2-unlocked-compressed-400us"
fileNameMll = "092820-300GHz-PML-MLL-6226-Ch2-unlocked-compressed-400us"
fileNameOfc = "092820-300GHz-RHIL-OFC-unlocked-compressed-400us-3"
fileNameAdditionRFSA = "-1MHz"
#CAPTURE_STATUS = "HIL-MLL All"
#CAPTURE_STATUS = "HIL-MLL RFSA HR"
#CAPTURE_STATUS = "HIL-MLL RFSA 10 MHz"
CAPTURE_STATUS = "MLL All"
#CAPTURE_STATUS = "MLL RFSA HR"
#CAPTURE_STATUS = "MLL RFSA 10 MHz"
#CAPTURE_STATUS = "OFC All"
#CAPTURE_STATUS = "HIL-MLL Locking Power"
#CAPTURE_STATUS = "Test"


#def capture_mode_selector(captureStatus):
if CAPTURE_STATUS == "HIL-MLL All":
    # Used instruments
    TDS_ACTIVE = True
    OSA_ACTIVE = True
    RFSA_ACTIVE = True
    CSA_ACTIVE = True
    INDEX_WRITE = True
    # File names
    fileName = fileNameHilMll
    measuredDevice = "HIL-MLL"
    fileNameAdditionRFSA = '-1MHz'
elif CAPTURE_STATUS == "HIL-MLL RFSA HR":
    # Used instruments
    TDS_ACTIVE = False
    OSA_ACTIVE = False
    RFSA_ACTIVE = True
    INDEX_WRITE = False
    # File names
    fileName = fileNameHilMll
    measuredDevice = "HIL-MLL"
    fileNameAdditionRFSA = '-1MHz-HR'
elif CAPTURE_STATUS == "HIL-MLL RFSA 10 MHz":
    # Used instruments
    TDS_ACTIVE = False
    OSA_ACTIVE = False
    RFSA_ACTIVE = True
    INDEX_WRITE = False
    # File names
    fileName = fileNameHilMll
    measuredDevice = "HIL-MLL"
    fileNameAdditionRFSA = '-10MHz'
elif CAPTURE_STATUS == "MLL All":
    # Used instruments
    TDS_ACTIVE = True
    OSA_ACTIVE = True
    RFSA_ACTIVE = True
    CSA_ACTIVE = True
    INDEX_WRITE = True
    # File names
    fileName = fileNameMll
    measuredDevice = "MLL"
    fileNameAdditionRFSA = '-1MHz'
elif CAPTURE_STATUS == "MLL RFSA HR":
    # Used instruments
    TDS_ACTIVE = False
    OSA_ACTIVE = False
    RFSA_ACTIVE = True
    CSA_ACTIVE = False
    INDEX_WRITE = False
    # File names
    fileName = fileNameMll
    measuredDevice = "MLL"
    fileNameAdditionRFSA = '-1MHz-HR'
elif CAPTURE_STATUS == "MLL RFSA 10 MHz":
    # Used instruments
    TDS_ACTIVE = False
    OSA_ACTIVE = False
    RFSA_ACTIVE = True
    INDEX_WRITE = False
    # File names
    fileName = fileNameMll
    measuredDevice = "MLL"
    fileNameAdditionRFSA = '-10MHz'
elif CAPTURE_STATUS == "OFC All":
    # Used instruments
    TDS_ACTIVE = True
    OSA_ACTIVE = True
    RFSA_ACTIVE = False
    CSA_ACTIVE = True
    INDEX_WRITE = True
    # File names
    fileName = fileNameOfc
    measuredDevice = "OFC"
#    fileNameAdditionRFSA = '-AOM'
elif CAPTURE_STATUS == "HIL-MLL Locking Power":
    # Used instruments
    TDS_ACTIVE = False
    OSA_ACTIVE = True
    RFSA_ACTIVE = True
    CSA_ACTIVE = True
    INDEX_WRITE = True
    # File names
    measuredDevice = "HIL-MLL"
    pOfcInj = 55
    fileName = fileNameHilMll + '-P-' + str(pOfcInj) + 'uW'
    fileNameAdditionRFSA = '-40MHz'
else:
    # Used instruments
    TDS_ACTIVE = True
    OSA_ACTIVE = True
    CSA_ACTIVE = True
    RFSA_ACTIVE = True
    PSG_ACTIVE = False
    
    TESTING_MODE = True
    SWEEP_SCOPE = False
    INDEX_WRITE = False

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
        fileType = '.csv'
        rTec = 14       # Measured resistance of TEC for MLL-PIC (kOhm)
        iGain = 87.0    # Current in the gain section (mA)
        iPsNum = 2      # Phase shifter used.
        iPs = 0.0      # Current in asymmetric MZIs of DCF (PS3) that move the spectrum (mA)
        vSa = 3.79      # Reverse bias voltage in saturable absorber (V)
        vEam = 0.00     # Reverse bias voltage in intracavity EAM (V)
        ixSoa = 120.8   # Current in the external SOA (mA)
        pMllInj = 24.0    # Power measured in the monitor coupler (~10%) of the MLL-PIC injection locking port (uW)
        pMllOut = 0.93   # Power measured in the monitor coupler (~50%) of the autocorrelator EDFA of the MLL-PIC output port (uW)
        pOfcInj = 82.7  # Power measured in the monitor coupler (<50% )of the injected OFC power (uW)
        fRepSynth = 29.9391  # Driving frequency of the EOM comb that generates OFC (~3frep) in GHz
        mzmBias = 6.360 # COEO MZM bias.
    
    if INDEX_WRITE:
        if os.path.isfile(filePath + "\\" + "indexFile.csv") == False:
            with open(filePath + "\\" + "indexFile.csv", "w+", newline='') as fileWriter:
                csvWriter = csv.writer(fileWriter, delimiter = ',', lineterminator='\n')
                csvWriter.writerow(("File name", "Measured device", "TEC value (kOhm)", "Igain (mA)", "PS used", "Ips (mA)", "V_SA (V)", "V_EAM (V)", "IxSOA (mA)", "P_MLL-inj 10% (uW)", "P_MLL-out 1% (uW)", "P_OFC-inj 50% (uW)", "f_rep-EOM (GHz)", "COEO MZM bias (V)"))
    
        with open(filePath + "\\" + "indexFile.csv", "a", newline='') as fileWriter:
            csvWriter = csv.writer(fileWriter, delimiter = ',', lineterminator='\n')
            csvWriter.writerow((fileName, measuredDevice, rTec, iGain, iPsNum, iPs, vSa, vEam, ixSoa, pMllInj, pMllOut, pOfcInj, fRepSynth, mzmBias))
        
    if RFSA_ACTIVE:
        RFSA_8566B = RFSA()
        RFSA_8566B.connect('GPIB0::18::INSTR')
        RFSA_8566B.get_spectrum()
        fileSubPathRfsa = 'RFSA'
#        fileNameAdditionRFSA = '-1MHz'
#        fileNameAdditionRFSA = '-1MHz-HR'
#        fileNameAdditionRFSA = '-10MHz'
#        fileNameAdditionRFSA = '_AOM'
        RFSA_8566B.save_csv(filePath + '\\' + fileSubPathRfsa + '\\' + fileName + fileNameAdditionRFSA + fileType)
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
    
    if CSA_ACTIVE:
        CSA_8200 = CSA()
        CSA_8200.connect('GPIB0::4::INSTR')
        CSA_8200.acquire_waveform()
        fileSubPathCsa = 'CSA'
        fileNameAddition = ''
        CSA_8200.save_csv(filePath + '\\' + fileSubPathCsa + '\\' + fileName + fileNameAddition + fileType)
        CSA_8200.plot_waveform()
    
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
    
    