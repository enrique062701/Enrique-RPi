// tst_sup_managed_cpp.cpp : main project file.

#include "stdafx.h"

using namespace System;
using namespace System::Collections::Generic;

int main(array<System::String ^> ^args)
{
	RC ^rc = gcnew RC();   // RC class instance
	bool success;
	List<String^> ^devs;   // list of devices
	List<String^> ^regs;   // list of registers for given device
	List<String^> ^values; // list of register values
	String^ strng;
	int timestamp;
	double dbl;

	// without initial Connect() call all other functions will return non OK ErrorCode
	//	success = rc->Connect(RC::ConnectionType::usb,
	//	           "" /* gray box S/N, COM port string or TCP host name / IP */, 
	//             "" /* path to REMOTECONTROL.CSV */ );
	//
	// You may also use shorter variant with default empty 2nd and 3rd parameters
	//success = rc->Connect(RC::ConnectionType::usb); // choose connection type usb/rs232/tcp

	// paste C++ code here

	return 0;
}
