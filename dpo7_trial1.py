#This is a file for testing the dpo7 scope

import numpy as np
from tm_data_types import read_file, AnalogWaveform, DigitalWaveform
from tm_devices import DeviceManager
import os
from epics import PV, caget, caput
import matplotlib.pyplot as plt
import time

dm = DeviceManager(verbose=False)
dm.visa_library = "@py"
scope = dm.add_scope("10.97.106.117")

local_pi_folder = "/home/phoenix/shared/" 
scope_mount_path = r'Z:\shared' 
save_path = f"{scope_mount_path}.wfm"
'''
Look at the commands:
SAVEON:TRIGger
SAVEON:WAVEform
'''
#For now comment out the files if the channel is not active
files = ["/home/phoenix/shared/sharedCH1.wfm",
         "/home/phoenix/shared/sharedCH2.wfm",
         "/home/phoenix/shared/sharedCH3.wfm",
         "/home/phoenix/shared/sharedCH4.wfm"]

while True:
    try:
        start_time = time.time()
        trigger_status = scope.write("TRIGger:STATE?")
        if trigger_status == "TRIGGER":
            scope.write(f'SAVE:WAVEFORM ALL, "{scope_mount_path}"')
            while not all(os.path.exists(file) for file in files):
                print('Waiting for files')
            print(f'It took {time.time() - start_time} for the files to save in the shared drive')
            #Now reading the data and uploading to EPICS

            file_1 = files[0]
            ch_data1 = read_file(file_1)
            voltage1 = ch_data1.normalized_vertical_values
            time_1 = ch_data1.normalized_horizontal_values
            caput('DPO7:Ch1:Trace', voltage1)
            caput('DPO7:Time', time_1)

            file_2 = files[1]
            ch_data2 = read_file(file_2)
            voltage2 = ch_data2.normalized_vertical_values
            caput('DPO7:Ch2:Trace', voltage2)
            
            file_3 = files[2]
            ch_data3 = read_file(file_3)
            voltage3 = ch_data3.normalized_vertical_values
            caput('DPO7:Ch3:Trace')

            file_4 = files[3]
            ch_data4 = read_file(file_4)
            voltage4 = ch_data4.normalized_vertical_values

            for file in files:
                os.remove(file)
            print(f'Total time to save data is {time.time() - start_time:.3g} s')

    except KeyboardInterrupt:
        break


