//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include <inifiles.hpp>

#include "DemoRemoteControl.h"

#include "RemoteControl.h"

#include <math.h>

#define DefaultTimeout 20

TStringList *PollList;
int  ChartLength;
         
// Start/stop control
char MasterModule[20];
char StartStopRegister[100];
char StartValue[100];
char StopValue[100];

// Output control
char OutputControlEnable;
char OutputControlModule[20];
char OutputControlRegister[100];

// Batch control
char BatchControlEnable;
char BatchControlModule[20];
char BatchControlRegister[100];


char Series1ModuleName[20 ];
char Series1RegisterName[128];
char Series2ModuleName[20 ];
char Series2RegisterName[128];

// ControlItem class is used to create controls dynamically
// from the list of items specified in INI file.
struct ControlItem{
   AnsiString DevName;
   AnsiString RegName;
   enum {Combo, Edit, ReadOnly} type;
   TEdit *edit;
   TComboBox *combobox;
   TButton   *SetButton;
   TButton   *NVButton;
   TCSpinButton *UpDown;
  public:
   ControlItem();
   void Initialize(TWinControl *parent, AnsiString ini);
   int Update(int);
   int Set(void);
   int SetNV(void);
   int Inc(int);
};

#define MAXNUMOFCONTROLS 100
ControlItem controls[MAXNUMOFCONTROLS];  // array of ControlItems
int numofcontrols;

ControlItem::ControlItem() // default constructor used to
{                          // initialize static array of controls
}

// initialize control item. Create edit box or combobox, also
// SET and NV buttons on the fly
void ControlItem::Initialize(TWinControl *parent, AnsiString inistr)
{
static int top = 10;
static int Index;
char tmp[100];
TLabel *lb;
int i;


   strcpy(tmp, inistr.c_str());

   {
      strtok(tmp, "="); // skip ini key

      this->DevName = strtok(NULL, ";");
      this->RegName = strtok(NULL, ";");

      lb = new TLabel(parent);
      lb->Parent = parent;
      lb->Caption = strtok(NULL, ";"); // Displayed register name
      lb->Left = 10;
      lb->Top = top;
      lb->Height = 25;
      lb->Layout = tlCenter;

      if(RMTCTRLERR_OK == rcGetRegFirstEnumValue(this->DevName.c_str(),
                                                 this->RegName.c_str(),
                                                 tmp, sizeof(tmp))
         )
      {
         this->type = Combo;

         this->combobox = new TComboBox(parent);
         this->combobox->Parent = parent;
         this->combobox->Tag = Index;

         this->combobox->OnKeyPress = frmMain->CBKeyPress;
         this->combobox->OnChange   = frmMain->CBChange;

         this->combobox->Left = 350;
         this->combobox->Top = top;

         do{
            this->combobox->Items->Add(tmp);
         } while(
             RMTCTRLERR_OK == rcGetRegNextEnumValue(this->DevName.c_str(),
                                                    this->RegName.c_str(),
                                                    tmp, sizeof(tmp))      );
         this->combobox->Width = 190+24;
      }
      else
      {
         this->type = Edit;

         this->edit = new TEdit(parent);
         this->edit->Parent = parent;
         this->edit->Tag = Index;

         this->edit->OnKeyPress = frmMain->EditEnter;

         this->edit->Left = 350;
         this->edit->Top = top;
         this->edit->Width = 190;
      }

      if(RMTCTRLERR_OK == rcIsRegisterWriteable(this->DevName.c_str(),
                                                this->RegName.c_str(),
                                                &i) && i)
      {
         if(this->type == Edit)
         {
            this->UpDown = new TCSpinButton(parent);
            this->UpDown->Parent = parent;
            this->UpDown->Tag = Index;

            this->UpDown->OnDownClick = frmMain->DownClick;
            this->UpDown->OnUpClick = frmMain->UpClick;

            this->UpDown->Left = this->edit->Left + this->edit->Width +2;
            this->UpDown->Top = top;
         }

         this->SetButton = new TButton(parent);
         this->SetButton->Parent = parent;
         this->SetButton->Tag = Index;

         this->SetButton->OnClick = frmMain->SetClick;

         this->SetButton->Left = 580;
         this->SetButton->Top = top;
         this->SetButton->Caption = "Set";
      }

      if(RMTCTRLERR_OK == rcIsRegisterNV(this->DevName.c_str(),
                                         this->RegName.c_str(),
                                         &i)  && i)
      {
         this->NVButton = new TButton(parent);
         this->NVButton->Parent = parent;
         this->NVButton->Tag = Index;

         this->NVButton->OnClick = frmMain->SetNVClick;

         this->NVButton->Left = this->SetButton->Left + this->SetButton->Width + 10;
         this->NVButton->Top = top;
         this->NVButton->Width /= 2;
         this->NVButton->Caption = "NV";
      }

      top += lb->Height * 140 / 100;  /* 40% line spacing */
      Index++;
   }
}

