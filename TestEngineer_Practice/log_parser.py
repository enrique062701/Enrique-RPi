"""
This file will help clean data and log it. Will use argparse so that different files can be passed through this file
Enrique C.
"""
import numpy as np
import argparse
import os
import sys
import time

"""
Sample data:
[2025-10-05 12:45:02] INFO: Sensor A reading = 23.4
[2025-10-05 12:45:03] ERROR: Sensor B timeout
[2025-10-05 12:45:04] INFO: Sensor A reading = 23.5
[2025-10-05 12:45:05] WARNING: Sensor B recovered
[2025-10-05 12:45:06] INFO: Sensor A reading = 23.6

Spit out a dictionary:
{"INFO": 3, "WARNING": 1, "ERROR": 1}
"""

def parse_log(log_file):
    logs = {}
    with open(log_file, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue # Skip blank lines
        
            # Split at the brackets section
            time_part, rest = line.split(']', 1)
            timestamp = time_part.strip('[]').strip()

            level_part, message = rest.split(':', 1)
            level = level_part.strip()

            logs = ({
                'timestamp': timestamp,
                'level' : level,
                'message' : message.strip(),
            })

    print(logs)
    return logs

if __name__ == "__main__":
    # This will allow you to pass any file through the terminal to get the results.
    base_parser = argparse.ArgumentParser(add_help = False)
    base_parser.add_argument("function", nargs = "?", choices = ['parse_log'], default = 'parse_log')

    args, sub_args = base_parser.parse_known_args()
    function = args.function

    parser = argparse.ArgumentParser(
        prog = f"{os.path.basename(sys.argv[0])} {function}",
        description = f"Arguments for the {function}"
    )

    parser.add_argument('-a', help = "File name")
    args = parser.parse_args(sub_args)

    if function == "parse_log":
        parse_log(args.a)


 






