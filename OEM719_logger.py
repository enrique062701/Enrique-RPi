"""
This file will be the logger for the NovAtel OEM719.
Prompt:
Develop a Python application in a project to parse the provided "OEM719 Simulated Log.txt" data into a separate .csv
files for each distinct message type.
    - Script should capture data at a frequency of 1 Hz for a duration of 30 seconds.
    - parsing the "OEM719 Simulated Log.txt" file should begin from an offset of 1,000,000 bytes from the start of 
        the file or when the the GPS acquires lock.
    - Each .csv file should include headers as specified in the OEM719 manual or see "GPS Logs Solution" for reference.
    - DO NOT modify the OEM719 Simulated Log.txt file.

Looking at the GPS Logs Solution folder, there are 6 different files that are considered solutions. Potentially
6 different files must be created? The files are:
    1. BESTXYZ.csv
    2. GPS GPGSV.csv
    3. GPS HWMONITOR.csv
    4. GPS PSRDOP.csv
    5. GPS RAW DATA.csv
    6. GPS TIME.csv

NOTE: Original data not provided due to limitations from NDA. This is my own work and can be created using publically available
documentes such as the OEM719 Manual. This does not violate any NDA as this is my work and no proprietary information as been provide.
Company is also kept hidden. This was an interview project. I passed the exam (correct work) but unfortunately someone finished before 
me and scheduled the final round interview before me and got the job.

Enrique Cisneros Jr 10/27/2025
"""
import csv
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import time

