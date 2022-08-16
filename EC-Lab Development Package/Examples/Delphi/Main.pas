{*******************************************************************************
 Test program.
*******************************************************************************}
unit Main;

interface

uses
  Windows, Messages, SysUtils, Classes, Graphics, Controls, Forms, Dialogs, StdCtrls,
  ExtCtrls, Buttons, ComCtrls,  Menus, ToolWin, Grids, Math, Clipbrd, EClib, VMPfindDevice;

type
  TMainFrm = class(TForm)
    Panel2: TPanel;
    Label1: TLabel;
    Bevel1: TBevel;
    Label18: TLabel;
    edtIPAddress: TEdit;
    btnConnect: TButton;
    btnDisconnect: TButton;
    Label2: TLabel;
    Bevel2: TBevel;
    btnInformations: TButton;
    cmboChannel: TComboBox;
    Label3: TLabel;
    Label4: TLabel;
    cmboTechnique: TComboBox;
    btnStart: TButton;
    btnStop: TButton;
    btnClose: TButton;
    StringGrid1: TStringGrid;
    Label5: TLabel;
    Bevel3: TBevel;
    iLedGray: TImage;
    iLedGreen: TImage;
    Label6: TLabel;
    edtNbPoints: TEdit;
    iLedRed: TImage;
    iLedGray1: TImage;
    btnCopy: TButton;
    btnChannelInfos: TButton;
    ckbReloadFirmware: TCheckBox;
    btnCurrentValues: TButton;
    btnAddDevice: TButton;
    procedure btnConnectClick(Sender: TObject);
    procedure btnStartClick(Sender: TObject);
    procedure btnStopClick(Sender: TObject);
    procedure btnDisconnectClick(Sender: TObject);
    procedure btnInformationsClick(Sender: TObject);
    procedure btnCloseClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormCloseQuery(Sender: TObject; var CanClose: Boolean);
    procedure btnCopyClick(Sender: TObject);
    procedure btnChannelInfosClick(Sender: TObject);
    procedure btnCurrentValuesClick(Sender: TObject);
    procedure btnAddDeviceClick(Sender: TObject);
    procedure edtIPAddressKeyPress(Sender: TObject; var Key: Char);
  private
    { Private declarations }
    FStopAcq: boolean;
    FID: int32;
    FDeviceCode : int32;
    FIsVMP4 : boolean;

    procedure EnableControls(val: boolean);
    procedure ShowErrorMsg(str: string; errorcode: int32);
  public
    { Public declarations }
  end;

const
   CRLF = #13 + #10;
   TAB  = #9;
   ALLOWED_VMP4_DEVICES = [KBIO_DEV_SP100, KBIO_DEV_SP200, KBIO_DEV_SP300,
      KBIO_DEV_VSP300, KBIO_DEV_VMP300, KBIO_DEV_SP240,KBIO_DEV_BP300];

var
  MainFrm: TMainFrm;

implementation

{$R *.DFM}

{-------------------------------------------------------------------------------
Show the error message
-------------------------------------------------------------------------------}
procedure TMainFrm.ShowErrorMsg(str: string; errorcode: int32);
var
   msg: PAnsiChar;
   len: int32;
begin
   msg := PAnsiChar(StrAlloc(255));
   len := 255;
   BL_GetErrorMsg(errorcode, msg, @len);
   ShowMessage(str + ' : ' + strpas(msg));
   StrDispose(msg);
end;

{-------------------------------------------------------------------------------
Enable/disable VCL controls
-------------------------------------------------------------------------------}
procedure TMainFrm.EnableControls(val: boolean);
begin
   btnDisconnect.Enabled := val;
   btnInformations.Enabled := val;
   cmboChannel.Enabled := val;
   cmboTechnique.Enabled := val;
   btnStart.Enabled := val;
   btnStop.Enabled := val;
   StringGrid1.Enabled := val;
   btnChannelInfos.Enabled := val;
   btnCurrentValues.Enabled := val;
   iLedGreen.Visible := val;
end;

{-------------------------------------------------------------------------------
Form create
-------------------------------------------------------------------------------}
procedure TMainFrm.FormCreate(Sender: TObject);
begin
   EnableControls(FALSE);
   FStopAcq := FALSE;
   FID := -1;
   {$ifdef Win32}
      MainFrm.Caption := 'Demo (Win32)';
   {$endif}
   {$ifdef Win64}
      MainFrm.Caption := 'Demo (Win64)';
   {$endif}
