"""
This code will mimick the controller and try to send commands from it as well.
"""
import os
import can
import time
import epics
import csv
import numpy as np 

# Will not set the can port down

channel = 'can0'

controller_messages = [] # This will contain all the messages that the controller sends.