class OEM719_Logger:

    def __init__(self, file: str, offset: int = 1000000, capture_freq: int = 1, capture_seconds: int = 30, leap_seconds: int = 0):
        self.file = file
        self.offset = offset
        self.capture_freq = capture_freq
        self.capture_seconds = capture_seconds
        self.max_per_type = capture_freq * capture_seconds
        self.leap_seconds = leap_seconds
        
        self.file_aquisition_time = datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3] #NORM
        # Columns definitions from the manual
        self.BESTXYZ_columns = [
            'Time','Message','Port','Sequence','% Idle Time','Time Status','Week','Seconds',
            'Receiver Status','Reserved','Receiver S/W Version',
            'P-sol status','pos type','P-X (m)','P-Y (m)','P-Z (m)','P-X ó (m)','P-Y ó (m)','P-Z ó (m)',
            'V-sol status','vel type','V-X (m/s)','V-Y (m/s)','V-Z (m/s)','V-X ó (m/s)','V-Y ó (m/s)','V-Z ó (m/s)',
            'stn ID','V-latency (s)','diff_age (s)','sol_age (s)','#SVs','#ggL1','#solnMultiSVs'
        ]

        self.GPGSV_columns = [
            'Time','#Sats in view','prn1','elev1','azimuth1','SNR1','prn2','elev2','azimuth2','SNR2',
            'prn3','elev3','azimuth3','SNR3','prn4','elev4','azimuth4','SNR4','prn5','elev5','azimuth5','SNR5',
            'prn6','elev6','azimuth6','SNR6','prn7','elev7','azimuth7','SNR7','prn8','elev8','azimuth8','SNR8',
            'prn9','elev9','azimuth9','SNR9','prn10','elev10','azimuth10','SNR10','prn11','elev11','SNR11',
            'azimuth11','prn12','elev12','azimuth12','SNR12','SNR13','azimuth13','elev13','prn13','SNR14',
            'azimuth14','elev14','prn14','SNR22','azimuth22','elev22','prn22','azimuth21','SNR21','elev21','prn21',
            'SNR20','azimuth20','elev20','prn20','SNR19','azimuth19','elev19','prn19','SNR18','azimuth18','elev18',
            'prn18','SNR17','azimuth17','elev17','prn17','SNR16','azimuth16','elev16','prn16','SNR15','azimuth15',
            'elev15','prn15','SNR23','azimuth23','elev23','prn23','SNR24','azimuth24','elev24','prn24','SNR36',
            'azimuth36','elev36','prn36','azimuth35','SNR35','elev35','prn35','SNR34','azimuth34','elev34','prn34',
            'SNR33','azimuth33','elev33','prn33','SNR32','azimuth32','elev32','prn32','SNR31','azimuth31','elev31',
            'prn31','SNR30','azimuth30','elev30','prn30','SNR29','azimuth29','elev29','prn29','SNR28','azimuth28',
            'elev28','prn28','SNR27','azimuth27','elev27','prn27','SNR26','azimuth26','elev26','prn26','SNR25',
            'azimuth25','elev25','prn25','SNR37','azimuth37','elev37','prn37','SNR38','azimuth38','elev38','prn38',
            'SNR46','azimuth46','elev46','prn46','azimuth45','SNR45','elev45','prn45','SNR44','azimuth44','elev44',
            'prn44','SNR43','azimuth43','elev43','prn43','SNR42','azimuth42','elev42','prn42','SNR41','azimuth41',
            'elev41','prn41','SNR40','azimuth40','elev40','prn40','SNR39','azimuth39','elev39','prn39','SNR47',
            'azimuth47','elev47','prn47','SNR48','azimuth48','elev48','prn48','SNR49','azimuth49','elev49','prn49',
            'SNR50','azimuth50','elev50','prn50','SNR52','azimuth52','elev52','prn52','azimuth51','SNR51','elev51',
            'prn51','SNR53','azimuth53','elev53','prn53','SNR54','azimuth54','elev54','prn54','SNR62','azimuth62',
            'elev62','prn62','azimuth61','SNR61','elev61','prn61','SNR60','azimuth60','elev60','prn60','SNR59',
            'azimuth59','elev59','prn59','SNR58','azimuth58','elev58','prn58','SNR57','azimuth57','elev57','prn57',
            'SNR56','azimuth56','elev56','prn56','SNR55','azimuth55','elev55','prn55','SNR63','azimuth63','elev63',
            'prn63','SNR64','azimuth64','elev64','prn64','SNR76','azimuth76','elev76','prn76','azimuth75','SNR75',
            'elev75','prn75','SNR74','azimuth74','elev74','prn74','SNR73','azimuth73','elev73','prn73','SNR72',
            'azimuth72','elev72','prn72','SNR71','azimuth71','elev71','prn71','SNR70','azimuth70','elev70','prn70',
            'SNR69','azimuth69','elev69','prn69','SNR68','azimuth68','elev68','prn68','SNR67','azimuth67','elev67',
            'prn67','SNR66','azimuth66','elev66','prn66','SNR65','azimuth65','elev65','prn65','SNR77','azimuth77',
            'elev77','prn77','SNR78','azimuth78','elev78','prn78','SNR80','azimuth80','elev80','prn80','SNR79',
            'azimuth79','elev79','prn79','SNR86','azimuth86','elev86','prn86','azimuth85','SNR85','elev85','prn85',
            'SNR84','azimuth84','elev84','prn84','SNR83','azimuth83','elev83','prn83','SNR82','azimuth82','elev82',
            'prn82','SNR81','azimuth81','elev81','prn81','SNR87','azimuth87','elev87','prn87','SNR88','azimuth88',
            'elev88','prn88','SNR90','azimuth90','elev90','prn90','SNR89','azimuth89','elev89','prn89','SNR96',
            'azimuth96','elev96','prn96','azimuth95','SNR95','elev95','prn95','SNR94','azimuth94','elev94','prn94',
            'SNR93','azimuth93','elev93','prn93','SNR92','azimuth92','elev92','prn92','SNR91','azimuth91','elev91',
            'prn91'
        ]

        self.HWMON_columns = [
            'Time','Message','Port','Sequence','% Idle Time','Time Status','Week','Seconds',
            'Receiver Status','Reserved','Receiver S/W Version',
            'Temperature (C)','Antenna Current (A)','Digital Core 3V3 Voltage (V)','Antenna Voltage (V)',
            'Digital 1V2 Core Voltage (V)','Regulated Supply Voltage (V)','1V8 (V)','5V Voltage (Volts)',
            'Secondary Temperature (C)','Temperature Status Flag','Antenna Current Status Flag',
            'Digital Core 3V3 Status Flag','Antenna Voltage Status Flag','Digital 1V2 Core Status Flag',
            'Regulated Supply Voltage Status Flag','1V8 Status Flag','5V Voltage Status Flag',
            'Secondary Temperature Status Flag'
        ]

        self.PSRDOP_columns = [
            'Time','Message','Port','Sequence','% Idle Time','Time Status','Week','Seconds',
            'Receiver Status','Reserved','Receiver S/W Version',
            'gdop','pdop','hdop','htdop','tdop','cutoff'
        ]

        self.RAW_columns = ['Time','MSGS RECEIVED']

        self.TIME_columns = [
            'Time','Message','Port','Sequence','% Idle Time','Time Status','Week','Seconds',
            'Receiver Status','Reserved','Receiver S/W Version',
            'clock status','offset (s)','offset std (s)','utc offset',
            'utc year','utc month','utc day','utc hour','utc min','utc ms','utc status'
        ]

        self.open_writers()

