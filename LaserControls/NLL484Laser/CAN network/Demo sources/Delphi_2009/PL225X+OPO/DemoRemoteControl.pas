unit DemoRemoteControl;
//
interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, REMOTECONTROL, ActnList, Menus, StdCtrls, ExtCtrls,
  ComCtrls, Buttons, TeEngine, Series, TeeProcs, Chart, StrUtils, Grids, IniFiles,
  Gauges, Log;

type
  TfrmMain = class(TForm)
    ActionList: TActionList;
    MainMenu: TMainMenu;
    aConnect: TAction;
    aDisconnect: TAction;
    Connect1: TMenuItem;
    aDisconnect1: TMenuItem;
    Timer1sec: TTimer;
    StatusBar: TStatusBar;
    edParameter: TEdit;
    btStart: TBitBtn;
    btStop: TBitBtn;
    aStart: TAction;
    aStop: TAction;
    btProgram: TButton;
    aProgram: TAction;
    rgOutput: TRadioGroup;
    aOutputControl: TAction;
    aQSWexternal: TAction;
    aSet: TAction;
    btSet: TButton;
    cbParamList: TComboBox;
    Panel1: TPanel;
    chOut: TChart;
    Series1: TFastLineSeries;
    rgBatch: TRadioGroup;
    rgSync: TRadioGroup;
    Series2: TFastLineSeries;
    btPack: TSpeedButton;
    Panel2: TPanel;
    sgPList: TStringGrid;
    Chart: TMenuItem;
    SelectedparametertoChart11: TMenuItem;
    SelectedparametertoChart21: TMenuItem;
    aSetSeries1: TAction;
    aSetSeries2: TAction;
    PopupMenu1: TPopupMenu;
    SelectedparametertoChart12: TMenuItem;
    SelectedparametertoChart22: TMenuItem;
    btProgramSyncMode: TButton;
    edCOM: TEdit;
    StaticText1: TStaticText;
    StaticText2: TStaticText;
    StaticText3: TStaticText;
    mnLog: TMenuItem;
    Panel3: TPanel;
    Panel4: TPanel;
    Label1: TLabel;
    Panel5: TPanel;
    edWave: TEdit;
    Label2: TLabel;
    btSetWave: TButton;
    btProgramWave: TButton;
    Label3: TLabel;
    aSetWave: TAction;
    AProgramWave: TAction;
    procedure aConnectExecute(Sender: TObject);
    procedure aDisconnectExecute(Sender: TObject);
    procedure Timer1secTimer(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure aStartExecute(Sender: TObject);
    procedure aStopExecute(Sender: TObject);
    procedure aProgramExecute(Sender: TObject);
    procedure edParameterKeyPress(Sender: TObject; var Key: Char);
    procedure aOutputControlExecute(Sender: TObject);
    procedure aSetExecute(Sender: TObject);
    procedure cbParamListChange(Sender: TObject);
    procedure rgBatchClick(Sender: TObject);
    procedure rgSyncClick(Sender: TObject);
    procedure btPackClick(Sender: TObject);
    procedure aSetSeries1Execute(Sender: TObject);
    procedure aSetSeries2Execute(Sender: TObject);
    procedure btProgramSyncModeClick(Sender: TObject);
    procedure mnLogClick(Sender: TObject);
    procedure aSetWaveExecute(Sender: TObject);
    procedure AProgramWaveExecute(Sender: TObject);
  private
    { Private declarations }
  function GetCPUregisterAsInteger(Reg:AnsiString):Integer;
  const
  MAX_string = 128;
  type
  NameType = array [0..MAX_string-1] of AnsiChar ;
  public
    { Public declarations }
  const
  DefaultTimeout =100;
  INIfile='REMOTECONTROL.INI';
  PSModuleName='PS5050:22';
  var
  Connected: boolean;
  Timestamp: Integer;
  Xcount:Integer; // current X in chart
  PollList:TStringList;
  SetProgramList:TStringList;
  ChartLength:integer;
  CPUModuleName, OPGModuleName,Series1ModuleName, Series2ModuleName,
  Series1RegisterName, Series2RegisterName: AnsiString;    // Values are read from ini
  ParameterUpdateAllowed: boolean;
  function ErrorCodeToString(Code:Integer; PopUpMessage:boolean):String;   // Comunication code converts to message

  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}
function TfrmMain.GetCPUregisterAsInteger(Reg:AnsiString):integer;   // Read CPU register for radio buttons setting
var ParameterValue:Double;
begin
rcGetRegAsDouble (PAnsiChar(CPUModuleName),PAnsiChar(Reg), ParameterValue , DefaultTimeout, timestamp);
Result:=round(ParameterValue);
end;

