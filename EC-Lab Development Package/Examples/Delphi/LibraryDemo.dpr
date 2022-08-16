program LibraryDemo;



uses
  Forms,
  Main in 'Main.pas' {MainFrm},
  EClib in 'EClib.pas',
  VMPFinddevice in 'VMPFinddevice.pas' {fVMPadddevice};

{$R *.RES}

begin
  Application.Initialize;
  Application.CreateForm(TMainFrm, MainFrm);
  Application.CreateForm(TfVMPadddevice, fVMPadddevice);
  Application.Run;
end.
