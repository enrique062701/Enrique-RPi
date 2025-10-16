'''
Enrique Cisneros Jr 11/14/24

This script runs in the background and sleeps while the 'while' loop is true. Once it senses a trigger in the oscilliscope, it 
will then acquire and plot the data. This only works when the scope is in single shot. After it is done, the script sets it back to 
single shot mode. It can also be contolled by EPICS UI and take data at 1Hz repetition rate.
Backup in 'Trigger_response.py' 11/14/24

'''
import numpy as np
from LeCroy_Scope import LeCroy_Scope
import time
from epics import caput, caget

# with scope = 
with LeCroy_Scope('10.97.106.92', verbose = True) as scope:

    #scope = LeCroy_Scope('10.97.106.92') #Enter IP of the scope
    start_time = time.time()

    scope.set_trigger_mode('SINGLE')
    caput('LeCroy:Armed', 1)
    caput('LeCroy:TriggerLED_RBV', 0)
    caput('LeCroy:WaitingForTrigger', 1)
    print('Trigger is automatically armed')

    message_printed = False
    disarm_start_time = None

    while True:
        try:
            armed = caget('LeCroy:Armed')
            #caput('LeCroy:TriggerLED_RBV', 0) 
            #caput('LeCroy:WaitingForTrigger', 1)
            single = caget('LeCroy:SingleTrigger') #For some reason when removing this, the scope tends to be much slower
        
       
            if armed == 1:
                print('Trigger has been armed.', end='\r')

                # with scpoe = 
                current_mode = scope.set_trigger_mode("")
                #data_points = scope.max_samples() --> For some reason this adds a huge delay to the scope and buffers a lot
                #zeros = np.zeros(data_points) #This is to get the maximum number of data points the scope recieves

                if current_mode[0:4] == 'STOP':
                    time1 = time.time()
                
                    caput('LeCroy:TriggerLED_RBV', 1) #Turn on the LED to signify it has been triggered
                    caput('LeCroy:WaitingForTrigger', 0)
           
                    traces = scope.displayed_traces()
                    channels = ['C1', 'C2', 'C3', 'C4']
                    data_list = []
                    volt_div = []

                    for tr in channels:
                        if tr in traces:
                            data = scope.acquire(tr)
                            data_list.append(data)
                            div = scope.vertical_scale(tr)
                            volt_div.append(div)
                        
                        else:
                            data_list.append(0) #Was trying to use the np.zeros method to append the zeros array but getting max samples adds huge delay
                            volt_div.append(0)
           
                    time_data = scope.time_array() 
                
                    T0 = time_data[0] #offset
                    dT = time_data[1] - T0 #deltaT
                    caput('LeCroy:T0', T0) 
                    caput('LeCroy:TimePerDivision', dT)
                
                    zeros = np.zeros(len(time_data)) 
                
                    caput('LeCroy:Time', time_data)
                    print(volt_div)
                    print(type(volt_div))
                    for i, ch in enumerate(channels):                    
                        caput(f'LeCroy:Ch{i+1}:VoltsPerDivision',volt_div[i] if ch in traces else 0)                     
                        caput(f'LeCroy:Ch{i+1}:Trace', data_list[i] if ch in traces else zeros)
                    time2 = time.time() 
                    #The bottom chunk of the code sets it back to single shot after uploading to EPICS instead of waiting for the script to close
                
                    if single == 1:
                        print('In single shot')
                        caput('LeCroy:Armed', 0)
                    scope.set_trigger_mode('SINGLE')
                
                    print(f'Total time is: {time2 - time1}')
                    caput('LeCroy:TriggerLED_RBV', 0) 
                    caput('LeCroy:WaitingForTrigger', 1)
            
            else:
                if not message_printed:
                    print('Trigger is disarmed or in single mode. Check EPICS UI.')
                    disarm_start_time = time.time()
                    message_printed = True
                elapsed_time = time.time() - disarm_start_time

                print(f'Disarm for {elapsed_time:.2f} seconds', end = '\r')

            time.sleep(0.01)


        except KeyboardInterrupt:
            print('Program has been interupted')
            break
            #Another error when scope not on network: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.

        except Exception as e:
            '''
            When the scope is disconnected from the Network you get: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.
            Once its connected back to the network, it takes approximately a minute to start running and taking data again.

            When disconnected from the power: 'Client' object has no attribute '_socket'.
            In order to start taking data, you must reset the script.
            '''
            if "'Client' object has no attribute '_socket'" in str(e):
                while True:
                    try:
                        scope = LeCroy_Scope('10.97.106.92') 
                        scope.set_trigger_mode('SINGLE')
                        caput('LeCroy:Armed',  1)
                        print('Reconnected')
                        break
                    except Exception as retry_error:
                        print('Failed to reconnect: {retry_error}. Retrying in 5 seconds')
                        time.sleep(5)

            crash_time = time.time() ##This block stops the program if there is an error and tells you what went wrong
            print(f'The program has stopped due to: {e}. \n Total run time is {crash_time - start_time:.2f}')
        


    
      





