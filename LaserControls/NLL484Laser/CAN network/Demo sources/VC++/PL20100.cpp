// PL20100.cpp : main project file.

#include "stdafx.h"
#include "Form1.h"
#include "pl20100.h"
#include "REMOTECONTROL_EXPLICIT.H"
 #define DEFINERCFPTRS 
#include "REMOTECONTROL_EXPLICIT.H"

using namespace PL20100;




double attenuation, reprate;

void LoadRCLibrary(void)
{
HMODULE module;
	
static const struct{
	FARPROC *fptr;
	char *fname;
}rcFunctions[] = {
	    {(FARPROC*)&rcConnect,    "rcConnect"},            
        {(FARPROC*)&rcDisconnect,           "rcDisconnect"},         
        {(FARPROC*)&rcGetFirstDeviceName,   "rcGetFirstDeviceName"}, 
        {(FARPROC*)&rcGetNextDeviceName,    "rcGetNextDeviceName"},  
        {(FARPROC*)&rcGetFirstRegisterName, "rcGetFirstRegisterName"}, 
        {(FARPROC*)&rcGetNextRegisterName,  "rcGetNextRegisterName"},  
        {(FARPROC*)&rcIsRegisterWriteable,  "rcIsRegisterWriteable"},  
        {(FARPROC*)&rcIsRegisterNV,         "rcIsRegisterNV"},         
        {(FARPROC*)&rcGetRegFirstEnumValue, "rcGetRegFirstEnumValue"}, 
        {(FARPROC*)&rcGetRegNextEnumValue,  "rcGetRegNextEnumValue"},  
        {(FARPROC*)&rcGetRegAsDouble,       "rcGetRegAsDouble"},       
        {(FARPROC*)&rcSetRegFromDouble,     "rcSetRegFromDouble"},     
        {(FARPROC*)&rcSetRegFromDoubleA,    "rcSetRegFromDoubleA"},    
        {(FARPROC*)&rcSetRegNVFromDouble,   "rcSetRegNVFromDouble"},   
        {(FARPROC*)&rcGetRegAsString,       "rcGetRegAsString"},       
        {(FARPROC*)&rcSetRegFromString,     "rcSetRegFromString"},     
        {(FARPROC*)&rcSetRegFromStringA,    "rcSetRegFromStringA"},    
        {(FARPROC*)&rcSetRegNVFromString,   "rcSetRegNVFromString"},   
        {(FARPROC*)&rcLogRegStart,          "rcLogRegStart"},          
        {(FARPROC*)&rcLogRegStop,           "rcLogRegStop"},           
        {(FARPROC*)&rcGetRegFromLogAsDouble,"rcGetRegFromLogAsDouble"}, 
        {(FARPROC*)&rcGetRegFromLogAsString,"rcGetRegFromLogAsString"}  
   };

   module = LoadLibraryA("REMOTECONTROL.DLL");

   for(int i = 0; i < sizeof(rcFunctions)/sizeof(rcFunctions[0]); i++)
   {
	   *rcFunctions[i].fptr  = GetProcAddress(module, rcFunctions[i].fname);
   }
}

void Connect(void)
{
int result;

	result = rcConnect(0/*USB*/, 0);
	if(result != RMTCTRLERR_OK)
	{
		System::Windows::Forms::MessageBox::Show("Can't connect");
		exit(-1);
	}
	// determine initial attenuator and rep.rate values
    result = rcGetRegAsDouble("SY320100:32", "Attenuator",      &attenuation, 50/*timeout*/, NULL);
    result |= rcGetRegAsDouble("SY320100:32", "Repetition rate", &reprate,     50/*timeout*/, NULL);
	if(result != RMTCTRLERR_OK)
		System::Windows::Forms::MessageBox::Show("Problem reading attenuation and repetition rate from laser");
}

void Run(void)
{
    rcSetRegFromString("SY320100:32", "Command",  "RUN");
}

void Stop(void)
{
    rcSetRegFromString("SY320100:32", "Command",  "STOP");
}

void SetAttenuation(double f)
{
	attenuation = f;
    rcSetRegFromDouble("SY320100:32", "Attenuator",      attenuation);
}

void SetRepRate(double f)
{
	reprate = f;
    rcSetRegFromDouble("SY320100:32", "Repetition rate", reprate);
}

[STAThreadAttribute]
int main(array<System::String ^> ^args)
{
    LoadRCLibrary();

	// Enabling Windows XP visual effects before any controls are created
	Application::EnableVisualStyles();
	Application::SetCompatibleTextRenderingDefault(false); 

	// Create the main window and run it
	Application::Run(gcnew Form1());
	return 0;
}