end;

{-------------------------------------------------------------------------------
From close query
-------------------------------------------------------------------------------}
procedure TMainFrm.FormCloseQuery(Sender: TObject; var CanClose: Boolean);
begin

   BL_Disconnect(FID);
end;

{-------------------------------------------------------------------------------
Close
-------------------------------------------------------------------------------}
procedure TMainFrm.btnCloseClick(Sender: TObject);
begin
   Close;
end;

{-------------------------------------------------------------------------------
Connection to the potentiostat
-------------------------------------------------------------------------------}
procedure TMainFrm.btnConnectClick(Sender: TObject);
var
   i        : int32;
   res      : int32;
   IP       : string[20];
   Infos    : TDeviceInfos;
   Channels : array[1..NB_CH] of uint8;
   Results  : array[1..NB_CH] of int32;
begin
   Screen.cursor := crHourGlass;
   try
      zeromemory(@Channels, sizeof(Channels));
      zeromemory(@Results, sizeof(Results));
      EnableControls(FALSE);

      {Connection to the potentiostat}
      IP := edtIPAddress.text + #0;
      res := BL_Connect(@IP[1],     {IP address (c-string)}
                         3,         {communication time out (sec)}
                         @FID,      {Instrument identifier}
                         @Infos);   {device infos}
      if res <> 0 then
      begin
         ShowErrorMsg('Connection failed', res);
         Exit;
      end;

      FDeviceCode := Infos.DeviceCode;
      //if BL_IsVMP4Device(FDeviceCode) then (does not work in 32 bits : FDeviceCode not well passed to DLL)
      if FDeviceCode in ALLOWED_VMP4_DEVICES then
         FIsVMP4 := true
      else
         FIsVMP4 := false;

      {Load the firmware}
      cmboChannel.Items.Clear;
      for i := 1 to NB_CH do
      begin
         Channels[i] := Ord(BL_IsChannelPlugged(FID, i - 1));
         if Channels[i] = 1 then
            cmboChannel.Items.Add(inttostr(i));
      end;
      cmboChannel.ItemIndex := 0;
      res := BL_LoadFirmware(FID,                        {Instrument identifier}
                             @Channels,                  {channels selected}
                             @Results,                   {results}
                             NB_CH,                      {length}
                             TRUE,                       {show gauge}
                             ckbReloadFirmware.Checked,  {force reloading the firmware}
                             nil,
                             nil);
      if res <> 0 then
      begin
         ShowErrorMsg('Cannot load the firmware', res);
         Exit;
      end;

      EnableControls(TRUE);
      ShowMessage('Connexion establish to ' + edtIPAddress.text + ' !' + CRLF +
         TAB + 'DeviceCode = ' + inttostr(Infos.DeviceCode) + CRLF +
         TAB + 'RAMsize = ' + inttostr(Infos.RAMsize) + CRLF +
         TAB + 'CPU = ' + inttostr(Infos.CPU) + CRLF +
         TAB + 'NumberOfChannels = ' + inttostr(Infos.NumberOfChannels) + CRLF +
         TAB + 'NumberOfSlots = ' + inttostr(Infos.NumberOfSlots) + CRLF +
         TAB + 'FirmwareVersion = ' + inttostr(Infos.FirmwareVersion) + CRLF +
         TAB + 'FirmwareDate (DD/MM/YYY) = ' + inttostr(Infos.FirmwareDate_dd) + '/'
                                             + inttostr(Infos.FirmwareDate_mm) + '/'
                                             + inttostr(Infos.FirmwareDate_yyyy) + CRLF +
         TAB + 'HTdisplayOn = ' + inttostr(Infos.HTdisplayOn) + CRLF +
         TAB + 'NbOfConnectedPC = ' + inttostr(Infos.NbOfConnectedPC));
   finally
      Screen.Cursor := crDefault;   
   end;
end;

{-------------------------------------------------------------------------------
Disconnect
-------------------------------------------------------------------------------}
procedure TMainFrm.btnDisconnectClick(Sender: TObject);
begin
   BL_Disconnect(FID);
   EnableControls(FALSE);
   FID := -1;
end;

{-------------------------------------------------------------------------------
Informations
-------------------------------------------------------------------------------}
procedure TMainFrm.btnInformationsClick(Sender: TObject);
var
   i       : int32;
   version : PAnsiChar;
   len     : int32;
   str     : string;