####################################################################################################################################################
    
    @staticmethod
    def safe_float(x, default = ""):
        try:
            return float(x)
        except Exception:
            return default
        
    
    @staticmethod
    def safe_int(x, default = ""):
        try:
            return int(float(x))
        except Exception:
            return default
        
    
    @staticmethod
    def split_data_and_crc(data_str: str):
        """
        Function that separates the endline and the byte information on the right side of the asterik: "*". It then returns the
        rest of the data by splitting it by the commas, returning a list.
        """
        if '*' in data_str:
            data, crc = data_str.split('*', 1)
        else:
            data, crc = data_str, ""
        data = data.strip().rstrip('\r').rstrip('\n')
        return [f.strip() for f in data.split(',') if f != ""], crc.strip()
    
####################################################################################################################################################
    
    def find_start_bytes(self, fh, data_bytes_target = 1000000):
        """
        This function helps find the start of the 1000000 bytes, only includes the data points (excludes # and crc). Once it reaches the
        1000000 bytes it will start parsing the file.
        """
        data_bytes = 0
        while True:
            position = fh.tell()
            line = fh.readline()
            if not line:
                break
            # Now remove the '#' and the CRC section
            clean  = line.strip()
            if clean.startswith("#"):# or clean.startswith("$"):
                clean = clean[1:]

            if "*" in clean:
                clean = clean.split("*", 1)[0]

            # Counting remainig bytes
            data_bytes += len(clean.encode("utf-8")) + 1 # for the newline
            if data_bytes >= data_bytes_target:
                fh.seek(position)
                break

####################################################################################################################################################
    def open_writers(self):
        """
        This function opens the CSV files and writes the headers once. 
        """
        self.files = {}
        self.writers = {}

        def open_file(path, cols):
            write_header = not os.path.exists(path)
            f = open(path, "w", newline = "")
            w = csv.DictWriter(f, fieldnames = cols)
            if write_header:
                w.writeheader()
            return f, w
        
        self.files["BESTXYZA"], self.writers["BESTXYZA"] = open_file("BESTXYZ_result.csv", self.BESTXYZ_columns)
        self.files["GPGSV"], self.writers["GPGSV"] = open_file("GPS GPGSV_result.csv", self.GPGSV_columns)
        self.files["HWMONITORA"], self.writers["HWMONITORA"] = open_file("GPS HWMONITOR_result.csv", self.HWMON_columns)
        self.files["PSRDOPA"], self.writers["PSRDOPA"] = open_file("GPS PSRDOP_result.csv", self.PSRDOP_columns)
        self.files["RAW"], self.writers["RAW"] = open_file("GPS RAW DATA_result.csv", self.RAW_columns)
        self.files["TIMEA"], self.writers["TIMEA"] = open_file("GPS TIME_result.csv", self.TIME_columns)