procedure TfrmMain.mnLogClick(Sender: TObject);
begin
frmLog.Show;
end;

procedure TfrmMain.aConnectExecute(Sender: TObject);
var
Code:integer;
ParameterValue:Double;
begin
if edCOM.Text='0' then
  Code:= rcConnect(0,0)
else
  Code:= rcConnect(1,StrToInt(edCOM.Text));

ErrorCodeToString(Code, True);
if Code = 0 then
  begin
  ParameterUpdateAllowed:=false;
  Connected:=true;
  Xcount:=0;  Series1.Clear; Series2.Clear;     // Clearing the chart
  StatusBar.Panels[0].Text:='Connected';
  MainMenu.Items[0].Enabled:=false;
  MainMenu.Items[1].Enabled:=true;             // Enabling of Disconnect menu item
  MainMenu.Items[3].Enabled:=true;             // Enabling of Log menu item
  rgOutput.ItemIndex:= getCPUregisterAsInteger('Amplifier On/Off');
  rgBatch.ItemIndex:= getCPUregisterAsInteger('Continuous / Burst mode / Trigger burst');
  rgSync.ItemIndex:= getCPUregisterAsInteger('Synchronization Mode');
  cbParamList.ItemIndex:=0;
  cbParamListChange(Sender);  // Fill actual parameter value in edit
  rcGetRegAsDouble (PAnsiChar(OPGModuleName),'WaveLength', ParameterValue , DefaultTimeout, timestamp);
  edWave.Text:= FloatToStr(ParameterValue);
  ParameterUpdateAllowed:=true;
  end;
end;

procedure TfrmMain.aSetWaveExecute(Sender: TObject);
var Code:integer; ParameterValue:double;
begin
Code:=rcSetRegFromDouble(PAnsiChar(OPGModuleName),'WaveLength', StrToFloat(edWave.Text));
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220);
rcGetRegAsDouble (PAnsiChar(OPGModuleName),'WaveLength', ParameterValue , DefaultTimeout, timestamp);
edWave.Text:= FloatToStr(ParameterValue);
end;

procedure TfrmMain.aDisconnectExecute(Sender: TObject);
begin
rcDisconnect;
Connected:=false;
StatusBar.Panels[0].Text:='Disconnected';
StatusBar.Panels[1].Text:='';
MainMenu.Items[0].Enabled:=true;  // Enabling of Connect menu item
MainMenu.Items[1].Enabled:=false;
end;

procedure SplitNames(S:AnsiString; var ModuleName, RegName, Description: AnsiString);
// Splits string 'xxx  yyyy  zzz' to module name xxx and register name yyy  and description zzz
var
SemicInd:integer;
begin
SemicInd:= AnsiPos ('  ',S);
ModuleName:=copy(S,1,SemicInd-1);
RegName:=copy(S,SemicInd+2,length(S)-SemicInd-1);
SemicInd:= AnsiPos ('  ',RegName);
if SemicInd>0 then
  begin
  S:=RegName;
  RegName:= copy(S,1,SemicInd-1);
  Description:= copy(S,SemicInd+2,length(S)-SemicInd-1);
  end
else Description:='';
end;

procedure CutKeyNames(S:TStringList);  //  Cutts key names from ini file strings
var I, Separator:integer;
begin
if S.Count>0 then
 for I := 0 to S.Count - 1 do
  begin
  Separator:=AnsiPos('=',S.Strings[I]);
  S.Strings[I]:=copy (S.Strings[I],Separator+1, length(S.Strings[I])-Separator);
  end;
end;

procedure TfrmMain.aOutputControlExecute(Sender: TObject);
begin
rcSetRegFromDouble(PAnsiChar(CPUModuleName), 'Amplifier On/Off', rgOutput.ItemIndex );
end;

procedure TfrmMain.aProgramExecute(Sender: TObject);
var ModuleName, RegName, Description: AnsiString;
Code:integer;
begin
SplitNames(SetProgramList.Strings[cbParamList.ItemIndex], ModuleName, RegName , Description);
Code:=rcSetRegNVFromDouble(PAnsiChar(ModuleName),PAnsiChar(RegName), StrToFloat(edParameter.Text));
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220);
cbParamListChange(Sender); // Go for poll actual parameter value after update
end;

procedure TfrmMain.AProgramWaveExecute(Sender: TObject);
var Code:integer;
begin
Code:=rcSetRegNVFromDouble(PAnsiChar(OPGModuleName),'WaveLength', StrToFloat(edWave.Text));
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220);
cbParamListChange(Sender); // Go for poll actual parameter value after update
end;

