#This is trial #2 that will allow the scope to see which channels are active and which are not
import numpy as np
import os
import time
from tm_data_types import read_file, AnalogWaveform, DigitalWaveform
from tm_devices import DeviceManager
import epics

dm = DeviceManager(verbose=False)
dm.visa_library = "@py"
scope = dm.add_scope("10.97.106.117")

local_pi_folder = "/home/phoenix/shared/" 
scope_mount_path = r'Z:\shared' 
save_path = f"{scope_mount_path}.wfm"

base = float(scope.query("HORizontal:SCAle?"))
recordlength = float(scope.query('HORizontal:RECORDlength?'))
trigger_pos = float(scope.query('HORizontal:POSition?'))
scope_time = np.arange(recordlength) * base * 10 # - trigger_pos --> Add if needed

def decoded_waveform(data):
    '''
    Look at the old script for the function. Check in the scope pi and look for the same MSO file.
    '''
    pass

while True:
    try:
        start_time = time.time()
        trigger_status = scope.write("TRIGger:STATE?")
        if trigger_status == 'TRIGGER':
            channels = scope.write('SELECT?').strip.split(';')
            available = ["CH" + str(i+1) for i, val in enumerate(channels.split(";")[:4]) if val == '1']
            volts = []
            data = []

            for channels in available:
                volts.append(float(scope.query(f"{ch}:VOLts?")))
                scope.write(f"DATa:SOUrce {ch}")
                scope.write("DATa:ENCdg ASCIi")
                scope.write("DATA:START 1")
                scope.write(f"DATA:STOP {len(scope_time)}")

                raw = scope.query('CURVe?')  # Retrieve waveform data
                decoded = decode_waveform(raw)
                clean = np.array(decoded) / 25.6 * volts[-1]  # Use latest voltage
                data.append(clean)

            else:
                volts.append(0)
                data.append(np.zeros(len(scope_time)))



    except KeyboardInterrupt:
        break








