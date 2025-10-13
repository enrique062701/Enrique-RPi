import os
import numpy as np
import pandas as pd
from tm_devices import DeviceManager
from epics import PV, caget, caput
from tm_data_types import read_file, AnalogWaveform, DigitalWaveform
import time
import os

'''
Adding the with Open statement
'''
caput('MSO24:Armed', 1)
####If this gets removed, its back to the original file
with DeviceManager(verbose=False) as dm:
    #dm = DeviceManager(verbose=False)
    dm.visa_library = "@py"
    scope = dm.add_scope("10.97.106.91") #Add scope here
    #Designated paths for each
    local_pi_folder = "/home/phoenix/shared/" #Samba shared folder on pu
    scope_mount_path = "Z:/waveform" #Reference folder on the scope to save
    start_time_true = time.time()
    # Define a unique filename
    save_path = f"{scope_mount_path}.wfm"
    prev_state = None

    '''
    Script seems to work and not be delayed. It is now synced. Only issue is that sometimes it can not read the first
    file.
    '''
    caput('MSO24:TriggerLED_RBV', 0)
    caput('MSO24:WaitingForTrigger', 1)
    scope.write("ACQuire:STOPAfter RUNStop")
    scope.write('ACQUIRE:STATE ON')
    scope.write("HORizontal:RECordlength 10000")
    #scope.write(f'SAVE:WAVEFORM ALL, "{save_path}"') #This is to initialize the files at first in case they dont exist in the drive

    print('Initializing the files', end = '\r')
    while True:
        try:
            armed = caget('MSO24:Armed')
            single = caget('MSO24:SingleTrigger')
            print('Trigger is unarmed, arm trigger', end = '\r')
            
            if armed == 1:
                start_time = time.time()
                trigger = scope.query('TRIGger:STATE?')
                print('Trigger has been armed, waiting for trigger.', end = '\r')

                if trigger != 'READY':
                    scope.write(f'SAVE:WAVEFORM ALL, "{save_path}"')
                    channels = scope.query('SELECT?').strip().split(';')  
                    channels = [int(ch) for ch in channels]  # Convert to list of integers [1,1,0,1]
                    files = []
                    for i, ch in enumerate(channels):
                        if ch == 1:
                            file = f'/home/phoenix/shared/waveform_ch{i+1}.wfm'
                            files.append(file)
                    time.sleep(0.3)
                    
                    
                    #NOTE:If the channel is turned off before a trigger occurs, it can accidently save a file that does not get registered as an active channel and vice versa
                    timeout = 0.1 
                    while not all(os.path.exists(file) for file in files):
                        if time.time() > timeout:
                            print('Files were not found, will assume files exist and continue with the script')
                            continue
                        print('Waiting for files', end = '\r')
                    print(f'It took {time.time() - start_time} for the files to save in the shared drive')
                    
                    
                    volt_div = []
                    for ch in range(1, 5): #Potential error if file does not exist
                        file_path = f'/home/phoenix/shared/waveform_ch{ch}.wfm'
                        if channels[ch-1] == 1:  #Channel is ON   --Need to make it so that it can detect the size of the orignal data instead of manually putting zerros
                            if os.path.exists(file_path):
                                ch_data = read_file(file_path)
                                voltage = ch_data.normalized_vertical_values
                                #div = scope.query('{ch}:SCALE?') #This does not work in single mode 
                                #volt_div.append(div)
                                print(np.size(voltage))
                                caput(f'MSO24:Ch{ch}:Trace', voltage) #Would it be better to append the data and upload to epics outside loop or upload directly
                                #print(voltage)
                                if ch == 1:
                                    caput('MSO24:Time', ch_data.normalized_horizontal_values)
                        else:  # Channel is OFF
                            print(f"Channel {ch} is OFF. Sending zeros instead.")
                            array = 10000
                            zero_array = np.zeros(array)  # Adjust array size if needed #set this array to the same size
                            caput(f'MSO24:Ch{ch}:Trace', zero_array)
                            
                        
                    print(f'Total time to take data is: {time.time()-start_time}')
                    caput('MSO24:TriggerLED_RBV', 0)
                    caput('MSO24:WaitingForTrigger', 1)
                    
                    if single == 1:
                        '''
                        For some reason, EPICS does not respond to the 'caput' command because it does not unarm the scope at all. I dont know how
                        to fix this. I tried adding a delay to communicate with the scope. It aslo keeps on triggering and acquiring data.
                        '''
                        scope.query("ACQuire:STOPAfter SEQ") #Sets the scope to single mode so that no more traces are read
                        print('Scope in single mode', end = '\r')
                        caput('MSO24:Armed', 0)
                        time.sleep(0.05)
                        
                    for file in files:
                        os.remove(file)
                        
                    scope.write("ACQuire:STOPAfter RUNStop") #This command is to let it be in continous mode to read data
                    scope.write("ACQUIRE:STATE ON")
                    
                    
                    
        except Exception as e:
            print(f'Error that occured is {e}')
            #time.sleep(0.3)
            #break


        except KeyboardInterrupt:
            break