begin
   {Read the version of the library}
   len := 12;
   version := PAnsiChar(StrAlloc(len));
   BL_GetLibVersion(version, @len);
   str := 'Library version : ' + version + #13 + #10;
   StrDispose(version);

   {List the channels plugged}
   str := str + 'Channels plugged : ';
   for i := 1 to NB_CH do
      if BL_IsChannelPlugged(FID, i - 1) then
         str := str + inttostr(i) + ', ';

   {Get volume serial number}
   str := str + #13 + #10 + 'Volume serial number : ' + inttostr(BL_GetVolumeSerialNumber);

   ShowMessage(str);
end;


{-------------------------------------------------------------------------------
Add device to the connected devices list
-------------------------------------------------------------------------------}
procedure TMainFrm.btnAddDeviceClick(Sender: TObject);
begin
   fVMPadddevice := TfVMPadddevice.Create(Application);
   fVMPadddevice.ShowModal;
   edtIPAddress.Text :=     fVMPadddevice.SIPAdress;
   if IsTcpIpAddress(edtIPAddress.Text)  then
      begin
         btnConnect.Enabled := True;
      end
   else
      begin
         btnConnect.Enabled := False;
      end;

   fVMPadddevice.Release;
   fVMPadddevice := nil;
   {calls ECglob.ECaddDevice() on fVMPaddDevice.btnSelectDeviceClick()}
end;


{-------------------------------------------------------------------------------
Display channel informations
-------------------------------------------------------------------------------}
procedure TMainFrm.btnChannelInfosClick(Sender: TObject);
var
   res          : int32;
   Channel      : int32;
   ChannelInfos : TChannelInfos;
begin
   {Get the channel selected}
   if cmboChannel.ItemIndex = -1 then
   begin
      ShowMessage('Invalid channel selected !');
      Exit;
   end;
   Channel := strtoint(cmboChannel.Items[cmboChannel.ItemIndex]) - 1; {0 -> 15}

   {Get channel informations}
   res := BL_GetChannelInfos(FID,             {Instrument identifier}
                             Channel,         {channel selected}
                             @ChannelInfos);  {channel informations}
   if res <> 0 then
      ShowErrorMsg('Cannot get channel informations', res)
   else
      ShowMessage('Channel ' + inttostr(ChannelInfos.Channel+1) + ' :' + CRLF +
         '  BoardVersion = ' + inttostr(ChannelInfos.BoardVersion) + CRLF +
         '  BoardSerialNumber = ' + inttostr(ChannelInfos.BoardSerialNumber) + CRLF +
         '  FirmwareCode = ' + inttostr(ChannelInfos.FirmwareCode) + CRLF +
         '  FirmwareVersion = ' + inttostr(ChannelInfos.FirmwareVersion) + CRLF +
         '  XilinxVersion = ' + inttostr(ChannelInfos.XilinxVersion) + CRLF +
         '  AmpCode = ' + inttostr(ChannelInfos.AmpCode) + CRLF +
         '  Zboard = ' + inttostr(ChannelInfos.Zboard) + CRLF +
         '  MemSize = ' + inttostr(ChannelInfos.MemSize) + CRLF +
         '  MemFilled = ' + inttostr(ChannelInfos.MemFilled) + CRLF +
         '  State = ' + inttostr(ChannelInfos.State) + CRLF +
         '  MaxIRange = ' + inttostr(ChannelInfos.MaxIRange) + CRLF +
         '  MinIRange = ' + inttostr(ChannelInfos.MinIRange) + CRLF +
         '  MaxBandwidth = ' + inttostr(ChannelInfos.MaxBandwidth));
end;

{-------------------------------------------------------------------------------
Return oem package absolute directory.
-------------------------------------------------------------------------------}
function GetLibDirectory(): ShortString;
var
   i, L, nbtimes: integer;
label
   Err;
begin
   result := ExtractFilePath(ParamStr(0));
   L := Length(result);
   if L = 0 then
      goto Err;
   if result[L] = '\' then
   begin
      result := Copy(result, 1, L-1);
      L := L-1;
   end;
   for nbtimes := 1 to 2 do
   begin
      for i := L downto 1 do
         if result[i] = '\' then
            break;
      if result[i] = '\' then
      begin
         L := i-1;
         result := Copy(result, 1, L);
      end
      else
         goto Err;
   end;
   result :=  result + '\EC-Lab Development Package\';
   Exit;