####################################################################################################################################################

    def close_writers(self):
        """
        This function is to close all the CSV files in one go.
        """
        for f in self.files.values():
            try:
                f.close()
            except Exception:
                pass

####################################################################################################################################################

    def parse_header(self, line: str) -> dict:
        """
        This functions parses one line of the inputted .txt file. It then returns a dictionary with 'data' string. The first few entries of the
        dictionary are the satellite information as listed. It is everything to the left of ';'. Everything to the right of ';' is lumped together
        as data since that is the data information. 
        """
        try:
            head, rest = line[1:].split(';', 1)
        except ValueError:
            head, rest = line[1:], ""

        parts = head.split(',')
        parts += [''] * (10 - len(parts))

        dictionary = {
            "Message": f"#{parts[0]}" if not parts[0].startswith('#') else parts[0],
            "Port": parts[1],
            "Sequence": parts[2],
            "% Idle Time": parts[3],
            "Time Status": parts[4],
            "Week": parts[5],
            "Seconds": parts[6],
            "Receiver Status": parts[7],
            "Reserved": parts[8],
            "Receiver S/W Version": parts[9],
            "data": rest
        }
        
        return dictionary
    
####################################################################################################################################################

    def row_TIMEA(self, hdr, data_fields):
        """
        This method handles the parsing of the #TIMEA line. It updates self.leap_seconds if needed. Ex line:
        #TIMEA,COM2,0,81.0,FINESTEERING,2159,68539.000,02444000,9924,16410;INVALID,0.000000000,0.000333564,-18.00000000000,2021,5,23,19,2,1000,WARNING*6e1b284b
        NOTE: There seems to be no 'ms' for the data so I will add 0 instead
        - hdr: comes from parse_header function
        - data_fields: comes from split_data_and_crc function
        """
        row = {k:"" for k in self.TIME_columns}
        row.update({
            "Message": hdr["Message"],
            "Port": hdr["Port"],
            "Sequence": hdr["Sequence"],
            "% Idle Time": hdr["% Idle Time"],
            "Time Status": hdr["Time Status"],
            "Week": self.safe_int(hdr["Week"], ""),
            "Seconds": self.safe_float(hdr["Seconds"], ""),
            "Receiver Status": hdr["Receiver Status"],
            "Reserved": hdr["Reserved"],
            "Receiver S/W Version": hdr["Receiver S/W Version"],
        })

        labels = ["clock status","offset (s)","offset std (s)","utc offset",
                  "utc year","utc month","utc day","utc hour","utc min", "utc status"] # Did this so that I can add the ms manually while iterating over the rest.
        
        for i, lab in enumerate(labels):
            row[lab] = data_fields[i] if i < len(data_fields) else ""

        row["utc ms"] = 0.0 # add 0 manually
        # Update leap seconds if utc offset present, use abs val to convert GPS -> UTC like the sample solutions
        try:
            utc_off = float(row["utc offset"])
            if abs(utc_off) > 0:
                self.leap_seconds = abs(int(utc_off))
        except Exception:
            pass

        row["Time"] = self.file_aquisition_time
        return row
    
