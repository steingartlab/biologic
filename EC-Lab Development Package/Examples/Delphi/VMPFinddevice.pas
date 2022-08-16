{-------------------------------------------------------------------------------

  search and select a device in the broadcast list
 (c) Bio-Logic company, 1997 - 2013

-------------------------------------------------------------------------------}
unit VMPFinddevice;

interface

uses
  Windows, SysUtils, Classes, Graphics, Controls, Forms,
  Dialogs, Grids, ExtCtrls, StdCtrls, Buttons;

type
  TEventOnClickSelect  = procedure of object;
  TEventOnClickCancel  = procedure of object;
  TShowInfosFrm        = procedure of object;
  puInt32  = ^uInt32;

  TBL_Find    = function(aLstDev : PChar; aLength : puInt32; aNbDevice : puInt32) : Int32; stdcall;
  TBL_SetCfg  = function(aIP : PChar; aNewCfg : PChar) : Int32; stdcall;
  TBL_GetErr  = procedure(aErrCode : Int32; aErrMsg : PChar; aLength : puInt32); stdcall;
  TBL_Init    = procedure(wPath : PChar);

  TfVMPadddevice = class(TForm)
    PanelDevice: TPanel;
    btnRefresh: TSpeedButton;
    StringGridDevices: TStringGrid;
    lblOnLine: TLabel;
    GroupBox5: TGroupBox;
    btnSelectDevice: TBitBtn;
    btnClose: TBitBtn;
    procedure FormCreate(Sender: TObject);
    procedure btnRefreshClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure btnSelectDeviceClick(Sender: TObject);


  private
    { Private declarations }
    FFindUSBdevices : boolean;           {Search USB device}

    FSIPAdress : string;

    FShowInfosFrm   : TShowInfosFrm;
    FSortInProgress : boolean;           {sort in progress}
    FPrevSelIP      : shortstring;       {previous IP selected}
    FRefreshDone    : boolean;
    mHandleLibFind        : integer;

    FBL_FindEChemDev      : TBL_Find;
    FBL_FindEChemEthDev   : TBL_Find;
    FBL_Init_Path         : TBL_Init;
    FBL_SetCfg            : TBL_SetCfg;
    FBL_GetErrMsg         : TBL_GetErr;

    procedure ClearStringGridList;
    procedure EnableStringGrid(enable: boolean);

    function  LoadFindLibrary : boolean;
    procedure FreeFindLibrary;

  public
    { Public declarations }
    constructor Create( AOwner        : TComponent;
                        aClickSelect  : TEventOnClickSelect;
                        aClickCancel  : TEventOnClickCancel;
                        aShowInfosFrm : TShowInfosFrm;
                        aLoadFlash    : TEventOnClickCancel); reintroduce; overload;
    destructor Destroy; override;
    property FindUSBdevices: boolean read FFindUSBdevices write FFindUSBdevices;
    property SIPAdress: string read FSIPAdress write FSIPAdress;

  end;

var
   fVMPadddevice: TfVMPadddevice;

   function BLExtractStringsEmpty(Separators, WhiteSpace: TSysCharSet; Content: PChar; Strings: TStrings): Integer;
   function IsTcpIpAddress(sIPAddress: ShortString): boolean; overload;  {Test if IPAdress is a valid TCP/IP address}


implementation

{$R *.dfm}

const

   SOFT_NAME            = 'LibraryDemo';
   {TCP/IP}
   ETHERNET_STR       = 'Ethernet';
   USB_STR            = 'USB';

   NB_MAX_DEVICE_FOUND   = 50;
   LIGHT_GREEN           = $C0FFC0;
   ORANGE                = $80C0FF;

   {StringGridDevices columns}
   COL_COMM    = 0;
   COL_ADDRESS = 1;

   {Comm type}
   COMM_NONE      = 0;
   COMM_TCPIP     = 1;
   COMM_USB       = 2;
   COMM_VIRTUAL   = 3;

   DO_BEEP = True;
   NO_BEEP = False;

   {dll Name}
   BLFIND_DLL_DIR  = '..\..\EC-Lab Development Package\';

 {$IFDEF WIN64}
   BLFIND_DLL_NAME = 'blfind64.dll';
{$ELSE}
   BLFIND_DLL_NAME = 'blfind.dll';
{$ENDIF}

