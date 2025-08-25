//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
USERES("ProjectDemoRemote.res");
USEFORM("DemoRemoteControl.cpp", frmMain);
USELIB("REMOTECONTROL.lib");
//---------------------------------------------------------------------------
WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int)
{
        try
        {
                 Application->Initialize();
                 Application->CreateForm(__classid(TfrmMain), &frmMain);
                 Application->Run();
        }
        catch (Exception &exception)
        {
                 Application->ShowException(&exception);
        }
        return 0;
}
//---------------------------------------------------------------------------