####################################################################################################################################################

    def row_PSRDOPA(self, hdr, data_fields, tstr):
        """
        This function parses the #PSRDOPA header log text. Data is in proper units already. Sample log:
        #PSRDOPA,COM2,0,82.0,FINESTEERING,2159,68542.000,02444000,1779,16410;10.2780,10.2210,10.1340,10.1920,1.0800,5.0,4,7,18,6,14*1536ebe7
        - hdr: comes from parse_header function
        - data_fields: comes from split_data_and_crc function
        NOTE: In the sample solution, the final column is "angle cutoff" but in the manual and the data there are still more fields leftover such
        as: #PRN, PRN, Next PRN offset. I only copied the headers from the Solution because I thought those are the only ones that matter. Can easily
        add these columns into the function if you wish to log them.
        """
        row = {k: "" for k in self.PSRDOP_columns}
        row.update({
            "Time": self.file_aquisition_time,
            "Message": hdr["Message"],
            "Port": hdr["Port"],
            "Sequence": hdr["Sequence"],
            "% Idle Time": hdr["% Idle Time"],
            "Time Status": hdr["Time Status"],
            "Week": self.safe_int(hdr["Week"], ""),
            "Seconds": self.safe_float(hdr["Seconds"], ""),
            "Receiver Status": hdr["Receiver Status"],
            "Reserved": hdr["Reserved"],
            "Receiver S/W Version": hdr["Receiver S/W Version"],
        })

        remainder = self.PSRDOP_columns[11:]
        for i, col in enumerate(remainder):
            if i < len(data_fields):
                v = data_fields[i]
                row[col] = self.safe_float(v, "") # Stops at cutoff because that is last val in Solution
        return row

####################################################################################################################################################

    def row_HMONITOR(self, hdr, data_fields, tstr):
        """
        This function parses the #HWMONITORA function. Sample Output:
        #HWMONITORA,COM2,0,81.0,FINESTEERING,2159,68539.000,02444000,52db,16410;9,31.074481964,100,0.129426137,200,3.269841433,600,5.061782837,700,1.191697240,800,3.271062374,f00,1.824175835,1100,5.100854874,1500,32.539684296,1600*f6a40ae2
        After the 'Reserved' part of the line, in this case 9, we must take every other data field bc its data + status and then data + stats. Example:
            9,31.074481964,100,0.129426137,200,3.269841433,600,5.061782837,700,
            - 9 represents the number of components being monitored.
            - 31.074481964 is the temperatue
            - 100 is the status for the temperature
            - 0.129426137 is the Current
            - 200 is the stats
            - And so on and so forth for the rest. 
        NOTE: Dropping all the status code for the corresponding values
        """
        row = {k: "" for k in self.HWMON_columns}
        row.update({
            "Time": self.file_aquisition_time,
            "Message": hdr["Message"],
            "Port": hdr["Port"],
            "Sequence": hdr["Sequence"],
            "% Idle Time": hdr["% Idle Time"],
            "Time Status": hdr["Time Status"],
            "Week": self.safe_int(hdr["Week"], ""),
            "Seconds": self.safe_float(hdr["Seconds"], ""),
            "Receiver Status": hdr["Receiver Status"],
            "Reserved": hdr["Reserved"],
            "Receiver S/W Version": hdr["Receiver S/W Version"],
        })

        remainder = self.HWMON_columns[11:]
        measurements_stirngs = data_fields[1::2]
        measurements = [self.safe_float(value,0.0) for value in measurements_stirngs] # Converts them to floats
        for i, col in enumerate(remainder):
            try:
                row[col] = measurements[i] if i < len(measurements) else 0.0
            except Exception:
                pass
        return row
       

