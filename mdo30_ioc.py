'''
This script will allow the scope to be controlled and set into single mode. Enrique 04/13/25
'''
import numpy as np
from tm_devices import DeviceManager
from epics import PV, caput, caget
import matplotlib.pyplot as plt
import os
import time
time1 = time.time()
dm = DeviceManager(verbose=False)
dm.visa_library = "@py"
scope = dm.add_scope("10.97.106.93")
print(f'Total time to open scope is: {time.time() - time1}')
'''
Use TRIGger:A:MODe? to find the current trigger mode
To change trigger modes:
'TRIGger:A:MODe SINGle
......          NORMal
'''

def read_data(raw):
    '''
    This function turns the raw binary data read from the scope and converts its to waveform data. Conversion to
    voltages will be done outside function because its dependent on the specific channel being read.
    The first 20 points of raw data: 
    b'#41000\xbd\xbc\xbd\xbe\...'
    raw[1]: Single digit character, 4 in this case, which tell you that the next 4 bytes (1000) is the 
    length of the dataset.
    data_len: This lets you know that the length is 1000 points long. The first part is ASCII which is why we use ".decode()"
    data: Calculates the starting position and tells you how the total length of the data and where to start
    waveform: Converts the data to readable data
    Works for any number of data points.
    '''
    header_len = int(chr(raw[1])) 
    data_len = int(raw[2:2 + header_len].decode())  
    data = raw[2 + header_len:2 + header_len + data_len] #Reading the data
    waveform = np.frombuffer(data, dtype=np.int8)
    return waveform
#Set scope to single initially
scope.write("ACQ:STATE ON")
caput('MDO30:Armed', 1)

while True:
    try:
        armed = caget('MDO30:Armed')
        #caput('MDO30:TrigerLED_RBV', 0)
        #caput('MDO30:WaitingForTrigger', 1)
        #time.sleep(0.01)        
        single = caget('MDO30:SingleTrigger')
        if armed == 1:
            scope.write("ACQ:STATE ON")

            start_time1 = time.time()
            #print('Trigger has been armed', end='\r')
            
            time_div = (scope.query("HORizontal:SCAle?")) #Time div
            sample_rate = float(scope.query("HORizontal:MAIn:SAMPLERate?"))
            record_length = int(scope.query("HORizontal:RECOrdlength?"))
            x_incr = 1 / sample_rate
            x_zero = 0 #Can be changed to where the axis starts
            time_array = np.arange(record_length) * x_incr + x_zero
            
            caput('MDO30:Time', time_array)
            caput('MDO30:TimePerDivision', time_div)
            single = caget('MDO30:SingleTrigger')
            trigger = scope.query('TRIGger:STATE?')
            #print(trigger)

            if trigger == 'TRIG':
                scope.write("ACQ:STATE OFF")
                #print('Scope has been Triggered', end = '\r')

                start_time = time.time()
                channels = ['CH1', 'CH2', 'CH3', 'CH4']
                select = scope.query("SELECT?")
                available = ["CH" + str(i+1) for i, val in enumerate(select.split(';')[:4]) if val == '1']
                Data = []
                volt_div = []
                for ch in channels:
                    if ch in available:
                        scope.write(f'DATA:SOURCE {ch}')
                        ymult = float(scope.query('WFMPRE:YMULT?'))
                        yoff = float(scope.query('WFMPRE:YOFF?'))
                        yzero = float(scope.query('WFMPRE:YZERO?'))
                        v_div = float(scope.query(f'{ch}:SCAle?'))
                        scope.write('CURVE?')
                        raw = scope.read_raw()
                        waveform = read_data(raw)
                        voltage = (waveform - yoff) * ymult + yzero
                        Data.append(voltage)
                    
                        volt_div.append(v_div)
                    else:
                        Data.append(np.zeros(int(record_length)))
                        volt_div.append(0)

                    
                for i, ch in enumerate(channels):
                    caput(f'MDO30:Ch{i+1}:Trace', Data[i])
                    caput(f'MDO30:Ch{i+1}:VoltsPerDivision', volt_div[i])
                
                print(f'Total time is {time.time() - start_time}')
                time.sleep(0.05)

               
                if single == 1:
                    print('Scope is in single mode', end = '\r')
                    scope.write("ACQ:STATE OFF")

                    caput('MDO30:Armed', 0)


                #Set it back to single mode to start acquiring again
                #scope.query('TRIGger:A:MODe SINGle')

    except KeyboardInterrupt:
        print('Program has been manually terminated')
        break





  