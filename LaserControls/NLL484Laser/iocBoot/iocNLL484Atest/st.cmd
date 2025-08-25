#!../../bin/linux-aarch64/NLL484Atest

#- You may have to change NLL484Atest to something else
#- everywhere it appears in this file

< envPaths
######################################################
#First set all your environments
epicsEnvSet "STREAM_PROTOCOL_PATH" "$(TOP)/db"

#Allow PV name prefixes and serial port name to be set from the environment 

epicsEnvSet "P" "$(P=NLL484)"
epicsEnvSet "R" "$(R=Laser)" 
epicsEnvSet "TTY" "$(TTY=10.97.106.99:4001)"

###################################################
#Next is to register all support components
cd "${TOP}"
dbLoadDatabase "dbd/NLL484Atest.dbd"
NLL484Atest_registerRecordDeviceDriver pdbbase

####################################################
# Next is to set up ASYN ports
drvAsynSerialPortConfigure("L0", "10.97.106.99:4001", 0, 0, 0)
asynOctetSetInputEos("L0", -1, "\n")
asynOctetSetOutputEos("L0", -1, "\n")
asynSetTraceIOMask("L0", -1, 0x2)
asynSetTraceMask("L0", -1, 0x9)

###################################################

## Load record instances
#dbLoadRecords("db/NLL484Atest.db","P=$(P), R=S(R), PORT = L0, A=0")

cd "${TOP}/iocBoot/${IOC}"
iocInit

## Start any sequence programs
#seq sncxxx,"user=phoenix"