type
   TByteArray16 = array [0..15] of byte;
   TArray25ofString = array[1..NB_MAX_DEVICE_FOUND] of ansistring;
   TArray25ofByte16 = array[1..NB_MAX_DEVICE_FOUND] of TByteArray16;

var
   NbDeviceFound        : integer;
   DeviceFoundComm      : TArray25ofString;  {'USB' or 'ethernet'}
   DeviceFoundIP        : TArray25ofString;
   DeviceFoundNM        : TArray25ofString;
   DeviceFoundGW        : TArray25ofString;
   DeviceFoundMAC       : TArray25ofString;
   DeviceFoundID        : TArray25ofString;
   DeviceFoundSerial    : TArray25ofByte16;
   DeviceFoundSerial_   : TArray25ofString;
   DeviceFoundName      : TArray25ofByte16;
   DeviceFoundDevice    : TArray25ofString;
   modindex             : integer;
   EdtIPAddress_Text    : ShortString;


{-------------------------------------------------------------------------------
Extract string
-------------------------------------------------------------------------------}
function BLExtractStringsEmpty(Separators, WhiteSpace: TSysCharSet; Content: PChar; Strings: TStrings): Integer;
var
  Head, Tail: PChar;
  EOS, InQuote: Boolean;
  QuoteChar: Char;
  Item: string;
