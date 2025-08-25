// tst_sup_unmanaged_c.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include "REMOTECONTROL.H"

int rcHandle;     // connection handle
int error;        // error code
double dbl;       // double return value
char strng[100];  // string return value
int timestamp;    // timestamp

int _tmain(int argc, _TCHAR* argv[])
{
	// without initial rcConnect2 call all other functions will return non OK return code
	// error = rcConnect2(&rcHandle, 0/* 0- USB, 1-RS232, 2-TCP*/,
	//                              "" /* gray box S/N, COM port string or TCP host name / IP */, 
	//                              "" /* path to REMOTECONTROL.CSV */ );

	// paste C code here

	return 0;
}