// update control value.
// argument is used to force update even if editbox or combobox is focused.
// evenfocused=0 allows to not disturb entering new value while
// periodic mass-update is in progress 
int ControlItem::Update(int evenfocused)
{
int Code;
char regval[100];

   Code = rcGetRegAsString(this->DevName.c_str(),
                                       this->RegName.c_str(),
                                       regval, sizeof(regval),
                                       DefaultTimeout, NULL);
   if(RMTCTRLERR_OK == Code)
   {
      switch(this->type)
      {
       case Edit:
         // don't update while user is entering new value
         if(evenfocused || this->edit->Focused() == false) this->edit->Text = regval;
         break;
       case Combo:
         if(evenfocused || this->combobox->Focused() == false) this->combobox->Text = regval;
         break;
      }
   }
   return Code;
}

// SET button handler
int ControlItem::Set(void)
{
int Code = 0;

   switch(this->type)
   {
    case Edit:
      Code = rcSetRegFromString(this->DevName.c_str(), this->RegName.c_str(),
                                this->edit->Text.c_str());
      this->Update(1);
      break;
    case Combo:
      Code = rcSetRegFromString(this->DevName.c_str(), this->RegName.c_str(),
                                this->combobox->Text.c_str());
      this->Update(1);
      break;
   }
   return Code;
}

// NV button handler
int ControlItem::SetNV(void)
{
int Code = 0;

   switch(this->type)
   {
    case Edit:
      rcSetRegNVFromString(this->DevName.c_str(), this->RegName.c_str(),
                         this->edit->Text.c_str());
      this->Update(1);
      break;
    case Combo:
      rcSetRegNVFromString(this->DevName.c_str(), this->RegName.c_str(),
                         this->combobox->Text.c_str());
      this->Update(1);
      break;
   }
   return Code;
}

// Spin Up/Down handler
int ControlItem::Inc(int inc)
{
int Code = 0;
char tmp[100];
char *decpt;  // pointer to dot
char numstrlen; // length of numeric part of string

double incmultiplier;
double d;

   switch(this->type)
   {
    case Edit:
      strcpy(tmp, this->edit->Text.c_str());

      // length of numeric-only string including leading and trailing spaces
      numstrlen = strspn(tmp, " +-.0123456789");

      // remove the rest (dimension etc)
      tmp[numstrlen] = '\0';

      // is there decimal dot in the output?
      decpt  = strchr(tmp, '.');

      // yes. Compute increment multiplier.
      // 1 for 0 digits past the dot, 0.1 for 1 digit past dot, 0.01 for 2 etc
      if(decpt!= NULL) incmultiplier = pow(10.0, -(numstrlen -1 - (decpt-tmp)) );
      else             incmultiplier = 1.0;

      if(numstrlen)
      {
         d = AnsiString(tmp).ToDouble() +  inc * incmultiplier;
         edit->Text = d;

         Code = rcSetRegFromStringA(this->DevName.c_str(), this->RegName.c_str(),
                                    edit->Text.c_str(), true);
      }
      this->Update(1);
      break;
   }
   return Code;
}

