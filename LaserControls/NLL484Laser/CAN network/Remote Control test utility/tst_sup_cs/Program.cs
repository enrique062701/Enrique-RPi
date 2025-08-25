using System;
using System.Collections.Generic;
using System.Text;

namespace tst_sup_cs
{
    class Program
    {
        static void Main(string[] args)
        {
            RC rc = new RC();
            bool success;
            List<string> devs;   // list of devices
            List<string> regs;   // list of registers for given device
            List<string> values; // list of register values
            string strng;
            double dbl;
            int timestamp;

            // without initial Connect() call all other functions will return non OK ErrorCode

            // success = rc.Connect(RC.ConnectionType.usb, // choose connection type usb/rs232/tcp
            //	             "" /* gray box S/N, COM port string or TCP host name / IP */, 
            //	             "" /* path to REMOTECONTROL.CSV */ );
	        
            // You may wish to use shorter variant with default empty 2nd and 3rd parameters
            //success = rc.Connect(RC.ConnectionType.usb); // choose connection type usb/rs232/tcp

            // paste C# code here
        }
    }
}
