program ProjectDemoRemote;

uses
  Forms,
  DemoRemoteControl in 'DemoRemoteControl.pas' {frmMain},
  REMOTECONTROL in 'REMOTECONTROL.PAS',
  log in 'log.pas' {frmLog};

{$R *.res}

begin
  Application.Initialize;
  Application.MainFormOnTaskbar := True;
  Application.CreateForm(TfrmMain, frmMain);
  Application.CreateForm(TfrmLog, frmLog);
  Application.Run;
end.
