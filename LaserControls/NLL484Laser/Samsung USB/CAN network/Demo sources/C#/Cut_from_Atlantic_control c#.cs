 public enum StateOfLaser : int
    {
        [StringValue("POWEROFF")]
        Off = 0,
        [StringValue("STARTING")]
        Starting = 1,
        [StringValue("SLEEP")]
        Sleep = 2,
        [StringValue("STOP")]
        Stop = 3,
        [StringValue("PAUSE")]
        Pause = 4,
        [StringValue("RUN")]
        Run = 5,
        [StringValue("FAULT")]
        Fault = 6
    }
	SetRegisterFromString(mainRegisters.RegSetState, GetStringFromState(state));
	 private  void SetRegisterFromString(string deviceName, string regName, string value)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            EksplaDevice dev = GetDevice(deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcSetRegFromString(dev.Name, regName, value);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to set " + regName + " for Ekspla laser.");
        }
		
	
	
   if(state._paramLaserRun)
                        Hardware.LaserController.SetState(StateOfLaser.Run);
                    else
                        Hardware.LaserController.SetState(StateOfLaser.Stop);


 public struct EksplaRegister
    {
        public string deviceName;
        public string regName;
        public EksplaRegister(string deviceName, string regName)
        {
            this.deviceName = deviceName;
            this.regName = regName;
        }
        public static EksplaRegister EmptyRegister
        {
            get { return new EksplaRegister("", ""); }
        }
    }
public Ekspla_PL()
        {
            registers.RegGetState = new EksplaRegister("SY320100:32", "Current State");
            registers.RegSetState = new EksplaRegister("SY320100:32", "Command");
            registers.RegAttenuator = new EksplaRegister("SY320100:32", "Attenuator");
            registers.RegData = new EksplaRegister("PHDamp:49", "Data");
            registers.RegMean = new EksplaRegister("PHDamp:49", "Mean");
            registers.RegSeedFreq = new EksplaRegister("SY320100:32", "Repetition rate");
            registers.RegSyncMode = new EksplaRegister("SY320100:32", "Synchronization Mode");
            registers.RegFault = new EksplaRegister("LDM6A:18", "Fault");
            registers.RegHV2 = new EksplaRegister("PS20100:16", "HV2 ON");
            registers.RegShutter = EksplaRegister.EmptyRegister;
            registers.RegPower = EksplaRegister.EmptyRegister;

            parametersFilePath = "Laser parameters\\Ekspla_PL\\REMOTECONTROL.CSV";
        }