//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "CSPIN"
#pragma resource "*.dfm"
TfrmMain *frmMain;
//---------------------------------------------------------------------------
__fastcall TfrmMain::TfrmMain(TComponent* Owner)
        : TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TfrmMain::aConnectExecute(TObject *Sender)
{
static int ControlsAreInitialized; // used to create and init
                                   // controls only once
int    Code;
double ParameterValue;

   Code = rcConnect(0,0);
   ErrorCodeToString(Code, true);
   if (RMTCTRLERR_OK == Code)
   {
      if(!ControlsAreInitialized)
      {
      TIniFile *Ini;
      TStringList *EditItems;

         EditItems = new TStringList;

         Ini = new TIniFile( ExtractFilePath(Application->ExeName) + "REMOTECONTROL.INI");
         Ini->ReadSectionValues("EditList", EditItems);
         delete Ini;

         numofcontrols = EditItems->Count;
         if(numofcontrols > MAXNUMOFCONTROLS) numofcontrols = MAXNUMOFCONTROLS;

         for(int i = 0; i < numofcontrols; i++)
         {
            controls[i].Initialize(ScrollBox, EditItems->Strings[i]);
         }
         delete EditItems;

         ControlsAreInitialized = true;
      }

      Connected = true;
      Xcount =0;
      Series1->Clear();     // Clearing the chart
      Series2->Clear();
      StatusBar->Panels->Items[0]->Text = "Connected";

      Connect1->Enabled = false;
      aDisconnect1->Enabled = true;      // Enabling Disconnect menu item

      if(OutputControlEnable)
      {
         // get actual ouput control state
         rcGetRegAsDouble (OutputControlModule, OutputControlRegister,
                           &ParameterValue, DefaultTimeout, NULL);
         rgOutput->ItemIndex = ParameterValue;
      }

      if(BatchControlEnable)
      {
         // get actual batch mode and batch length
         Code = rcGetRegAsDouble(BatchControlModule,BatchControlRegister,
                          &ParameterValue , DefaultTimeout, NULL);
         rgBatch->ItemIndex = ParameterValue;
      }
   }
}

void __fastcall TfrmMain::aDisconnectExecute(TObject *Sender)
{
   rcDisconnect();
   Connected=false;
   StatusBar->Panels->Items[0]->Text="Disconnected";
   StatusBar->Panels->Items[1]->Text="";
   Connect1->Enabled=true;
   aDisconnect1->Enabled=false;
}

void __fastcall TfrmMain::aOutputControlExecute(TObject *Sender)
{
   rcSetRegFromDouble(OutputControlModule, OutputControlRegister, rgOutput->ItemIndex );
}
void __fastcall TfrmMain::aStartExecute(TObject *Sender)
{
int Code;

   Code= rcSetRegFromString (MasterModule, StartStopRegister, StartValue);
   if (Code != RMTCTRLERR_OK)
      ShowMessagePos(ErrorCodeToString(Code, false),
                     frmMain->Left+ 120 ,frmMain->Top +  220); // Failure, e.g. disconected, need to be inicated
}

void __fastcall TfrmMain::aStopExecute(TObject *Sender)
{
int Code;

   Code= rcSetRegFromString (MasterModule, StartStopRegister, StopValue);
   if (Code != RMTCTRLERR_OK)
      ShowMessagePos(ErrorCodeToString(Code, false),
                     frmMain->Left+ 120 ,frmMain->Top +  220); // Failure need to be inicated
}


AnsiString __fastcall TfrmMain::ErrorCodeToString(int Code, bool PopUpMessage)
{
static const char * const ErrorList[] =
{
   "Comunication succeeded, no error",
   "End of registers list",
   "No config file found" ,
   "Wrong CSV file",
   "Application provided return buffer is too short",
   "No such device name",
   "No such register name",
   "Failed to connect",
   "Timeout waiting for device answer",
   "Register is read only",
   "Register is not NV",
   "Attempt to set value above upper limit",
   "Attempt to set value below bottom limit",
   "Attempt to set not allowed value",
   "Register is not being logged",
   "Not enough memory",
   "No data in the queue yet",
   "Already connected, please disconnect first",
   "Not connected, please connect first"
};

   Code &= ~RMTCTRLERR_LOGOVERFLOW;
   if (PopUpMessage && (Code != RMTCTRLERR_OK))
   {
      if(Code > sizeof(ErrorList)/sizeof(const char*))
         ShowMessage("Unknown error");
      else
         ShowMessage(ErrorList[Code]);
   }
   return ErrorList[Code];
}


void __fastcall TfrmMain::rgBatchClick(TObject *Sender)
{
   rcSetRegFromDouble(BatchControlModule, BatchControlRegister, rgBatch->ItemIndex );
}


