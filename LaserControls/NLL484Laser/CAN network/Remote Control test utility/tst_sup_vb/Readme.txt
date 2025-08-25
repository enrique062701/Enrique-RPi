Please use the following steps to recreate project in VS2013:

1. In Visual Studio new project wizard choose Visual Basic -> Console Application
2. Project->Add Reference... and add rcclass.dll
3. Copy following DLLs and REMOTECONTROL.CSV to target.exe folder
   REMOTECONTROL.DLL
   REMOTECONTROL64.DLL
   USBCAND.DLL
   USBCAND64.DLL
   CANRS232.DLL
   CANRS23264.DLL
4. Modify code


All RC class functions return true on success and false on failure. Further failure information is stored 
in RC.ErrorCode.

RC member function C# prototypes:

	// contype  - ConnectionType enum, usb/rs232/tcp
	// hwdevice - USB serial number / com port name / IP or hostname
	// inipath  - path to REMOTECONTROL.CSV file
    public bool Connect(ConnectionType contype, string hwdevice, string inipath);
	// Same like above with default hwdevice="" and inipath="". Useful only for USB connection,
	// connect to first available USB device, look for CSV in exe folder.
    public bool Connect(ConnectionType contype);

    public bool Disconnect();

	// get list of available devices.
    public bool GetDevices(out List<string> slist);

    // GetFirstDeviceName and GetNextDeviceName are for compatibility with plain REMOTECONTROL.DLL calls.
	// It should be easier to use GetDevices() instead. GetFirst...() returns first device, GetNext...()
	// are called to retrieve further devices until GetNext...() returns false
	public bool GetFirstDeviceName(out string devname);
    public bool GetNextDeviceName(out string devname);

	// get list of available regiters in specified device
    public bool GetRegisters(string device, out List<string> slist);

    // GetFirstRegisterName and GetNextRegisterName are for compatibility with plain REMOTECONTROL.DLL calls.
	// It should be easier to use GetRegisters() instead. GetFirst...() returns first register, GetNext...()
	// are called to retrieve further registers until GetNext...() returns false
	public bool GetFirstRegisterName(string device, out string regname);
    public bool GetNextRegisterName(out string regname);

	// Get() reads register setting. There are two similar groups, one for receiving string value and 
	// another one for receiving double. In case timeout is skipped, default value of 50ms is used.
    public bool Get(string device, string register, out double value, int timeout, out int timestamp);
    public bool Get(string device, string register, out double value, int timeout);
    public bool Get(string device, string register, out double value);
    public bool Get(string device, string register, out string value, int timeout, out int timestamp);
    public bool Get(string device, string register, out string value, int timeout);
    public bool Get(string device, string register, out string value);

	// Check if register is writeable.
    public bool IsWriteable(string device, string register, out bool iswriteable);

    // Check if writeable register has nonvolatile power on settting.
	public bool IsNV(string device, string register, out bool isnv);

	// Get allowed register values. In case register has values list like ON/OFF/TRISTATE, GetValues()
	// will return true and allowed values in slist. If there are no values list, GetValues()
	// will return false and set RC.ErrorCode to RC.RMTCTRLERR_NOMOREDATA
	public bool GetValues(string device, string register, out List<string> slist);

    // Get allowed register values using separate GetFirst...() and GetNext...() calls
	public bool GetFirstAllowedValue(string device, string register, out string value);
    public bool GetNextAllowedValue(string device, string register, out string value);

	// Set register value. Two functions for string value and two for double.
	// When forcelimits is true and value is violating register limits, respective min/max limit is
	// applied without triggering failure. Functions without forcelimits argument behave as if 
	// forcelimits was false, which means error is triggered with value is violating 
	// register limits.
    public bool Set(string device, string register, double value, bool forcelimits);
    public bool Set(string device, string register, double value);
    public bool Set(string device, string register, string value, bool forcelimits);
    public bool Set(string device, string register, string value);

    // Set register and register NV value.
	public bool SetNV(string device, string register, double value);
    public bool SetNV(string device, string register, string value);

    // Start register log. Default logmemsize is 100.000 bytes
	public bool StartLog(string device, string register, int logmemsize);
    public bool StartLog(string device, string register);
    public bool StopLog(string device, string register);

    // Read register log
	public bool GetLog(string device, string register, out double value, out int timestamp);
    public bool GetLog(string device, string register, out double value);
    public bool GetLog(string device, string register, out string value, out int timestamp);
    public bool GetLog(string device, string register, out string value);

    // Get register min value
	public bool GetMin(string device, string register, out double min);

    // Get register max value
    public bool GetMax(string device, string register, out double max);

	// Get register min and max values
    public bool GetMinMax(string device, string register, out double min, out double max);
    public bool GetMinMax(string device, string register, out string min, out string max);

	// Get default C printf format string for printing register value.
    public bool GetPrintfString(string device, string register, out string fmtstr);


RC.ErrorCode values:
    public  const int RMTCTRLERR_OK                =0;  // Success, no error
    public  const int RMTCTRLERR_NOMOREDATA        =1;  // End of registers / devices or enumerated values list
    public  const int RMTCTRLERR_NOCFGFILE         =2;  // REMOTECONTROL.CSV file is not found
    public  const int RMTCTRLERR_WRONGCFGFILE      =3;  // wrong REMOTECONTROL.CSV file
    public  const int RMTCTRLERR_BUFFERTOOSHORT    =4;  // application provided return buffer is too short
    public  const int RMTCTRLERR_NOSUCHDEVICE      =5;  // specified device is not available
    public  const int RMTCTRLERR_NOSUCHREGISTER    =6;  // specified register is not available
    public  const int RMTCTRLERR_CANTCONNECT       =7;  // unable to establish connection
    public  const int RMTCTRLERR_TIMEOUT           =8;  // timeout waiting for device answer
    public  const int RMTCTRLERR_READONLY          =9;  // register is read only
    public  const int RMTCTRLERR_NOT_NV           =10;  // register is not NV
    public  const int RMTCTRLERR_HILIMIT          =11;  // attempt to set value above upper limit
    public  const int RMTCTRLERR_LOLIMIT          =12;  // attempt to set value below bottom limit
    public  const int RMTCTRLERR_NOSUCHVALUE      =13;  // attempt to set not allowed value
    public  const int RMTCTRLERR_NOTLOGGED        =14;  // register is not being logged
    public  const int RMTCTRLERR_MEMORYFULL       =15;  // not enough memory
    public  const int RMTCTRLERR_LOGISEMPTY       =16;  // no data in the queue yet
    public  const int RMTCTRLERR_ALREADYCONNECTED =17;  // already connected, please disconnect first
    public  const int RMTCTRLERR_NOTYETCONNECTED = 18;  // not connected, please connect first

    public const int RMTCTRLERR_LOGOVERFLOW = -2147483648; // Log FIFO overrun. ErrorCode is bitwise ORed with this error code.