begin
  Result := 0;
  if (Content = nil) or (Content^=#0) or (Strings = nil) then Exit;
  Tail := Content;
  InQuote := False;
  QuoteChar := #0;
  Strings.BeginUpdate;
  try
    repeat
      while (CharInSet(Tail^, WhiteSpace + [#13, #10])) do
        Tail := StrNextChar(Tail);
      Head := Tail;
      while True do
      begin
        while (InQuote and not CharInSet(Tail^, [QuoteChar, #0])) or
          not (CharInSet(Tail^, Separators + [#0, #13, #10, '''', '"'])) do Tail := StrNextChar(Tail);

        if CharInSet(Tail^, ['''', '"']) then
        begin
          if (QuoteChar <> #0) and (QuoteChar = Tail^) then
            QuoteChar := #0
          else if QuoteChar = #0 then
            QuoteChar := Tail^;
          InQuote := QuoteChar <> #0;
          Tail := StrNextChar(Tail);
        end else Break;
      end;
      EOS := Tail^ = #0;
      if (Head^ <> #0) then
      begin
        if Strings <> nil then
        begin
          SetString(Item, Head, Tail - Head);
          Strings.Add(Item);
        end;
        Inc(Result);
      end;
      Tail := StrNextChar(Tail);
    until EOS;
  finally
    Strings.EndUpdate;
  end;
end;

{-------------------------------------------------------------------------------
Test if sIPAdress is a valid TCP/IP address.
   . IP address format : a.b.c.d    with a,b,c,d in [0,255]
   . convert sIPaddress into an int32
-------------------------------------------------------------------------------}
function IsTcpIpAddress(sIPaddress: ShortString; var i32IPAddress: uint32): boolean; overload;

   {...........................................................................}
   function ExtractFirstNum(var IPstr: ShortString; var firstNum: integer): boolean;
   var dotPos: integer;
   begin
      result := false;
      dotPos := pos('.',IPstr);
      if (dotPos <= 1) or (dotPos >= 5) then exit;
      firstNum := StrToIntDef(Copy(IPstr,0,dotPos - 1),-1);
      if (firstNum < 0) or (firstNum > $ff) then exit;
      IPstr := Copy(IPstr,dotPos + 1,length(IPstr));
      result := true;
   end;
   {...........................................................................}

var a,b,c,d: integer;
begin
   result := False;
   i32IPAddress := 0;
   if (length(sIPAddress) <= 0) or (length(sIPAddress) > 15) then exit;
   if not ExtractFirstNum(sIPaddress,a) then exit;
   if not ExtractFirstNum(sIPaddress,b) then exit;
   if not ExtractFirstNum(sIPaddress,c) then exit;
   if (pos('.',sIPaddress) > 0) then exit;
   d := StrToIntDef(sIPaddress,-1);
   if (d < 0) or (d > $ff) then exit;
   i32IPAddress := (a shl 24)+ (b shl 16) + (c shl 8) + d;
   result := true;
end;

{-------------------------------------------------------------------------------
Is TcpIp Address  valid
-------------------------------------------------------------------------------}
function IsTcpIpAddress(sIPAddress: ShortString): boolean;
var i32IPAddress: uint32;
begin
   result := IsTcpIpAddress(sIPAddress,i32IPAddress);
end;

{-------------------------------------------------------------------------------
Pascal message box (with strings instead of PAnsiChar).
-------------------------------------------------------------------------------}
function MsgBoxPas(ChMsg,ChTitle: UnicodeString; Flags: Word; DoBeep: boolean): integer; overload;
var WMsg,WTitle: WideString;
begin
	if DoBeep then messageBeep(0);
   WMsg := ChMsg;
   WTitle := ChTitle;
	result := Application.MessageBox(PWideChar(WMsg),PWideChar(WTitle),Flags);
end;

{-------------------------------------------------------------------------------
Message box
-------------------------------------------------------------------------------}
function MsgBoxPas(ChMsg,ChTitle: UnicodeString; Flags: Word): integer; overload;
begin
   result := MsgBoxPas(ChMsg,ChTitle,Flags,DO_BEEP);
end;

{-------------------------------------------------------------------------------
string conversion
-------------------------------------------------------------------------------}
function blStrToPWideChar(var Ch: WideString): PWideChar;
var L: integer;
begin
	L := Length(Ch);
   if L = 0 then
   begin
      Ch := #0;
   end
   else if Ch[L] <> #0 then
   begin
       Ch := Ch + #0;
   end;
   result := @(Ch[1]);
end;


{-------------------------------------------------------------------------------
Create TfVMPadddevice object
-------------------------------------------------------------------------------}
constructor TfVMPadddevice.Create(AOwner        : TComponent;
                                  aClickSelect  : TEventOnClickSelect;
                                  aClickCancel  : TEventOnClickCancel;
                                  aShowInfosFrm : TShowInfosFrm;
                                  aLoadFlash    : TEventOnClickCancel);
begin
   inherited Create(AOwner);
   FShowInfosFrm   := aShowInfosFrm;

   FreeFindLibrary;
end;

{-------------------------------------------------------------------------------
Form Create
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.FormCreate(Sender: TObject);
begin
   NbDeviceFound     := 0;

   StringGridDevices.ColCount   := 2;
   StringGridDevices.Rows[0][0] := 'Comm';
   StringGridDevices.Rows[0][1] := 'Address';
   ClearStringGridList;

   FFindUSBdevices := FALSE;

   btnSelectDevice.Visible := True;
   btnClose.Visible        := True;

   FSortInProgress := FALSE;
   FPrevSelIP := '';
   FRefreshDone := FALSE;

   if LoadFindLibrary = false then
      Exit;

end;


{-------------------------------------------------------------------------------
Form Show
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.FormShow(Sender: TObject);
begin
   btnSelectDevice.Enabled := FALSE;
   ClearStringGridList;
   btnRefreshClick(self);
   btnRefresh.Enabled:=true;
   btnSelectDevice.Enabled := TRUE;
end;


{-------------------------------------------------------------------------------
destroy TfVMPadddevice object
-------------------------------------------------------------------------------}
destructor TfVMPadddevice.destroy;
begin
   FreeFindLibrary;
   inherited;
end;


{-------------------------------------------------------------------------------
Select device
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.btnSelectDeviceClick(Sender: TObject);
var
   indx: integer;
   DevCode: byte;
label errNoDevice, errInvalidIP, errInvalidSel;
begin
   indx := StringGridDevices.Row;

   if CompareText(string(DeviceFoundIP[indx]), StringGridDevices.Cells[COL_ADDRESS,indx]) <> 0 then
      goto errInvalidSel;

   if (indx < 1) or (indx >= StringGridDevices.RowCount) then
   begin
      goto errNoDevice;
   end;

   FSIPAdress := string(DeviceFoundIP[indx]);
   Exit;

errNoDevice:
   MsgBoxPas('No device selected !', 'Warning', MB_OK or MB_ICONWARNING);
   Exit;

errInvalidIP:
   MsgBoxPas('Invalid IP address selected !', 'Warning', MB_OK or MB_ICONWARNING);
   Exit;

errInvalidSel:
   MsgBoxPas('Invalid instrument selection !', 'Error', MB_OK or MB_ICONWARNING);
   Exit;
end;


{-------------------------------------------------------------------------------
Refresh devices list
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.btnRefreshClick(Sender: TObject);
var
   bSelectLastIP : boolean;
   vLstDev       : TStringList;
   vLstField     : TStringList;
   vIdx, i       : integer;
   vBuf          : array of char;
   vBufErrMsg    : array[0..255] of char;
   vNbDev        : UInt32;
   vBufSize      : UInt32;
   vErr          : Int32;

begin

   bSelectLastIP := False;

   Screen.Cursor := crHourGlass;
   try
      FRefreshDone := FALSE;

      EnableStringGrid(FALSE);

      bSelectLastIP := (FPrevSelIP = '');


      ClearStringGridList;
      NbDeviceFound :=0;
      modindex := 0;
      zeromemory(@DeviceFoundComm, sizeof(DeviceFoundComm));
      zeromemory(@DeviceFoundIP, sizeof(DeviceFoundIP));
      zeromemory(@DeviceFoundNM, sizeof(DeviceFoundNM));
      zeromemory(@DeviceFoundGW, sizeof(DeviceFoundGW));
      zeromemory(@DeviceFoundMAC, sizeof(DeviceFoundMAC));
      zeromemory(@DeviceFoundID, sizeof(DeviceFoundID));
      zeromemory(@DeviceFoundSerial, sizeof(DeviceFoundSerial));
      zeromemory(@DeviceFoundSerial_, sizeof(DeviceFoundSerial_));
      zeromemory(@DeviceFoundName, sizeof(DeviceFoundName));
      zeromemory(@DeviceFoundDevice, sizeof(DeviceFoundDevice));

      SetLength(vBuf, 5120);
      ZeroMemory(@vBuf[0], sizeof(vBuf));

      if (mHandleLibFind = 0) then
      begin
         MsgBoxPas(BLFIND_DLL_NAME + ': file not found.', SOFT_NAME, MB_OK or MB_ICONEXCLAMATION);
         Exit;
      end;

      if (@FBL_FindEChemDev = nil) or
         (@FBL_FindEChemEthDev = nil) or
         (@FBL_GetErrMsg = nil) then
      begin
         MsgBoxPas(BLFIND_DLL_NAME + ': incompatible file, functions missing.', SOFT_NAME, MB_OK or MB_ICONEXCLAMATION);
         Exit;
      end;

      vBufSize := length(vBuf);

      if FFindUSBdevices then
      begin
         vErr := FBL_FindEChemDev( @vBuf[0], @vBufSize, @vNbDev)
      end
      else
      begin
         vErr := FBL_FindEChemEthDev( @vBuf[0], @vBufSize, @vNbDev);
      end;

      if vErr < 0 then
      begin
         vBufSize := length(vBufErrMsg);
         FBL_GetErrMsg(vErr, @vBufErrMsg[0], @vBufSize);

         MsgBoxPas(vBufErrMsg, SOFT_NAME, MB_OK or MB_ICONEXCLAMATION);
         Exit;
      end;
      vLstDev   := TStringList.Create;
      vLstField := TStringList.Create;


      ExtractStrings(['%'], [], @vBuf[0], vLstDev);

      vIdx := 0;
      while ( vIdx < vLstDev.Count ) and ( NbDeviceFound < NB_MAX_DEVICE_FOUND ) do
      begin

        BLExtractStringsEmpty(['$'], [], @((vLstDev.Strings[vIdx])[1]), vLstField);

        if vLstField.Count = 9 then
        begin
           Inc( NbDeviceFound );

           DeviceFoundComm[NbDeviceFound]    := shortstring( vLstField[0] );
           DeviceFoundIP[NbDeviceFound]      := shortstring( vLstField[1] );
           DeviceFoundGW[NbDeviceFound]      := shortstring( vLstField[2] );
           DeviceFoundNM[NbDeviceFound]      := shortstring( vLstField[3] );
           DeviceFoundMAC[NbDeviceFound]     := shortstring( vLstField[4] );
           DeviceFoundID[NbDeviceFound]      := shortstring( vLstField[5] );
           DeviceFoundDevice[NbDeviceFound]  := shortstring( vLstField[6] );
           DeviceFoundSerial_[NbDeviceFound] := shortstring( vLstField[7] );

           for i := 0 to length(vLstField[7]) - 1 do
              DeviceFoundSerial[NbDeviceFound][i] := ord( vLstField[7][i+1] );

           for i := 0 to length(vLstField[8]) - 1 do
              DeviceFoundName[NbDeviceFound][i] := ord( vLstField[8][i+1] );


           with StringGridDevices do
           begin
              if Rows[RowCount-1][0] <> '' then
                 RowCount := RowCount + 1;
              Rows[RowCount-1][COL_COMM]    := string( DeviceFoundComm[NbDeviceFound] );
              Rows[RowCount-1][COL_ADDRESS] := string( DeviceFoundIP[NbDeviceFound] );
           end;
        end;

        vLstField.Clear;
        vIdx := vIdx + 1;

      end;

      vLstDev.Destroy;
      vLstField.Destroy;

   finally
      EnableStringGrid(TRUE);
      FRefreshDone := TRUE;
      Screen.Cursor := crDefault;
   end;
end;


{-------------------------------------------------------------------------------
Clear devices list
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.ClearStringGridList;
var i, j: integer;
begin
   for i := 1 to StringGridDevices.RowCount - 1 do
      for j := 0 to StringGridDevices.ColCount - 1 do
         StringGridDevices.Rows[i][j] := '';
   StringGridDevices.RowCount := 2; {do not set RowCount := 1 otherwise FixedRows is set to 0}
end;


{-------------------------------------------------------------------------------
Enable Device selection
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.EnableStringGrid(enable: boolean);
begin
   StringGridDevices.Enabled := enable;
   if enable then
   begin
      StringGridDevices.Font.Color := clBlack;
   end
   else
   begin
      StringGridDevices.Font.Color := clGrayText;
   end;
end;


{-------------------------------------------------------------------------------
Load BLFind Library
-------------------------------------------------------------------------------}
function TfVMPadddevice.LoadFindLibrary : boolean;
var
   vSeparator, vLibraryPath : string;
   lwpath: WideString;
   lpwpath: PWideChar;
begin
   if mHandleLibFind <> 0 then
      FreeFindLibrary;

   try
      vSeparator := '';

      vLibraryPath   := BLFIND_DLL_DIR + BLFIND_DLL_NAME;
      mHandleLibFind := loadlibrary( @vLibraryPath[1] );


      if mHandleLibFind <> 0 then
      begin

         @FBL_FindEChemDev      := GetProcAddress(mHandleLibFind, 'BL_FindEChemDev');
         @FBL_FindEChemEthDev   := GetProcAddress(mHandleLibFind, 'BL_FindEChemEthDev');
         @FBL_Init_Path       := GetProcAddress(mHandleLibFind, 'BL_Init_Path');
         lwpath := BLFIND_DLL_DIR;
         lpwpath := blStrToPWideChar(lwpath);
         FBL_Init_Path(lpwpath);
         @FBL_SetCfg            := GetProcAddress(mHandleLibFind, 'BL_SetConfig');
         @FBL_GetErrMsg         := GetProcAddress(mHandleLibFind, 'BL_GetErrorMsg');

         if (@FBL_FindEChemDev = nil) or
            (@FBL_FindEChemEthDev = nil) or
            (@FBL_SetCfg = nil) or
            (@FBL_GetErrMsg = nil) then
         begin
            Result := false;
         end
         else
            Result := true;
      end
      else
         Result := false;
   except
      Result := false;
   end;
end;

{-------------------------------------------------------------------------------
Free BLFind Library
-------------------------------------------------------------------------------}
procedure TfVMPadddevice.FreeFindLibrary;
begin
   try

      @FBL_FindEChemDev      := nil;
      @FBL_FindEChemEthDev   := nil;
      @FBL_SetCfg            := nil;
      @FBL_GetErrMsg         := nil;

      if mHandleLibFind <> 0 then
         FreeLibrary( mHandleLibFind );

      mHandleLibFind := 0;
   except
   end;
end;


initialization
   fVMPadddevice := nil;

finalization
end.