void __fastcall TfrmMain::Timer1secTimer(TObject *Sender)      // Polling of parameters list
{
static int PollIndex;
static int SetIndex;
static int OldCode;            // old return code
static int KeepShowingOldCode; // show non-RMTCTRLERR_OK code at least 10 times

int Code;

double ParameterValue;

char tmp[100];
char Value[100];
bool RUNmode;

   if (Connected)
   {
      // Are we running?
      Code = rcGetRegAsString(MasterModule, StartStopRegister,
                              Value, sizeof(Value), DefaultTimeout, NULL);
      if( Code == RMTCTRLERR_OK  &&  !strcmp(Value, StartValue) )
         RUNmode = true;
      else
         RUNmode = false;

      // Are there errors in mastermodule?
      Code=rcGetRegAsString(MasterModule, "Error Code",
                            Value, sizeof(Value)-1 ,DefaultTimeout, NULL);
      if(Code == RMTCTRLERR_OK)
      {
         if (!strcmp(Value,"0000"))
            StatusBar->Panels->Items[2]->Text="OK";
         else
            StatusBar->Panels->Items[2]->Text=AnsiString("Current Error Code = ")
                                                         + MasterModule  + "  "
                                                         + Value;
      }


      // update current poll register
      {
      char *devname;
      char *regname;

         strncpy(tmp, PollList->Strings[PollIndex].c_str(), sizeof(tmp));
         strtok(tmp, "="); // skip key name like "Name0="
         devname = strtok(NULL,";"); //  device name
         regname = strtok(NULL,";"); // skip register name

         if(devname!=NULL && regname!=NULL)
            Code=rcGetRegAsString(devname, regname, Value, sizeof(Value)-1 ,DefaultTimeout, NULL);
         if (Code==RMTCTRLERR_OK)
         {
            sgPList->Cells[1][PollIndex+1] = Value;
         };

         // update poll index
         PollIndex++;
         if(PollIndex >= PollList->Count) PollIndex = 0;
      };

      // update current set register
      {
         controls[SetIndex].Update(0);

         // update set index
         SetIndex++;
         if(SetIndex >= numofcontrols) SetIndex = 0;
      }

      if (RUNmode)   // Chart updated in run mode only
      {
         Code=rcGetRegAsDouble (Series1ModuleName, Series1RegisterName, &ParameterValue , DefaultTimeout, NULL);   //getting value far a chart
         if(Code == RMTCTRLERR_OK)
         {
            Series1->AddXY(Xcount,ParameterValue, 0, clBlack);
            if (Series1->Count() > ChartLength)
               Series1->Delete(0);
            rcGetRegAsDouble (Series2ModuleName, Series2RegisterName, &ParameterValue , DefaultTimeout, NULL);   //getting value far a chart

            Series2->AddXY(Xcount,ParameterValue, 0, clBlack);
            if (Series2->Count() > ChartLength)
               Series2->Delete(0);
            Xcount++;
         }
      }

      // make fast changing codes readable by freezing them for 1s
      if(KeepShowingOldCode) KeepShowingOldCode--;
      if(Code != OldCode && !KeepShowingOldCode)
      {
         OldCode = Code;
         KeepShowingOldCode = 10;

         if(Code == RMTCTRLERR_OK)
            StatusBar->Panels->Items[1]->Text= "";
         else
            StatusBar->Panels->Items[1]->Text= ErrorCodeToString(OldCode, false);
      }
   } //if connected
}