Err:
   result := LIB_DIRECTORY;   {relative path}
end;

{-------------------------------------------------------------------------------
Start the procotol selected
-------------------------------------------------------------------------------}
procedure TMainFrm.btnStartClick(Sender: TObject);
var
   i, k          : int32;
   res           : int32;
   Channel       : int32;
   DataInfos     : TDataInfos;
   CurrentValues : TCurrentValues;
   Buf           : TDataBuffer;
   indx          : int32;
   EccParams     : TEccParams;
   EccParamArray : array of TEccParam;
   filename      : string[255];
   val_k         : uint32;
   val_sgl       : single;
   vLibDirectory : ShortString;
begin
   FStopAcq := FALSE;
   edtNbPoints.Text := '0';
   StringGrid1.RowCount := 1;
   StringGrid1.Rows[0].Clear;
   vLibDirectory := GetLibDirectory();

   {Get the channel selected}
   if cmboChannel.ItemIndex = -1 then
   begin
      ShowMessage('Invalid channel selected !');
      Exit;
   end;
   Channel := strtoint(cmboChannel.Items[cmboChannel.ItemIndex]) - 1; {0 -> 15}

   {Get parameters} 
   case cmboTechnique.ItemIndex of
   0: {OCV}
      begin
         if FIsVMP4 then
            filename := vLibDirectory + 'ocv4.ecc' + #0
         else
            filename := vLibDirectory + 'ocv.ecc' + #0;
         SetLength(EccParamArray, 4);
         BL_DefineSglParameter('Rest_time_T',      10.0,        0, @EccParamArray[0]);    {rest for time T (s)}
         BL_DefineSglParameter('Record_every_dE',  0.1,         0, @EccParamArray[1]);    {record every dE (V)}
         BL_DefineSglParameter('Record_every_dT',  0.01,        0, @EccParamArray[2]);    {and at least every dT (s)}
         BL_DefineIntParameter('E_Range',          KBIO_ERANGE_AUTO, 0, @EccParamArray[3]);    {E range}
      end;
   1: {VSCAN}
      begin
         if FIsVMP4 then
            filename := vLibDirectory + 'vscan4.ecc' + #0
         else
            filename := vLibDirectory + 'vscan.ecc' + #0;
         SetLength(EccParamArray, 20);
         {Vertex #0}
         BL_DefineSglParameter ('Voltage_step',      0.0,         0, @EccParamArray[0]);    {E0 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       0, @EccParamArray[1]);    {vs. init}
         BL_DefineSglParameter ('Scan_Rate',         0.0,         0, @EccParamArray[2]);    {scan rate (V/s) - unused}
         {Vertex #1}
         BL_DefineSglParameter ('Voltage_step',      1.0,         1, @EccParamArray[3]);    {E1 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       1, @EccParamArray[4]);    {vs. init}
         BL_DefineSglParameter ('Scan_Rate',         10.0,        1, @EccParamArray[5]);    {scan rate (V/s)}
         {Vertex #2}
         BL_DefineSglParameter ('Voltage_step',      -2.0,        2, @EccParamArray[6]);    {E2 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       2, @EccParamArray[7]);    {vs. init}
         BL_DefineSglParameter ('Scan_Rate',         15.0,        2, @EccParamArray[8]);    {scan rate (V/s)}
         {Vertex #3}
         BL_DefineSglParameter ('Voltage_step',      0.0,         3, @EccParamArray[9]);    {E3 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       3, @EccParamArray[10]);   {vs. init}
         BL_DefineSglParameter ('Scan_Rate',         20.0,        3, @EccParamArray[11]);   {scan rate (V/s)}
         {others}
         BL_DefineIntParameter ('Scan_number',       2,           0, @EccParamArray[12]);   {scan number}
         BL_DefineIntParameter ('N_Cycles',          0,           0, @EccParamArray[13]);   {cycle Nc time}
         BL_DefineSglParameter ('Record_every_dE',   0.01,        0, @EccParamArray[14]);   {record every dE (V)}
         BL_DefineSglParameter ('Begin_measuring_I', 0.4,         0, @EccParamArray[15]);   {measure I from}
         BL_DefineSglParameter ('End_measuring_I',   0.8,         0, @EccParamArray[16]);   {to (% of the step duration)}
         BL_DefineIntParameter ('I_Range',           KBIO_IRANGE_10MA, 0, @EccParamArray[17]);   {I Range}
         BL_DefineIntParameter ('E_Range',           KBIO_ERANGE_AUTO, 0, @EccParamArray[18]);   {E Range}
         BL_DefineIntParameter ('Bandwidth',         KBIO_BW_5, 0, @EccParamArray[19]);   {bandwidth}
      end;
   2: {CP}
      begin
         if FIsVMP4 then
            filename := vLibDirectory + 'cp4.ecc' + #0
         else
            filename := vLibDirectory + 'cp.ecc' + #0;
         SetLength(EccParamArray, 16);
         {Step #0}
         BL_DefineSglParameter ('Current_step',      0.002,       0, @EccParamArray[0]);    {I0 (A)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       0, @EccParamArray[1]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',     0.1,         0, @EccParamArray[2]);    {Step duration (s)}
         {Step #1}
         BL_DefineSglParameter ('Current_step',      -0.001,      1, @EccParamArray[3]);    {I1 (A)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       1, @EccParamArray[4]);    {scan to E1 s. init}
         BL_DefineSglParameter ('Duration_step',     0.2,         1, @EccParamArray[5]);    {Step duration (s)
         {Step #2}
         BL_DefineSglParameter ('Current_step',      0.004,       2, @EccParamArray[6]);    {I2 (A)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       2, @EccParamArray[7]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',     0.1,         2, @EccParamArray[8]);    {Step duration (s)}
         {others}
         BL_DefineIntParameter ('Step_number',       2,           0, @EccParamArray[9]);    {step number}
         BL_DefineIntParameter ('N_Cycles',          0,           0, @EccParamArray[10]);   {cycle Nc time}
         BL_DefineSglParameter ('Record_every_dE',   0.1,         0, @EccParamArray[11]);   {record every dE (V)}
         BL_DefineSglParameter ('Record_every_dT',   0.01,        0, @EccParamArray[12]);   {or every dT (s)}
         BL_DefineIntParameter ('I_Range',           KBIO_IRANGE_10MA, 0, @EccParamArray[13]);   {I Range}
         BL_DefineIntParameter ('E_Range',           KBIO_ERANGE_AUTO, 0, @EccParamArray[14]);   {E Range}
         BL_DefineIntParameter ('Bandwidth',         KBIO_BW_5, 0, @EccParamArray[15]);   {bandwidth}
      end;
   3: {CA}
      begin
         if FIsVMP4 then
            filename := vLibDirectory + 'ca4.ecc' + #0
         else
            filename := vLibDirectory + 'ca.ecc' + #0;
         SetLength(EccParamArray, 16);
         {Step #0}
         BL_DefineSglParameter ('Voltage_step',      1.5,         0, @EccParamArray[0]);    {E0 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       0, @EccParamArray[1]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',     0.1,         0, @EccParamArray[2]);    {Step duration (s)}
         {Step #1}
         BL_DefineSglParameter ('Voltage_step',      -1.0,        1, @EccParamArray[3]);    {E1 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       1, @EccParamArray[4]);    {scan to E1 s. init}
         BL_DefineSglParameter ('Duration_step',     0.2,         1, @EccParamArray[5]);    {Step duration (s)
         {Step #2}
         BL_DefineSglParameter ('Voltage_step',      2.0,         2, @EccParamArray[6]);    {E2 (V)}
         BL_DefineBoolParameter('vs_initial',        FALSE,       2, @EccParamArray[7]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',     0.1,         2, @EccParamArray[8]);    {Step duration (s)}
         {others}
         BL_DefineIntParameter ('Step_number',       2,           0, @EccParamArray[9]);    {step number}
         BL_DefineIntParameter ('N_Cycles',          0,           0, @EccParamArray[10]);   {cycle Nc time}
         BL_DefineSglParameter ('Record_every_dI',   0.1,         0, @EccParamArray[11]);   {record every dI (A)}
         BL_DefineSglParameter ('Record_every_dT',   0.01,        0, @EccParamArray[12]);   {or every dT (s)}
         BL_DefineIntParameter ('I_Range',           KBIO_IRANGE_AUTO, 0, @EccParamArray[13]);   {I Range}
         BL_DefineIntParameter ('E_Range',           KBIO_ERANGE_AUTO, 0, @EccParamArray[14]);   {E Range}
         BL_DefineIntParameter ('Bandwidth',         KBIO_BW_5, 0, @EccParamArray[15]);   {bandwidth}
      end;
   4: {MOD}
      begin
         if FIsVMP4 then
            filename := vLibDirectory + 'mp4.ecc' + #0
         else
            filename := vLibDirectory + 'mp.ecc' + #0;
         SetLength(EccParamArray, 18);
         {Step #0}
         BL_DefineSglParameter ('Value_step',      -0.660,         0, @EccParamArray[0]);    {E (V)}
         BL_DefineBoolParameter('vs_initial',      FALSE,       0, @EccParamArray[1]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',   0.01,         0, @EccParamArray[2]);    {Step duration (s)}
         BL_DefineSglParameter ('Record_every_dM', 1,         0, @EccParamArray[3]);    {Record every dI (A) or dE (V)}
         BL_DefineSglParameter ('Record_every_dT', 0.001,        0, @EccParamArray[4]);    {or every dT (s)}
         BL_DefineIntParameter ('Mode_step',       0,           0, @EccParamArray[5]);    {mode Potentio / Galvano}
         {Step #1}
         BL_DefineSglParameter ('Value_step',      0.0,         1, @EccParamArray[6]);    {I(A)}
         BL_DefineBoolParameter('vs_initial',      FALSE,       1, @EccParamArray[7]);    {vs. init}
         BL_DefineSglParameter ('Duration_step',   0.01,         1, @EccParamArray[8]);    {Step duration (s)}
         BL_DefineSglParameter ('Record_every_dM', 1,         1, @EccParamArray[9]);    {Record every dI (A) or dE (V)}
         BL_DefineSglParameter ('Record_every_dT', 0.001,        1, @EccParamArray[10]);    {or every dT (s)}
         BL_DefineIntParameter ('Mode_step',       1,           1, @EccParamArray[11]);    {mode Potentio / Galvano}
         {others}
         BL_DefineIntParameter ('Step_number',       1,           0, @EccParamArray[12]);    {step number}
         BL_DefineIntParameter ('N_Cycles',          10,           0, @EccParamArray[13]);   {cycle Nc time}
         BL_DefineIntParameter ('Record_every_rc',   1,           0, @EccParamArray[14]);   {cycle Nc time}
         BL_DefineIntParameter ('I_Range',           KBIO_IRANGE_1mA, 0, @EccParamArray[15]);   {I Range}
         BL_DefineIntParameter ('E_Range',           KBIO_ERANGE_2_5, 0, @EccParamArray[16]);   {E Range}
         BL_DefineIntParameter ('Bandwidth',         KBIO_BW_7, 0, @EccParamArray[17]);   {bandwidth}
      end
   else
      begin
         ShowMessage('Unknown technique selected !');
         Exit;
      end;
   end;

   {Load the technique on the channel selected}
   EccParams.len := length(EccParamArray);
   EccParams.pParams := @EccParamArray[0];
   res := BL_LoadTechnique(FID,              {Instrument identifier}
                           Channel,          {channel selected}
                           @filename[1],     {ECC filename (c-string)}
                           EccParams,        {parameters}
                           TRUE,             {first technique}
                           TRUE,             {last technique}
                           True);           {Display parameters}
   if res <> 0 then
   begin
      ShowErrorMsg('Cannot load parameters', res);
      Exit;
   end;

   {Start the technique loaded}
   res := BL_StartChannel(FID, Channel);
   if res <> 0 then
   begin
      ShowErrorMsg('Cannot start the channel selected', res);
      Exit;
   end;
   iLedRed.Visible := TRUE;

   repeat
      {Get data}
      res := BL_GetData(FID,           {instrument identifier}
                        Channel,       {channel selected}
                        @Buf,          {data buffer}
                        @DataInfos,
                        @CurrentValues);   {data informations}
      if res <> 0 then
      begin
         ShowErrorMsg('Cannot get channel data', res);
         Exit;
      end;

      if (DataInfos.NbRaws > 0) and (DataInfos.NbCols > 0) then
      begin
         StringGrid1.ColCount := DataInfos.NbCols + 1;

         {Display data}
         for i := 0 to DataInfos.NbRaws - 1 do
         begin
            indx := StringGrid1.RowCount - 1;
            StringGrid1.Cells[0, indx] := '#' + inttostr(indx);

            for k := 0 to DataInfos.NbCols - 1 do
            begin
               val_k := Buf[k + 1 + i*DataInfos.NbCols];

               if ((k in [0, 1]) or (k in [4..6])) or ((k=DataInfos.NbCols - 1) and (cmboTechnique.ItemIndex>0)) then
                  StringGrid1.Cells[k + 1, indx] := inttostr(val_k)
               else
               begin
                  BL_ConvertNumericIntoSingle(val_k, @val_sgl);
                  StringGrid1.Cells[k + 1, indx] := StringReplace(Format('%.3e', [val_sgl]), '.',
                     FormatSettings.DecimalSeparator, [rfReplaceAll]);
               end;
            end;
            StringGrid1.RowCount := StringGrid1.RowCount + 1;
            StringGrid1.Rows[StringGrid1.RowCount - 1].Clear;
         end;
         edtNbPoints.Text := inttostr(strtointdef(edtNbPoints.Text, 0) + DataInfos.NbRaws);
      end;

      {Stop the channel}
      if FStopAcq then
         BL_StopChannel(FID, Channel);
   until FStopAcq or ((CurrentValues.State <> KBIO_STATE_RUN) and (CurrentValues.MemFilled = 0));
   iLedRed.Visible := FALSE;
end;

{-------------------------------------------------------------------------------
Stop the procotol selected
-------------------------------------------------------------------------------}
procedure TMainFrm.btnStopClick(Sender: TObject);
begin
   FStopAcq := TRUE;
end;

{------------------------------------------------------------------------------}
procedure TMainFrm.edtIPAddressKeyPress(Sender: TObject; var Key: Char);
begin
   if Ord(Key) = vk_Return then
      btnConnect.Enabled := IsTcpIpAddress(edtIPAddress.Text);
end;

{-------------------------------------------------------------------------------
Copy the results into the clipboard
-------------------------------------------------------------------------------}
procedure TMainFrm.btnCopyClick(Sender: TObject);
var
   k, i       : int32;
   StringList : TStringList;
   str        : string;
begin
   StringList := TStringList.Create;
   Clipboard.Open;
   try
      Clipboard.Clear;
      for k := 0 to StringGrid1.RowCount - 1 do
      begin
         str := '';
         for i := 0 to StringGrid1.ColCount - 1 do
            if StringGrid1.Cells[i, k] <> '' then
               str := str + StringGrid1.Cells[i, k] + #9;
         StringList.Add(str);
      end;
      Clipboard.AsText := StringList.Text;
   finally
      Clipboard.Close;
      StringList.Free;
   end;
end;

{-------------------------------------------------------------------------------
Display current values
-------------------------------------------------------------------------------}
procedure TMainFrm.btnCurrentValuesClick(Sender: TObject);
var
   res           : int32;
   Channel       : int32;
   CurrentValues : TCurrentValues;
const
   CRLF = #13 + #10;
begin
   {Get the channel selected}
   if cmboChannel.ItemIndex = -1 then
   begin
      ShowMessage('Invalid channel selected !');
      Exit;
   end;
   Channel := strtoint(cmboChannel.Items[cmboChannel.ItemIndex]) - 1; {0 -> 15}

   {Get channel informations}
   res := BL_GetCurrentValues(FID,              {Instrument identifier}
                              Channel,          {channel selected}
                              @CurrentValues);  {current value}
   if res <> 0 then
      ShowErrorMsg('Cannot get current values', res)
   else
      ShowMessage('Channel ' + inttostr(Channel+1) + ' :' + CRLF +
         '  Ewe(V) = ' + FloatToStr(CurrentValues.Ewe) + CRLF +
         '  Ece(V) = ' + FloatToStr(CurrentValues.Ece) + CRLF +
         '  EweRange = ' + FloatToStr(CurrentValues.EweRangeMin) + '/' + FloatToStr(CurrentValues.EweRangeMax) + CRLF +
         '  Eoverflow = ' + inttostr(CurrentValues.Eoverflow) + CRLF +
         '  I(A) = ' + FloatToStr(CurrentValues.I) + CRLF +
         '  IRange = ' + inttostr(CurrentValues.IRange) + CRLF +
         '  Ioverflow = ' + inttostr(CurrentValues.Ioverflow) + CRLF +
         '  TimeBase(s) = ' + FloatToStr(CurrentValues.TimeBase) + CRLF +
         '  ElapsedTime(s) = ' + FloatToStr(CurrentValues.ElapsedTime));
end;

end.


