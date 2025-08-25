TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = NLL484LaserAtest
# NLL484LaserAtest.dbd will be created and installed
DBD += NLL484LaserAtest.dbd

# NLL484LaserAtest.dbd will be made up from these files:
NLL484LaserAtest_DBD += base.dbd

# Include dbd files from all support applications:
#NLL484LaserAtest_DBD += xxx.dbd
NLL484LaserAtest_DBD += calc.dbd
NLL484LaserAtest_DBD += stream.dbd
NLL484LaserAtest_DBD += asyn.dbd
NLL484LaserAtest_DBD += drvAsynIPPort.dbd

# Add all the support libraries needed by this IOC
#NLL484LaserAtest_LIBS += xxx
NLL484LaserAtest_LIBS += calc
NLL484LaserAtest_LIBS += stream asyn

# NLL484LaserAtest_registerRecordDeviceDriver.cpp derives from NLL484LaserAtest.dbd
NLL484LaserAtest_SRCS += NLL484LaserAtest_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
NLL484LaserAtest_SRCS_DEFAULT += NLL484LaserAtestMain.cpp
NLL484LaserAtest_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#NLL484LaserAtest_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
NLL484LaserAtest_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

