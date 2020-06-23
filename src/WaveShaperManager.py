# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:51:22 2019

@author: ri679647
"""


from wsapi import *

class WaveShaperManager():
    def __init__(self, waveShaperName):
        self.fileConfig = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2019\\SN068806.wsconfig'
        self.waveShaperName = waveShaperName
        self.waveShaperProfile = []
        fileProfilePredefined = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\'
        self.waveShaperIndex = {'no_mask':-1}
        self.load_profile_from_file(fileProfilePredefined + 'BlockAll.wsp', 'BlockAll')
        self.load_profile_from_file(fileProfilePredefined + 'PassAll.wsp', 'PassAll')
    
    def connect_to_waveshaper(self):
        rc = ws_create_waveshaper(self.waveShaperName, self.fileConfig)
        if ws_get_result_description(rc).decode("utf-8") == 'success':
            print("WaveShaper configuration file found and WaveShaper name available.")
            rc = ws_open_waveshaper(self.waveShaperName)
            if ws_get_result_description(rc).decode("utf-8") == 'success':
                print("Connection to WaveShaper successfully stablished.")
            elif ws_get_result_description(rc).decode("utf-8") == 'waveshaper not found':
                print("WaveShaper object does not exist.")
            elif ws_get_result_description(rc).decode("utf-8") == 'open failed':
                print("Could not open the WaveShaper. Possible connection problem.")
            else:
                print("Could not open the WaveShaper. Unknown error")
        else:
            print("WaveShaper configuration file not found or WaveShaper name taken.")
    
    def load_profile_from_file(self, fileProfile, profileName):
        wspFile = open(fileProfile, 'r')
        self.waveShaperProfile.append(wspFile.read())
        wspFile.close()
        # Make tuple for accessing the waveshaper profile
        profileNumber = len(self.waveShaperProfile)
        self.waveShaperIndex.update({profileName: profileNumber - 1})
    
    def load_profile_to_waveshaper(self, profileName):
        rc = ws_load_profile(self.waveShaperName, self.waveShaperProfile[self.waveShaperIndex[profileName]])
        rcString = ws_get_result_description(rc).decode("utf-8")
        if rcString == "success":
            print("Profile successfully loaded to WaveShaper.")
        else:
            print("Error while loading profile to WaveShaper.")
            if rcString == "waveshaper not found":
                print("WaveShaper object does not exist.")
            elif rcString == "invalid port":
                print("Profile error. Port number is not valid.")
            elif rcString == "WS_INVALIDFREQ":
                print("Profile error. Frequency specified out of range.")
            elif rcString == "WS_INVALIDATTN":
                print("Profile error. Attenuation is not valid.")
            elif rcString == "WS_INVALIDSPACING":
                print("Profile error. Frequencies not incremented in 0.001 THz step.")
            elif rcString == "WS_NARROWBANDWIDTH":
                print("Profile error. Bandwidth of frequencies to the same port is less than 0.010 THz.")
            elif rcString == "WS_INVALIDPROFILE":
                print("Profile error. Other parsing error.")
            elif rcString == "WS_OPENFAILED":
                print("Could not open the WaveShaper. Possible connection problem.")
            elif rcString == "WS_WAVESHAPER_CMD_ERROR":
                print("Error response from WaveShaper. May be communication corruption.")
            else:
                print("Unknown error.")
    
    def block_all(self):
        self.load_profile_to_waveshaper('BlockAll')
    
    def pass_all(self):
        self.load_profile_to_waveshaper('PassAll')
        
    
    def disconnect_from_waveshaper(self):
        rc = ws_close_waveshaper(self.waveShaperName)
        if ws_get_result_description(rc).decode("utf-8") == 'success':
            print("WaveShaper disconnected successfully.")
            rc = ws_delete_waveshaper(self.waveShaperName)
            if ws_get_result_description(rc).decode("utf-8") == 'success':
                print("WaveShaper object successfully deleted.")
            elif ws_get_result_description(rc).decode("utf-8") == 'WaveShaper not found':
                print("WaveShaper object does not exist.")
        else:
            print("WaveShaper disconnection error. Waveshaper object does not exist.")
        

if __name__ == "__main__":
#    fileConfig = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2019\\SN010566.wsconfig'
#    rc = ws_create_waveshaper('ws_harmonic_master_ofc', fileConfig)
#    print('ws_create_waveshaper rc = ' + ws_get_result_description(rc).decode("utf-8"))
#    
#    # Read WSP profile
    fileProfile = 'C:\\Users\\ri679647\\Desktop\\Dual Tone IL Mask\\2019\\CW 0.5THz Python\\420GHz-Spacing.wsp'
#    WSPfile = open(fileProfile, 'r')
#    maskProfile = WSPfile.read()
#    
#    # Load profile to Waveshaper
#    rc = ws_load_profile('ws_harmonic_master_ofc', maskProfile)
#    print('ws_load_profile rc = ' + ws_get_result_description(rc).decode("utf-8"))
#    
#    # Delete Waveshaper instance
#    rc = ws_delete_waveshaper('ws_harmonic_master_ofc')
#    print('ws_delete_waveshaper rc = ' + ws_get_result_description(rc).decode("utf-8"))
    
    wvmngr = WaveShaperManager("ws1")
    wvmngr.connect_to_waveshaper()
    wvmngr.load_profile_from_file(fileProfile, '420GHz-Spacing')
    wvmngr.load_profile_to_waveshaper('420GHz-Spacing')
    wvmngr.pass_all()
    wvmngr.disconnect_from_waveshaper()

    
    
    
    