procedure TfrmMain.aSetExecute(Sender: TObject);
var ModuleName, RegName, Description: AnsiString;
Code:integer;
begin
SplitNames(SetProgramList.Strings[cbParamList.ItemIndex], ModuleName, RegName , Description);
Code:=rcSetRegFromDouble(PAnsiChar(ModuleName),PAnsiChar(RegNAme), StrToFloat(edParameter.Text));
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220);
cbParamListChange(Sender); // Go for poll actual parameter value after update
end;

procedure TfrmMain.aSetSeries1Execute(Sender: TObject);
var
Ini:TCustomIniFile;
Description:AnsiString;
begin
Ini := TIniFile.Create( GetCurrentDir+'/'+INIfile );
  try
    SplitNames(PollList.Strings[sgPList.Row], Series1ModuleName, Series1RegisterName ,Description);
    INI.WriteInteger('Chart','Series1', sgPList.Row );
    Series1.Clear;
    chOUt.SeriesList[0].Title:=Description;
  finally
    Ini.Free
  end;
end;

procedure TfrmMain.aSetSeries2Execute(Sender: TObject);
var
Ini:TCustomIniFile;
Description:AnsiString;
begin
Ini := TIniFile.Create( GetCurrentDir+'/'+INIfile );
  try
    SplitNames(PollList.Strings[sgPList.Row], Series2ModuleName, Series2RegisterName ,Description);
    INI.WriteInteger('Chart','Series2', sgPList.Row );
    Series2.Clear;
    chOUt.SeriesList[1].Title:=Description;;
  finally
    Ini.Free
  end;
end;

procedure TfrmMain.aStartExecute(Sender: TObject);
var Code:integer;
begin
Code:= rcSetRegFromString (PAnsiChar(CPUModuleName),'State','ON');
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220); // Failure, e.g. disconected, need to be inicated
end;

procedure TfrmMain.aStopExecute(Sender: TObject);
var Code:integer;
begin
Code:= rcSetRegFromString (PAnsiChar(CPUModuleName),'State','OFF');
if Code <> 0 then ShowMessagePos(ErrorCodeToString(Code, False), frmMain.Left+ 120 ,frmMain.top +  220); // Failure need to be inicated
end;

procedure TfrmMain.btPackClick(Sender: TObject);
begin
rcSetRegFromDouble(PAnsiChar(CPUModuleName), 'Continuous / Burst mode / Trigger burst', 2 );
rgBatch.ItemIndex:=1; // Laser enters batch mode
end;

procedure TfrmMain.btProgramSyncModeClick(Sender: TObject);
begin
rcSetRegNVFromDouble(PAnsiChar(CPUModuleName), 'Synchronization Mode', rgSync.ItemIndex );
end;

procedure TfrmMain.cbParamListChange(Sender: TObject);   // Fills parameter edit with actual vaule
var ModuleName, RegName , Description: AnsiString;
Value: Double;
Code:integer;
begin
SplitNames(SetProgramList.Strings[cbParamList.ItemIndex], ModuleName, RegName , Description);
Code:=rcGetRegAsDouble(PAnsiChar(ModuleName),PAnsiChar(RegName), Value ,DefaultTimeout, Timestamp);
if Code=0 then edParameter.Text:= FloatToStr (Value);
end;

procedure TfrmMain.edParameterKeyPress(Sender: TObject; var Key: Char);
begin
if Key = #13 then
  aSetExecute(Sender);
end;

function TfrmMain.ErrorCodeToString(Code:Integer; PopUpMessage:boolean):String;
const
  ErrorList: Array[0..18] of string = ('Comunication succeeded, no error',
'End of registers list','No config file found' ,'Wrong CSV file'
,'Application provided return buffer is too short','No such device name',
'No such register name','Failed to connect','Timeout waiting for device answer','Register is read only'
,'Register is not NV','Attempt to set value above upper limit'
,'Attempt to set value below bottom limit','Attempt to set not allowed value','Register is not being logged'
,'Not enough memory','No data in the queue yet','Already connected, please disconnect first'
,'Not connected, please connect first');
begin
if PopUpMessage and (Code > 0) then
      ShowMessage(ErrorList[Code])
else ErrorCodeToString:= ErrorList[Code];
end;

procedure TfrmMain.FormCreate(Sender: TObject);
var I:integer; s,s1, Description:ansistring;
Ini:TCustomIniFile;
begin
  chOUt.Title.Text.clear;
