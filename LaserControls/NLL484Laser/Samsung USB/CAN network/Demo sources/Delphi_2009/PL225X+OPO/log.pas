unit log;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ExtCtrls, TeEngine, Series, TeeProcs, Chart, REMOTECONTROL, StdCtrls,
  ComCtrls, Buttons, CheckLst, ImgList, ExtDlgs;

type
  TfrmLog = class(TForm)
    Chart1: TChart;
    btStartScan: TButton;
    btStopScan: TButton;
    BitBtn1: TBitBtn;
    Panel1: TPanel;
    clbRegisterSelection: TCheckListBox;
    Series2: TFastLineSeries;
    Series3: TFastLineSeries;
    Series4: TFastLineSeries;
    Timer2: TTimer;
    Series1: TFastLineSeries;
    ImageList1: TImageList;
    procedure FormShow(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btStartScanClick(Sender: TObject);
    procedure btStopScanClick(Sender: TObject);
    procedure BitBtn1Click(Sender: TObject);
    procedure Timer2Timer(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    { Private declarations }
  const
  MAX_string = 128;
  MaxSeries = 4;
  MaxChartLength = 30000;
  type
  NameType = array [0..MAX_string-1] of AnsiChar ;
  var
    OnLog:Boolean;
    ConnectedStatus:boolean;
    StartTime:integer;
    NamesOnLog:TStringList;
  public
    { Public declarations }
  end;

var
  frmLog: TfrmLog;

implementation
uses DemoRemoteControl;

{$R *.dfm}

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

procedure TfrmLog.BitBtn1Click(Sender: TObject);
begin
Close;
end;

procedure TfrmLog.btStartScanClick(Sender: TObject);
var code,  I:integer;
ModuleName, RegName, Description: AnsiString;
begin
For I:=0 to MaxSeries-1 do
  begin
  Chart1.SeriesList[I].Clear;
  chart1.SeriesList[I].Title:='---';
  end;
clbRegisterSelection.Enabled:= false;
NamesOnLog.Clear;
OnLog:=true;
StartTime:=0;
for I := 0 to clbRegisterSelection.Items.Count - 1 do
    begin
    if clbRegisterSelection.Checked[I]and(NamesOnLog.Count<4) then
      begin
      SplitNames(clbRegisterSelection.Items[I],ModuleName, RegName, Description);
      Code:=  rcLogRegStart(PAnsiChar(ModuleName),PAnsiChar(RegName),10000);
      if Code=0 then
         begin
         chart1.SeriesList[NamesOnLog.count].Title:=clbRegisterSelection.Items[I];
         NamesOnLog.Add(clbRegisterSelection.Items[I]);
         end;
      end;
    end;
end;

procedure TfrmLog.btStopScanClick(Sender: TObject);
var code,  I:integer;
ModuleName, RegName, Description: AnsiString;
begin
OnLog:=false;
clbRegisterSelection.Enabled:= true;
for I := 0 to NamesOnLog.Count - 1 do
    begin
    SplitNames(NamesOnLog.Strings[I],ModuleName, RegName, Description);
    Code:=  rcLogRegStop(PAnsiChar(ModuleName),PAnsiChar(RegName));
    end;
end;

procedure TfrmLog.FormClose(Sender: TObject; var Action: TCloseAction);
var code:integer;
begin
end;

procedure TfrmLog.FormCreate(Sender: TObject);
begin
NamesOnLog:=TStringList.Create;
end;

procedure TfrmLog.FormDestroy(Sender: TObject);
begin
NamesOnLog.Free;
end;

procedure TfrmLog.FormShow(Sender: TObject);
var code, CodeD:integer;
Timestamp: Integer;
DevName, RegName: NameType;
begin
// Filling Register selection box with names
CodeD:= rcGetFirstDeviceName(@DevName, MAX_string);
while CodeD=0 do
  begin
  Code:= rcGetFirstRegisterName(@DevName, @RegName, MAX_string);
  while Code=0 do
    begin
    clbRegisterSelection.Items.Add(String(DevName)+'  '+ String(RegName));
    Code:= rcGetNextRegisterName(@RegName, MAX_string);
    end;
  CodeD:= rcGetNextDeviceName(@DevName, MAX_string);
  end;
// End of filling
end;



procedure TfrmLog.Timer2Timer(Sender: TObject);
var code, I:integer;
ParameterValue:Double;
Timestamp: Integer;
ModuleName, RegName, Description: AnsiString;
begin
for I := 0 to NamesOnLog.Count - 1 do     // repeat cycle for every series
  begin
  SplitNames(NamesOnLog.Strings[I] ,ModuleName, RegName, Description);
  repeat
  Code:=rcGetRegFromLogAsDouble (PAnsiChar(ModuleName),PAnsiChar(RegName), ParameterValue , timestamp);   //getting value for a chart
  if Code=0 then
      begin
      if OnLog then
        begin
        if StartTime=0 then StartTime:= TimeStamp;                                    // Memorise reference time
        Chart1.SeriesList[I].AddXY((timestamp-StartTime)/1000,ParameterValue);      // X is time in seconds relative to reference time
        if Chart1.SeriesList[I].Count > MaxChartLength then
           Chart1.SeriesList[I].Delete(0);     // Delete first
        end;
      end;
  until Code<>0;
  end;

end;

end.