####################################################################################################################################################

    def row_BESTXYZA(self, hdr, data_fields, tstr):
        """
        This function parses a line that starts with the header #BESTXYZA. It updates the rows with the basic sattellite information and then 
        parses the 'data' part that is returned when using 'self.split_data_and_crc' function. Since 'split...' returns a list, this function
        then parses the 'remainder' part by comma to fill into its corresponding column as listed in the manual. Units are already in meters (m) for
        coordinate variables and meters per second (m/s) for velocity variables. Sample line:
        #BESTXYZA,COM2,0,81.0,FINESTEERING,2159,68539.000,02444000,44cf,16410;SOL_COMPUTED,SINGLE,3697473.3591,2853107.0896,-5024519.8589,41.5719,25.7385,27.3269,SOL_COMPUTED,DOPPLER_VELOCITY,5422.3615,1939.8433,5090.5280,4.9688,3.0763,3.2662,"",0.000,0.000,0.000,4,4,4,0,0,00,00,01*e36c2af8
        
        - hdr: comes from parse_header function
        - data_fields: comes from split_data_and_crc function
        """
        row = {k: "" for k in self.BESTXYZ_columns}
        row.update({
            "Time": self.file_aquisition_time,
            "Message": hdr["Message"],
            "Port": hdr["Port"],
            "Sequence": hdr["Sequence"],
            "% Idle Time": hdr["% Idle Time"],
            "Time Status": hdr["Time Status"],
            "Week": self.safe_int(hdr["Week"], ""),
            "Seconds": self.safe_float(hdr["Seconds"], ""),
            "Receiver Status": hdr["Receiver Status"],
            "Reserved": hdr["Reserved"],
            "Receiver S/W Version": hdr["Receiver S/W Version"],
        })

        remainder = self.BESTXYZ_columns[11:]
        for i, col in enumerate(remainder): # This just fills in the data field to its corresponding place in the columns. Columns should be
            if i < len(data_fields):
                v = data_fields[i]
                try:
                    row[col] = float(v)
                except Exception:
                    row[col] = v
        return row
    
####################################################################################################################################################

    def row_GPGSV(self, fh, first_line, tstr):
        """
        This function parses the line that starts with $GPGSV. Looking at the log, they seem to always come in pair, two back to back.
        If there are more than 4 satellites, additional messages are sent. So that means up too two lines are sent back to back.
        A sample output goes as follows:
            $GPGSV,2,1,05,| 07,65,197,43,| 06,37,251,42,| 13,31,060,42,| 14,29,100,42| *78 -> Should be 20 messages.
            $GPGSV,2,2,05,| 10,13,136,41| *4E

        The way it is structured:
        $GPGSV, # msgs, msg #, # sats, prn, elevation, azimuth, SNR, prn2, elev2, azimuth2,SNR2,... 
        """
       
        row = {k:"" for k in self.GPGSV_columns}
        consumed = [first_line]

        def parse_one(line):
            parts = line.strip().split(',')
            total_msg = int(parts[1])
            msg_num = int(parts[2])
            num_sats = int(parts[3])
            payload = parts[4:] if len(parts) >= 5 else []
            if payload:
                payload[-1] = payload[-1].split('*', 1)[0]
            return total_msg, msg_num, num_sats, payload
        
        try:
            total_msgs, msg_nums, sats_in_view, payload = parse_one(first_line)
        except Exception as e:
            print(e)
            row["#Sats in view"] = "#NV"
            row["Time"] = self.file_aquisition_time
            return row, consumed
        all_payload = list(payload)
        expected_next = msg_nums + 1

        while expected_next <= total_msgs:
            pos = fh.tell()
            next_line = fh.readline()
            if not next_line:
                break
            if not next_line.startswith("$GPGSV"):
                break
            t2, n2, sats2, p2 = parse_one(next_line)
            if t2 != total_msgs or n2 != expected_next:
                fh.seek(pos)
                break
            consumed.append(next_line)
            all_payload.extend(p2)
            expected_next += 1
        
        row['#Sats in view'] = sats_in_view
        row["Time"] = self.file_aquisition_time

        sats_cols = [c for c in self.GPGSV_columns if c.startswith(("prn", "elev", "azimuth", "SNR"))]
        for i, col in enumerate(sats_cols):
            row[col] = all_payload[i] if i < len(all_payload) and all_payload[i] != "" else "#NV"

        return row, consumed
    
    
