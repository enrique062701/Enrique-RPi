//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include <inifiles.hpp>

#include "OptionsFrm.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TOptionsForm *OptionsForm;
//---------------------------------------------------------------------------
__fastcall TOptionsForm::TOptionsForm(TComponent* Owner)
        : TForm(Owner)
{
}
//---------------------------------------------------------------------------

void __fastcall TOptionsForm::FormCreate(TObject *Sender)
{
TIniFile *ini;

   ini = new TIniFile( ChangeFileExt(Application->ExeName, ".INI"));
   PortRG->ItemIndex = ini->ReadInteger("Port", "PortType", 0);
   COMUpDown->Position =  ini->ReadInteger("Port", "ComPortNo", 1);

   delete ini;
}
//---------------------------------------------------------------------------



void __fastcall TOptionsForm::FormClose(TObject *Sender,
      TCloseAction &Action)
{
TIniFile *ini;

   ini = new TIniFile( ChangeFileExt(Application->ExeName, ".INI"));
   ini->WriteInteger( "Port", "PortType", PortRG->ItemIndex );
   ini->WriteInteger( "Port", "ComPortNo", COMUpDown->Position );

   delete ini;
}
//---------------------------------------------------------------------------



void __fastcall TOptionsForm::FormKeyDown(TObject *Sender, WORD &Key,
      TShiftState Shift)
{
   if(Key == VK_ESCAPE) Close();
}
//---------------------------------------------------------------------------


