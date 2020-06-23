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
#from src.RFSA import RFSA
#import visa
import time
#import numpy as np
import datetime
import matplotlib.pyplot as plt

TDS_ACTIVE = False
OSA_ACTIVE = False
DCA_ACTIVE = False
RFSA_ACTIVE = False
TESTING_MODE = False

if __name__ == "__main__":

#    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Python Scripts\\Test files'
#    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\300 GHz EOM Comb\\Master OFC'
    filePath = 'H:\\Home\\UP\\Shared\\Ricardo\\Dual Tone Injection Locking\\300 GHz EOM Comb\\HIL-MLL'
    now_ = datetime.datetime.now()
    timestamp = now_.strftime("%Y-%m-%d_%H-%M")
    
    if 
    RFSA_8566B = RFSA()
    RFSA_8566B.connect('GPIB0::18::INSTR')
    RFSA_8566B.get_spectrum()
    fileSubPathRfsa = 'RFSA'
#    fileName = 'RFSA_' + 'Test_' + timestamp + '.csv '
    fileName = 'Waveform1-OFC-AOM-30GHz.csv'
    RFSA_8566B.save_csv(filePath + '\\' + fileSubPathRfsa + '\\' + fileName)
    RFSA_8566B.plot_waveform()
    RFSA_8566B.close()

    
#    PSG = ElectricalSynthesizer()
#    PSG.connect('GPIB0::19::INSTR')
#    PSG.set_psg_frequency(7.501e9)
#    freqEo = str(PSG.get_psg_frequency())
#    powerEo = str(PSG.get_power_attenuation())
#    print('f_eo = ' + freqEo + ' Hz, Pout= ' + powerEo + ' dB\n')
#    PSG.set_psg_output_state('OFF')
#    print(PSG.get_psg_output_state())
#    PSG.close()
    
    OSA_243A = OSA()
    OSA_243A.connect('GPIB0::27::INSTR')
    OSA_243A.grab_spectrum('B')
    fileSubPathOsa = 'OSA'
    fileName = 'OSA_' + 'Test_' + timestamp + '.csv '
    fileName = 'Waveform1-OFC-30GHz.csv'
    OSA_243A.save_csv(filePath + '\\' + fileSubPathOsa + '\\' + fileName)
    OSA_243A.plot_waveform()
#    
#    DCA_89100C = DCA()
#    DCA_89100C.connect('GPIB0::7::INSTR')
#    fileSubPathDca = 'DCA'
#    fileName  = 'DCA_' + 'Test_' + timestamp + '.csv '
#    DCA_89100C.acquire_waveform()
#    DCA_89100C.save_csv(filePath + '\\' + fileSubPathDca + '\\' + fileName)
#    DCA_89100C.plot_waveform()
#    
#    TDS210 = TDS()
#    TDS210.connect('GPIB0::5::INSTR')
#    fileSubPathTds = 'SHG'
##    TDS210.set_osc_state('STOP')
##    print("TDS Stopped...")
##    time.sleep(5)
##    TDS210.set_osc_state('RUN')
##    print("TDS Running...")
##    time.sleep(5)
##    print("TDS Acquiring...")
##    fileName  = 'TDS_' + 'Test_' + timestamp + '.csv '    
##    fileName = 'OE-Waves-FPE-PDH_EDFA-max_EOM-' + freqEo + 'Hz-' + powerEo + 'dBm_1km-SMF_100m-HNLF_Att-10mW_Span-100us.csv'
##    fileName = 'OEW_FPE_EDFA-max_EOM_1W_SMF_HNLF-ZD_WS_0.4psnm_30GHz_POL-100us-ND-EDFA.csv'
#    fileName = 'Waveform1-OFC-30GHz.csv'
#    TDS210.acquire_waveform()
#    TDS210.save_csv(filePath + '\\' + fileSubPathTds + '\\' + fileName)
#    TDS210.close()
#    TDS210.plot_waveform()
    
    