void __fastcall TfrmMain::FormCreate(TObject *Sender)
{
char tmp[100];
char *cptr;
TIniFile *Ini;

   PollList = new TStringList;
   Ini = new TIniFile( ExtractFilePath(Application->ExeName) + "REMOTECONTROL.INI");

   try{
      frmMain->Caption = Ini->ReadString("Product", "Name", "Laser control panel");

      // read polling list
      Ini->ReadSectionValues("PollList",PollList );

      strncpy(MasterModule,       Ini->ReadString("StartStopControl", "MasterModule",       "").c_str(), sizeof(MasterModule) );
      strncpy(StartStopRegister,  Ini->ReadString("StartStopControl", "StartStopRegister",  "").c_str(), sizeof(StartStopRegister) );
      strncpy(StartValue,         Ini->ReadString("StartStopControl", "StartValue",         "").c_str(), sizeof(StartValue) );
      strncpy(StopValue,          Ini->ReadString("StartStopControl", "StopValue",          "").c_str(), sizeof(StopValue) );

      OutputControlEnable =        Ini->ReadInteger("OutputControl",  "OutputControlEnable", 0);
      if(OutputControlEnable) rgOutput->Visible = 1;
      strncpy(OutputControlModule,  Ini->ReadString("OutputControl",  "OutputControlModule","").c_str(), sizeof(OutputControlModule) );
      strncpy(OutputControlRegister,Ini->ReadString("OutputControl",  "OutputControlRegister","").c_str(), sizeof(OutputControlRegister) );

      BatchControlEnable =        Ini->ReadInteger("BatchControl",    "BatchControlEnable", 0);
      if(BatchControlEnable) BatchPanel->Visible = 1;
      strncpy(BatchControlModule, Ini->ReadString( "BatchControl",    "BatchControlModule","").c_str(), sizeof(BatchControlModule) );
      strncpy(BatchControlRegister,Ini->ReadString("BatchControl",    "BatchControlRegister","").c_str(), sizeof(BatchControlRegister) );


      strncpy(Series1ModuleName,  Ini->ReadString("Chart",            "Series1ModuleName",  "").c_str(), sizeof(Series1ModuleName) );
      strncpy(Series2ModuleName,  Ini->ReadString("Chart",            "Series2ModuleName",  "").c_str(), sizeof(Series2ModuleName) );
      strncpy(Series1RegisterName,Ini->ReadString("Chart",            "Series1RegisterName","").c_str(), sizeof(Series1RegisterName) );
      strncpy(Series2RegisterName,Ini->ReadString("Chart",            "Series2RegisterName","").c_str(), sizeof(Series2RegisterName) );
      ChartLength = Ini->ReadInteger("Chart","ChartLength",  200);

      chOut->Title->Text->Clear();
      chOut->Title->Text->Add(AnsiString(Series1ModuleName) + ' ' + AnsiString(Series1RegisterName));
      chOut->Title->Text->Add(AnsiString(Series2ModuleName) + ' ' + AnsiString(Series2RegisterName));
   }
   catch(...)
   {
   }

   // Poll chart header
   sgPList->Cells[0][0] = "Register";
   sgPList->Cells[1][0] = "Value";
   sgPList->RowCount = 1/*header*/ + PollList->Count;
   for( int i = 0; i< PollList->Count; i++)  // Fill grid with parameter names
   {
      strcpy(tmp, PollList->Strings[i].c_str());
      strtok(tmp, "="); // skip key name like "Name0="
      strtok(NULL,";"); // skip device name
      strtok(NULL,";"); // skip register name
      cptr =strtok(NULL,";"); // name to add to the poll spreadsheet
      if(cptr != NULL)
         sgPList->Cells[0][i+1] = cptr;
   };
   delete Ini;
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::FormDestroy(TObject *Sender)
{
   if (Connected )  rcDisconnect();
   delete PollList;
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::btPackClick(TObject *Sender)
{
   rcSetRegFromDouble(BatchControlModule, BatchControlRegister, 2 );
   rgBatch->ItemIndex=1; // Laser enters batch mode
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::SetClick(TObject *Sender)
{
int Code;

   Code = controls[dynamic_cast<TWinControl *>(Sender)->Tag].Set();
   ErrorCodeToString(Code, true);
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::SetNVClick(TObject *Sender)
{
int Code;

   Code = controls[dynamic_cast<TWinControl *>(Sender)->Tag].SetNV();
   ErrorCodeToString(Code, true);
}
//---------------------------------------------------------------------------



void __fastcall TfrmMain::EditEnter(TObject *Sender, char &Key)
{
   if (Key == 13)
   {
      SetClick(Sender);
   }
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::DownClick(TObject *Sender)
{
int Code;

   Code=controls[dynamic_cast<TWinControl *>(Sender)->Tag].Inc(-1);
   ErrorCodeToString(Code, true);
}
//---------------------------------------------------------------------------

void __fastcall TfrmMain::UpClick(TObject *Sender)
{
int Code;

   Code = controls[dynamic_cast<TWinControl *>(Sender)->Tag].Inc(+1);
   ErrorCodeToString(Code, true);
}
//---------------------------------------------------------------------------



void __fastcall TfrmMain::CBKeyPress(TObject *Sender, char &Key)
{
   // this is used to prevent ComboBox edits by user to further
   // prevent OnChange event while combobox text deosn't match list value
   Key = 0;
}
//---------------------------------------------------------------------------


void __fastcall TfrmMain::CBChange(TObject *Sender)
{
   // on combobox change issue set command 
   SetClick(Sender);
}
//---------------------------------------------------------------------------