####################################################################################################################################################

    def run_parser(self):
        """
        This function is the main function that runs the main process. It will cycle for 30 seconds and then stop. It will also
        start after 100000 bytes.
        """
        counts = {"TIMEA": 0, "PSRDOPA": 0, "HWMONITORA": 0, "BESTXYZA": 0, "GPGSV": 0}
        message_type = ["TIMEA", "PSRDOPA", "HWMONITORA", "BESTXYZA", "GPGSV"]
        have_valid_time = False
        
        size = os.path.getsize(self.file)
        start_pos = self.offset if size > self.offset else 0
        """
        NOTE: For some reason can not match the same exact values as shown in the sample solution. Using two different methods to count the
        1,000,000 bytes, I start at two different sections of the .txt file, either before the solution or after the solution. The other method
        counts all the bytes by doing:
            with open(self.file, "r", errors = "ignore") as fh:
                fh.seek(start_pos, os.SEEK_SET)

        For when the satellite starts lock on, in the manual it states when the time status is FINESTEERING, it is fully connected to the GPS
        but this happens wayyy earlier, before the 1,000,000 bytes, no where near the solutions. Using the bytes method, it comes closest to the
        solutions provided.
        """
        with open(self.file, "r", errors = "ignore") as fh:
            self.find_start_bytes(fh, self.offset)
            start_time = time.time()

            while(time.time() - start_time) < self.capture_seconds:
                cycle_start = time.time()
                got = {msg: False for msg in message_type}
                
                current_time = datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f %p")[:-3]

                while not all(got.values()):
                    position = fh.tell()
                    raw = fh.readline()
                    if not raw:
                        break
                    line = raw.strip()
                    if not line:
                        continue

                    #Record in raw file
                    self.writers["RAW"].writerow({"Time": current_time, "MSGS RECEIVED": line})
                    
                    if line.startswith("#"):
                        hdr = self.parse_header(line)
                        data_fields, _crc = self.split_data_and_crc(hdr["data"])
                        msg = hdr["Message"]

                        if msg == "#TIMEA" and not got["TIMEA"]:
                            row = self.row_TIMEA(hdr, data_fields)
                            row["Time"] = current_time
                            self.writers["TIMEA"].writerow(row)
                            counts["TIMEA"] += 1
                            got["TIMEA"] = True
                            have_valid_time = True

                        elif msg == "#PSRDOPA" and not got["PSRDOPA"] and have_valid_time:
                            row = self.row_PSRDOPA(hdr, data_fields, current_time)
                            row["Time"] = current_time
                            self.writers["PSRDOPA"].writerow(row)
                            counts["PSRDOPA"] += 1
                            got["PSRDOPA"] = True

                        elif msg == "#HWMONITORA" and not got["HWMONITORA"] and have_valid_time:
                            row = self.row_HMONITOR(hdr, data_fields, current_time)
                            row["Time"] = current_time
                            self.writers["HWMONITORA"].writerow(row)
                            counts["HWMONITORA"] += 1
                            got["HWMONITORA"] = True

                        elif msg == "#BESTXYZA" and not got["BESTXYZA"] and have_valid_time:
                            row = self.row_BESTXYZA(hdr, data_fields, current_time)
                            row["Time"] = current_time
                            self.writers["BESTXYZA"].writerow(row)
                            counts["BESTXYZA"] += 1
                            got["BESTXYZA"] = True
                    
                    elif line.startswith("$GPGSV") and not got["GPGSV"] and have_valid_time:
                        row, consumed = self.row_GPGSV(fh, line, current_time)
                        row["Time"] = current_time
                        self.writers["GPGSV"].writerow(row)
                        counts["GPGSV"] += 1
                        got['GPGSV'] = True
                        for cl in consumed:
                            self.writers["RAW"].writerow({"Time": current_time, "MSGS RECEIVED": cl.strip()})

                    if all(got.values()):
                        break
                
                elapsed = time.time() - cycle_start
                delay = max(0.0, (1.0 / self.capture_freq) - elapsed)
                time.sleep(delay)

                #Stop after 30 seconds
                if all(counts[m] >= self.max_per_type for m in message_type):
                    break

        self.close_writers()

####################################################################################################################################################
####################################################################################################################################################

if __name__ == "__main__":
    file = "OEM719 Simulated Log.txt"
    offset = 1000000
    capture_freq = 1
    capture_seconds = 30
    parser = OEM719_Logger(file, offset, capture_freq, capture_seconds)
    parser.run_parser()