PollList:= TStringList.Create;
SetProgramList:= TStringList.Create;
Ini := TIniFile.Create(GetCurrentDir+'/'+INIfile);    //  ChangeFileExt( Application.ExeName, '.INI' )
chOUt.Title.Text.clear;    // Chart titles
chOUt.Title.Text.Add('');
chOUt.Title.Text.Add('');
try
  frmMain.Caption := Ini.ReadString('Product','Name','Laser control panel');
  Ini.ReadSectionValues('PollList',PollList );
  Ini.ReadSectionValues('SetProgramList',SetProgramList);
  CutKeyNames (PollList);
  CutKeyNames (SetProgramList);
  CPUModuleName:=Ini.ReadString('Modules','CPUModuleName',  '');
  OPGModuleName:=Ini.ReadString('Modules','OPGModuleName',  'PG503:31');
  edCOM.Text :=Ini.ReadString('COM','PortNr',  '0');
  sgPList.Row:= Ini.ReadInteger('Chart','Series1', 1);
  aSetSeries1Execute(Sender);    // Set Chart series1
  sgPList.Row:=Ini.ReadInteger('Chart','Series2', 2);
  aSetSeries2Execute(Sender);    // Set Chart series1
  ChartLength:=Ini.ReadInteger('Chart','ChartLength',  200);
finally
    Ini.Free;
end;

Connected:=false;
for I := 0 to PollList.Count - 1 do  // Fill grid with parameter names
    begin
    SplitNames(PollList.Strings[I] ,s, s1, Description);
    sgPList.Cells[0,I]:= Description;
    end;
for I := 0 to SetProgramList.Count - 1 do  // Fill combo box with strings
  begin
  SplitNames(SetProgramList.Strings[I] ,s, s1, Description);
  cbParamList.Items.Add(Description);
  end;
end;

procedure TfrmMain.FormDestroy(Sender: TObject);
var
Ini:TCustomIniFile;
begin
if Connected then  rcDisconnect;
PollList.Free;
SetProgramList.Free;
Ini := TIniFile.Create( GetCurrentDir+'/'+INIfile );   //writing COM port
  try
    INI.WriteString('COM','PortNr', edCOM.Text );
  finally
    Ini.Free
  end;
end;

procedure TfrmMain.rgBatchClick(Sender: TObject);
begin
rcSetRegFromDouble(PAnsiChar(CPUModuleName), 'Continuous / Burst mode / Trigger burst', rgBatch.ItemIndex );
end;

procedure TfrmMain.rgSyncClick(Sender: TObject);
begin
if ParameterUpdateAllowed then
    rcSetRegFromDouble(PAnsiChar(CPUModuleName), 'Synchronization Mode', rgSync.ItemIndex );
end;

procedure TfrmMain.Timer1secTimer(Sender: TObject);      // Polling of parameters list
var
Value: array [0..MAX_string-1] of AnsiChar;
I, Code:integer;
ParameterValue:Double;
RUNmode:boolean;
ModuleName, RegName, Description: AnsiString;
begin
if Connected then
  begin
  for I := 0 to PollList.Count-1 do  // Fill poll list
    begin
    SplitNames(PollList.Strings[I] ,ModuleName, RegName, Description);   // Split parameter string to module, register and parameter names
    Code:=rcGetRegAsString(PAnsiChar(ModuleName),PAnsiChar(RegName), @Value, MAX_string ,DefaultTimeout, Timestamp);
    if Code=0 then
       begin
       sgPList.Cells[1,I]:=String(Value);
       if (I=0) then      // Laser status on the first line
         begin
         if  (string(Value)='ON') then
           RUNmode:=true
         else
           begin
           RUNmode:=false;
           if  (string(Value)='Failure') then       // Polling of curren fault code
            begin
            Code:=rcGetRegAsString(PAnsiChar(CPUModuleName),'Error Code', @Value, MAX_string ,DefaultTimeout, Timestamp);
            if String(Value)='0000' then
               StatusBar.Panels[2].Text:='Laser status OK'   // Fault condition is gone
            else
               StatusBar.Panels[2].Text:='Current Fault Code = '+ string(CPUModuleName)+ '  ' +string(Value);
            end
         else
            StatusBar.Panels[2].Text:='No Faults is triggered';
            end;
         end;
       end;
    end;
  Code:=rcGetRegAsDouble (PAnsiChar(Series2ModuleName),PAnsiChar(Series2RegisterName), ParameterValue , DefaultTimeout, timestamp);   //getting value far a chart
  if Code=0 then   // Add point to Chart1
      begin
       Series2.AddXY(Xcount,ParameterValue);
      if Series2.Count>ChartLength then Series2.Delete(0);
      end;
  Code:=rcGetRegAsDouble (PAnsiChar(Series1ModuleName),PAnsiChar(Series1RegisterName), ParameterValue , DefaultTimeout, timestamp);   //getting value far a chart
  if Code=0 then  // Add point to Chart2
      begin
      Series1.AddXY(Xcount,ParameterValue);
      if Series1.Count>ChartLength then Series1.Delete(0);
       inc(Xcount);
      end;
  StatusBar.Panels[1].Text:= ErrorCodeToString(Code, False);  // Fill status panel
  end;
end;



end.