protected EksplaLaserControlRegisters registers;
 public struct EksplaLaserControlRegisters
    {
        public EksplaRegister RegGetState;
        public EksplaRegister RegSetState;
        public EksplaRegister RegAttenuator;
        public EksplaRegister RegData;
        public EksplaRegister RegMean;
        public EksplaRegister RegSeedFreq;
        public EksplaRegister RegSyncMode;
        public EksplaRegister RegFault;
        public EksplaRegister RegHV2;
        public EksplaRegister RegShutter;
        public EksplaRegister RegPower;
    }

    public class EksplaLaserControl : ALaserController
    {
        #region Variables
        const int SIZE = 40;
        const int DEFAULT_TIMEOUT = 1000;
        EksplaLaserControlRegisters mainRegisters;

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern IntPtr LoadLibrary(string filename);
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern bool FreeLibrary(IntPtr hModule);

        List<EksplaDevice> devices = new List<EksplaDevice>();
        List<Thread> threads = new List<Thread>();
        BasicDeviceStatusGUI dataStatusGUI = new BasicDeviceStatusGUI();
        BasicDeviceStatusGUI meanStatusGUI = new BasicDeviceStatusGUI();
        BasicDeviceStatusGUI stateStatusGUI = new BasicDeviceStatusGUI();
        bool isInitialized = false;
        static bool filesChecked = false;

        bool watchLaserState = false; //for observing laser connection on fabrication
        bool watchGUI = false; //for GUI watching register values
        private EksplaLaserControlParams parameters;
        private AEksplaLaserModel eksplaLaserModel;

     
        #endregion
        public AEksplaLaserModel getLaserController()
        {
            return eksplaLaserModel;
        }
        public void setFrequency(double frequency)
        {
            eksplaLaserModel.setFrequencyFromDouble(frequency);
        }
        public EksplaLaserControlRegisters Registers
        {
            get
            {
                return mainRegisters;
            }
        }

        #region Constructors
        public EksplaLaserControl(EksplaLaserControlParams parameters, AEksplaLaserModel eksplaLaserModel, LaserModel model)
        {
            keepMonitoring = false;
            monitorRegisterList = new List<EksplaRegister>();
            monitor = new Thread(new ThreadStart(MonitorThreadProc));

            this.parameters = parameters;
            type = Parameters.LaserType.Ekspla;

            this.model = model;
            this.eksplaLaserModel = eksplaLaserModel;
            mainRegisters = eksplaLaserModel.Registers;

            try
            {
                Uri uri = new Uri(System.Reflection.Assembly.GetExecutingAssembly().GetName().CodeBase);
                string exeDirectory = Path.GetDirectoryName(uri.LocalPath);
                string path = Path.Combine(exeDirectory, eksplaLaserModel.ParametersFilePath);
                if (File.Exists(path))
                {
                    string pathDestination = Path.Combine(exeDirectory, "REMOTECONTROL.CSV");
                    File.Copy(path, pathDestination, true);
                }
            }
            catch
            {
                Active.Log.Log("Failed to copy REMOTECONTROL.CSV Ekpsla laser control file");
            }
        }
        ~EksplaLaserControl()
        {
            MonitorStop();
        }
        #endregion

        #region GUI Status Watching
        public void MonitorData()
        {
            if (!watchGUI)
            {
                watchGUI = true;
                if (Active.Laser.ShowData)
                {
                    //StartWatchRegister("Laser data", dataStatusGUI, mainRegisters.RegData, Active.Laser.UpdateRate);
                    //Thread.Sleep(100);
                    //StartWatchRegister("Laser mean", meanStatusGUI, mainRegisters.RegMean, Active.Laser.UpdateRate);
                    //Thread.Sleep(100);
                }
                if(Active.Laser.ShowStatus)
                    StartWatchRegister("Laser state", stateStatusGUI, mainRegisters.RegGetState, Active.Laser.UpdateRate);
            }
        }

        private void StartWatchRegister(string name, BasicDeviceStatusGUI gui, EksplaRegister register, int timespan)
        {
            gui.SetDeviceName(name);
            gui.SetDeviceValue("_");
            WatchProperties prop = new WatchProperties(gui, timespan, register);
            Thread t = new Thread(new ParameterizedThreadStart(Watcher));
            threads.Add(t);
            t.Start(prop);
        }

        private void Watcher(object obj)
        {
            if (obj == null) return;
            WatchProperties prop = (WatchProperties)obj;
            string value = "";
            while (watchGUI)
            {
                try
                {
                    Thread.Sleep(prop.timespan);
                    value = GetRegisterAsString(prop.register.deviceName, prop.register.regName);
                    if (!prop.register.regName.Equals("Current State"))
                        value = value.Substring(0, 4 < value.Length ? 4 : value.Length);
                    else
                    {
                        switch (value)
                        {
                            case "FAULT":
                                prop.gui.ForeColor = System.Drawing.Color.Red;
                                prop.gui.Enabled = !prop.gui.Enabled;
                                break;
                            case "RUN":
                            case "SLEEP":
                            case "PAUSE":
                            case "STOP":
                                prop.gui.ForeColor = System.Drawing.Color.Black;
                                prop.gui.Enabled = true;
                                break;
                            default:
                                prop.gui.ForeColor = System.Drawing.Color.Green;
                                prop.gui.Enabled = !prop.gui.Enabled;
                                break;
                        }
                    }
                    prop.gui.SetDeviceValue(value);
                }
                catch 
                {
                    Thread.Sleep(750);
                    continue; 
                }
            }
        }
        #endregion

        #region CAN Monitor

        List<EksplaRegister> monitorRegisterList;
        Thread monitor;
        bool keepMonitoring;
        protected event EksplaRegisterChangedEventHandler registerChanged;
        protected virtual void OnRegisterChanged(EksplaRegisterChangedEventArgs e)
        {
            if (registerChanged != null)
                registerChanged(this, e);
        }
        public event EksplaRegisterChangedEventHandler RegisterChanged
        {
            add
            {
                if (!delegates.Contains(value))
                {
                    registerChanged += value;
                    delegates.Add(value);
                }
            }
            remove
            {
                if (delegates.Contains(value))
                {
                    registerChanged -= value;
                    delegates.Remove(value);
                }
            }
        }

        public void MonitorAddRegister(EksplaRegister register)
        {
            if (!monitorRegisterList.Contains(register))
                monitorRegisterList.Add(register);
        }
        public void MonitorRemoveRegister(EksplaRegister register)
        {
            if (monitorRegisterList.Contains(register))
            {
                monitorRegisterList.Remove(register);
            }
        }

        public bool MonitorStart()
        {
            if (keepMonitoring) return false;
            keepMonitoring = true;
            monitor.Start();
            return true;
        }
        public void MonitorReset()
        {
            if (keepMonitoring)
                MonitorStop();
            monitorRegisterList.Clear();

        }
        public void MonitorStop()
        {
            keepMonitoring = false;
            Thread.Sleep(200);
        }
        public bool IsMonitoring
        {
            get { return keepMonitoring; }
        }

        private void MonitorThreadProc()
        {
            List<string> valuesList = new List<string>(monitorRegisterList.Count);
            StringBuilder value = new StringBuilder(50);
            ErrorCode errorCode = ErrorCode.TIMEOUT;
            int timestamp = 0;
            int timeout = 1000;

            while (keepMonitoring)
            {
                Thread.Sleep(300);
                if (monitorRegisterList == null || monitorRegisterList.Count == 0)
                {
                    Thread.Sleep(500);
                    if (!keepMonitoring)
                        return;
                    continue;
                }
                for (int i = 0; i < monitorRegisterList.Count; i++)
                {
                    EksplaRegister reg =  monitorRegisterList[i];
                    Thread.Sleep(10);
                    if (!keepMonitoring) return;
                    try
                    {
                        errorCode = EksplaRC.rcGetRegAsString(reg.deviceName, reg.regName, value, 50, timeout, ref timestamp);
                        if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                        {
                            if (!keepMonitoring)
                                return;
                            Thread.Sleep(200);
                        }
                        else
                        {
                            if (i >= valuesList.Count)
                            {
                                valuesList.Add(value.ToString());
                            }
                            else if (!valuesList[i].Equals(value.ToString()))
                            {
                                OnRegisterChanged(new EksplaRegisterChangedEventArgs(reg.deviceName, reg.regName, value.ToString()));
                                valuesList[i] = value.ToString();
                            }
                        }
                    }
                    catch
                    {
                        if (!keepMonitoring)
                            return;
                        Thread.Sleep(300);
                    }
                }
            }
        }

        #endregion

        #region Initialize/Deinitialize
        private void CheckFiles()
        {
            IntPtr hwnd = LoadLibrary(EksplaRC._dllLocation);
            if (IntPtr.Equals(hwnd, IntPtr.Zero))
            {
                filesChecked = false;
                isInitialized = false;
                throw new CmdLib.Primitives.SCAException("Ekspla laser files missing. Unable to initialize laser");
            }
            filesChecked = true;
            FreeLibrary(hwnd);
        }

        private void Connect(int connectionType, int port)
        {
            ErrorCode errorCode = EksplaRC.rcConnect(connectionType, port);
            if (EksplaRC.EqualCodes(errorCode, ErrorCode.OK) || EksplaRC.EqualCodes(errorCode, ErrorCode.ALREADYCONNECTED))
            {
                GetAllDevices();
                isInitialized = true;

                // fix for initialization when laser initialize laser but do not connects
                if (Active.Laser.LaserModel == CmdLib.Parameters.LaserModel.Ekspla_NL20X) 
                {
                    if (!IsConnected()) isInitialized = false;                      
                }
                // end fix 
                return;
            }
            else
            {
                isInitialized = false;
                throw new CmdLib.Primitives.SCAException("Unable to connect with Ekspla laser.");
            }
        }

        public override void Initialize()
        {
            if (isInitialized) return;
            if (!filesChecked) CheckFiles();
            Connect(parameters.connectionType, parameters.port);
            eksplaLaserModel.Initialize(this);
            MonitorData();
        }

        private  void TerminateThreads()
        {
            foreach (Thread t in threads)
            {
                try
                {
                    if (t.IsAlive)
                        t.Abort();
                }
                catch { }
            }
            threads.Clear();
            if (monitor.IsAlive)
            {
                MonitorStop();
                if (monitor.IsAlive)
                    monitor.Abort();
                Thread.Sleep(300);
            }
        }

        public override void DeInitialize()
        {
            watchLaserState = false;
            watchGUI = false;
            MonitorStop();
            eksplaLaserModel.DeInitialize();
            EksplaRC.rcDisconnect();
            TerminateThreads();
            isInitialized = false;
        }

        private  void GetAllDevices()
        {
            ErrorCode errorCode = new ErrorCode();
            StringBuilder sb = new StringBuilder(SIZE);
            devices = new List<EksplaDevice>();
            errorCode = EksplaRC.rcGetFirstDeviceName(sb, SIZE);
            if (EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                devices.Add(new EksplaDevice(sb.ToString()));

            while (errorCode == ErrorCode.OK)
            {
                errorCode = EksplaRC.rcGetNextDeviceName(sb, SIZE);
                if (EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                    devices.Add(new EksplaDevice(sb.ToString()));
            }

            foreach (EksplaDevice device in devices)
            {
                errorCode = EksplaRC.rcGetFirstRegisterName(device.Name, sb, SIZE);
                if (EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                    device.Registers.Add(new EksplaRegister(device.Name, sb.ToString()));

                while (errorCode == ErrorCode.OK)
                {
                    errorCode = EksplaRC.rcGetNextRegisterName(sb, SIZE);
                    if (EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                        device.Registers.Add(new EksplaRegister(device.Name, sb.ToString()));
                }
            }
        }
        #endregion
        #region General

        public void WaitForRun(int timeout, ref bool cancel)
        {
            System.Diagnostics.Stopwatch stopwatch = new System.Diagnostics.Stopwatch();
            stopwatch.Start();
            string runString = GetStringFromState(StateOfLaser.Run);
            while (stopwatch.ElapsedMilliseconds < timeout)
            {
                if (cancel) return;
                Thread.Sleep(1000);
                try
                {
                    if (GetRegisterAsString(mainRegisters.RegGetState).Equals(runString)) return;
                }
                catch { continue; }
            }
            SetState(CmdLib.Interfaces.StateOfLaser.Sleep);
            throw new Exception("Laser is not in RUN state!");
        }

        public EksplaDevice GetDevice(string name)
        {
            foreach(EksplaDevice device in devices)
            {
                if (name.Equals(device.Name))
                    return device;
            }
            return null;
        }

        public void SetHV(bool turnOn, double percent)
        {
            eksplaLaserModel.SetHV(turnOn, percent);
        }
        #endregion
        #region Monitor Laser State
        public void StartStateWatch()
        {
            if (!isInitialized) return;
            watchLaserState = true;
            Thread thread = new Thread(new ThreadStart(WatchLaserState));
            threads.Add(thread);
            thread.Start();
        }

        private void WatchLaserState()
        {
            StringBuilder value = new StringBuilder(SIZE);
            ErrorCode errorCode = ErrorCode.TIMEOUT;
            string laserErrorMessage = "";
            int timestamp = 0;
            int timeout = 1000;
            int errorCount = 0;
            string faultString = GetStringFromState(StateOfLaser.Fault);

            while (watchLaserState)
            {
                Thread.Sleep(499);
                try
                {
                    errorCode = EksplaRC.rcGetRegAsString(mainRegisters.RegGetState.deviceName, mainRegisters.RegGetState.regName, value, SIZE, timeout, ref timestamp);
                    if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                    {
                        errorCount++;
                        if (errorCount < 5) continue;
                        laserErrorMessage = "Lost connection with Ekspla laser!";
                        watchLaserState = false;
                        OnFaulted(new LaserEventArgs(false, true, laserErrorMessage));
                        return;
                    }
                    if (value.ToString().Equals(faultString))
                    {
                        try
                        {
                            EksplaRC.rcGetRegAsString(mainRegisters.RegFault.deviceName, mainRegisters.RegFault.regName, value, SIZE, timeout, ref timestamp);
                            laserErrorMessage = "Laser fault: " + value.ToString(); }
                        catch { laserErrorMessage = "Laser fault!"; }
                        watchLaserState = false;
                        OnFaulted(new LaserEventArgs(true, false, laserErrorMessage));
                        return;
                    }
                    errorCount = 0;
                }
                catch
                {
                    errorCount++;
                    if (errorCount < 5) continue;
                    laserErrorMessage = "Lost connection with Ekspla laser!";
                    watchLaserState = false;
                    OnFaulted(new LaserEventArgs(false, true, laserErrorMessage));
                    return;
                }
            }
        }

        public  void StopStateWatch()
        {
            watchLaserState = false;
        }
        #endregion
        #region Get/Set Registers
        public string GetRegisterAsString(EksplaRegister register)
        {
            return GetRegisterAsString(register.deviceName, register.regName);
        }

        public void StartLogRegister(EksplaRegister register, int queueSize)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            EksplaDevice dev = GetDevice(register.deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcLogRegStart(register.deviceName, register.regName, queueSize);

            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to start log " + register.regName + " for Ekspla laser.");
        }

        public void StopLogRegister(EksplaRegister register)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            EksplaDevice dev = GetDevice(register.deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcLogRegStop(register.deviceName, register.regName);

            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to stop log " + register.regName + " for Ekspla laser.");
        }

        public string GetRegisterFromLogAsString(EksplaRegister register)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            int timestamp = 0;
            StringBuilder value = new StringBuilder(SIZE);

            EksplaDevice dev = GetDevice(register.deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");
            
            ErrorCode errorCode = EksplaRC.rcGetRegFromLogAsString(register.deviceName, register.regName, value, SIZE, ref timestamp);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to get " + register.regName + " for Ekspla laser.");
            return value.ToString();
        }

        public double GetRegisterFromLogAsDouble(EksplaRegister register)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            int timestamp = 0;
            double value = 0.0;

            EksplaDevice dev = GetDevice(register.deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcGetRegFromLogAsDouble(register.deviceName, register.regName, ref value, ref timestamp);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to get " + register.regName + " for Ekspla laser.");
            return value;
        }

        private  string GetRegisterAsString(string deviceName, string regName)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            int timestamp = 0;
            StringBuilder value = new StringBuilder(SIZE);

            EksplaDevice dev = GetDevice(deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcGetRegAsString(dev.Name, regName, value, SIZE, DEFAULT_TIMEOUT, ref timestamp);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to get " + regName + " for Ekspla laser.");
            return value.ToString();
        }

        public double GetRegisterAsDouble(EksplaRegister register)
        {
            return GetRegisterAsDouble(register.deviceName, register.regName);
        }

        private  double GetRegisterAsDouble(string deviceName, string regName)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            int timestamp = 0;
            double value = 0;

            EksplaDevice dev = GetDevice(deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcGetRegAsDouble(dev.Name, regName, ref value, DEFAULT_TIMEOUT, ref timestamp);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to get " + regName + " for Ekspla laser.");
            return value;
        }

        public void SetRegisterFromDouble(EksplaRegister register, double value)
        {
            SetRegisterFromDouble(register.deviceName, register.regName, value);
        }

        private  void SetRegisterFromDouble(string deviceName, string regName, double value)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            EksplaDevice dev = GetDevice(deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcSetRegFromDouble(dev.Name, regName, value);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to set " + regName + " for Ekspla laser.");
        }

        public void SetRegisterFromString(EksplaRegister register, string value)
        {
            SetRegisterFromString(register.deviceName, register.regName, value);
        }

        private  void SetRegisterFromString(string deviceName, string regName, string value)
        {
            if (!isInitialized) throw new CmdLib.Primitives.SCAException("Ekspla laser not initialized.");

            EksplaDevice dev = GetDevice(deviceName);
            if (dev == null) throw new CmdLib.Primitives.SCAException("Can not find the module in Ekspla laser controller.");

            ErrorCode errorCode = EksplaRC.rcSetRegFromString(dev.Name, regName, value);
            if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                throw new CmdLib.Primitives.SCAException("Failed to set " + regName + " for Ekspla laser.");
        }
        #endregion

        public override void Prefire()
        {
            throw new NotImplementedException();
        }

        public override void PostFire()
        {
            throw new NotImplementedException();
        }
        public override bool CanReadFrequency() { return false; }
        public override double GetFrequencyInHz() {
            if (Active.Laser.LaserModel == CmdLib.Parameters.LaserModel.Ekspla_NL20X)
                return GetRegisterAsDouble(Registers.RegSeedFreq);
            return 0.0; }

        public override bool IsFault()
        {
            if (GetState() == StateOfLaser.Fault)
                return true;
            else
                return false;
        }

        public override void PreExecute()
        {
            try
            {
                if (IsConnected())
                {
                    if (IsFault())
                        throw new Exception("Execution can not be started! Ekspla laser fault!");
                    else
                    {
                        if (Active.Laser.UseEksplaHVMon)
                            StartStateWatch();
                        return;
                    }
                }
                throw new SCAException("Execution can not be started! No connection with Ekspla laser!");
            }
            catch(SCAException)
            {
                if (IsConnected())
                {
                    if (IsFault())
                        throw new SCAException("Execution can not be started! Ekspla laser fault!");
                    else
                    {
                        if (Active.Laser.UseEksplaHVMon)
                            StartStateWatch();
                        return;
                    }
                }
                throw new SCAException("Execution can not be started! No connection with Ekspla laser!");
            }
        }

        public override bool IsPowered()
        {
            if (isInitialized) 
                return true;
            else 
                return false;
        }

        public override void PostExecute()
        {
            if (!isInitialized) return;
            StopStateWatch();
            eksplaLaserModel.PostExecute();
        }

        public override bool IsConnected()
        {
            if (!isInitialized) return false;

            StringBuilder temp = new StringBuilder(SIZE);
            int timestamp = 0;
            int timeout = 250;
            int count = 0;
            do
            {
                ErrorCode errorCode = EksplaRC.rcGetRegAsString(mainRegisters.RegGetState.deviceName, mainRegisters.RegGetState.regName, temp, SIZE, timeout, ref timestamp);
                if (!EksplaRC.EqualCodes(errorCode, ErrorCode.OK))
                {
                    count++;
                    Thread.Sleep(10);
                }
                else
                    return true;
            }
            while(count < 3);
            return false;
        }

        public override bool IsInitialized()
        {
            return isInitialized;
        }

        public override string GetFaultMessage()
        {
            return GetRegisterAsString(mainRegisters.RegFault);
        }

        public override StateOfLaser GetState()
        {
            return GetStateFromString(GetRegisterAsString(mainRegisters.RegGetState));
        }

        public override void SetState(StateOfLaser state)
        {
            if (state == StateOfLaser.Fault || state == StateOfLaser.Starting) return;
            SetRegisterFromString(mainRegisters.RegSetState, GetStringFromState(state));
        }

        public void SetShutter(bool open)
        {
            eksplaLaserModel.SetShutter(open);
        }

        public bool ValidateSeedFrequency(int frequencyInHz)
        {
            return eksplaLaserModel.ValidateSeedFrequency(frequencyInHz);
        }

        public StateOfLaser GetStateFromString(string str)
        {
            return eksplaLaserModel.GetStateFromString(str);
        }

        public string GetStringFromState(StateOfLaser state)
        {
            return eksplaLaserModel.GetStringFromState(state);
        }

        public override List<System.Windows.Forms.UserControl> GetExtraGUIs()
        {
            List<System.Windows.Forms.UserControl> list = new List<System.Windows.Forms.UserControl>();
            list.Add(dataStatusGUI);
            list.Add(meanStatusGUI);
            return list;
        }

        public override System.Windows.Forms.UserControl GetStatusGUI()
        {
            return stateStatusGUI;
        }

        public override System.Windows.Forms.Form GetFormW()
        {
            throw new NotImplementedException();
        }
        public override void UpdateSettings(ALaserControlParams param)
        {
            parameters = (EksplaLaserControlParams)param;
        }
    }
 
		
		
		