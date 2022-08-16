{-------------------------------------------------------------------------------

 Definition of the constants, types, records and functions used by ECLIB.DLL

 (c) Bio-Logic company, 1997 - 2008

-------------------------------------------------------------------------------}
unit EClib;

interface

type
  int8     = Shortint;
  int16    = SmallInt;
  int32    = LongInt;
  uint8    = byte;
  uint16   = word;
  uint32   = Longword;
  puint8   = ^uint8;
  puint16  = ^uint16;
  puint32  = ^uint32;
  pint8    = ^int8;
  pint16   = ^int16;
  pint32   = ^int32;
  psingle  = ^single;

const
   LIB_DIRECTORY = '..\..\EC-Lab Development Package\';

{$IFDEF WIN64}
   ECLIB_DLL     = LIB_DIRECTORY + 'EClib64.dll';
{$ELSE}
   ECLIB_DLL     = LIB_DIRECTORY + 'EClib.dll';
{$ENDIF}


   {Nb of channels}
   NB_CH = 16;

   {ERROR CODES}
   ERR_NOERROR                    =    0;    {function succeeded}
   {General error codes}
   ERR_GEN_NOTCONNECTED           =   -1;    {no instrument connected}
   ERR_GEN_CONNECTIONINPROGRESS   =   -2;    {connection in progress}
   ERR_GEN_CHANNELNOTPLUGGED      =   -3;    {selected channel(s) not plugged}
   ERR_GEN_INVALIDPARAMETERS      =   -4;    {invalid function parameters}
   ERR_GEN_FILENOTEXISTS          =   -5;    {selected file does not exists}
   ERR_GEN_FUNCTIONFAILED         =   -6;    {function failed}
   ERR_GEN_NOCHANNELSELECTED      =   -7;    {no channel selected}
   ERR_GEN_INVALIDCONF            =   -8;    {invalid instrument configuration}
   ERR_GEN_ECLAB_LOADED           =   -9;    {EC-Lab firmware loaded on the instrument}
   ERR_GEN_LIBNOTCORRECTLYLOADED  =  -10;    {library not correctly loaded in memory}
   ERR_GEN_USBLIBRARYERROR        =  -11;    {USB library not correctly loaded in memory}
   ERR_GEN_FUNCTIONINPROGRESS     =  -12;    {function of the library already in progress}
   ERR_GEN_CHANNEL_RUNNING        =  -13;    {selected channel(s) already used}
   ERR_GEN_DEVICE_NOTALLOWED      =  -14;    {Device not allowed}
   ERR_GEN_UPDATEPARAMETERS       =  -15;    {invalid function update parameters}
   {Instrument error codes}
   ERR_INSTR_VMEERROR             = -101;    {internal instrument communication failed}
   ERR_INSTR_TOOMANYDATA          = -102;    {too many data to transfer from the instrument}
   ERR_INSTR_RESPNOTPOSSIBLE      = -103;    {channel not plugged or firmware not allowed}
   ERR_INSTR_RESPERROR            = -104;    {instrument response error}
   ERR_INSTR_MSGSIZEERROR         = -105;    {invalid message size}
   {Communication error codes}
   ERR_COMM_COMMFAILED            = -200;    {communication failed with the instrument}
   ERR_COMM_CONNECTIONFAILED      = -201;    {cannot establish connection with the instrument}
   ERR_COMM_WAITINGACK            = -202;    {waiting for the instrument response}
   ERR_COMM_INVALIDIPADDRESS      = -203;    {invalid IP address}
   ERR_COMM_ALLOCMEMFAILED        = -204;    {cannot allocate memory in the instrument}
   ERR_COMM_LOADFIRMWAREFAILED    = -205;    {cannot load firmware into selected channel(s)}
   ERR_COMM_INCOMPATIBLESERVER    = -206;    {communication firmware not compatible with the library}
   ERR_COMM_MAXCONNREACHED        = -207;    {maximum number of allowed connections reached}
   {Firmware error codes}
   ERR_FIRM_FIRMFILENOTEXISTS     = -300;    {cannot find firmware file}
   ERR_FIRM_FIRMFILEACCESSFAILED  = -301;    {cannot read firmware file}
   ERR_FIRM_FIRMINVALIDFILE       = -302;    {invalid firmware file}
   ERR_FIRM_FIRMLOADINGFAILED     = -303;    {cannot load firmware on the selected channel(s)}
   ERR_FIRM_XILFILENOTEXISTS      = -304;    {cannot find xilinx file}
   ERR_FIRM_XILFILEACCESSFAILED   = -305;    {cannot read xilinx file}
   ERR_FIRM_XILINVALIDFILE        = -306;    {invalid xilinx file}
   ERR_FIRM_XILLOADINGFAILED      = -307;    {cannot load xilinx file on the selected channel(s)}
   ERR_FIRM_FIRMWARENOTLOADED     = -308;    {no firmware loaded on the selected channel(s)}
   ERR_FIRM_FIRMWAREINCOMPATIBLE  = -309;    {loaded firmware not compatible with the library}
   {Technique error codes}
   ERR_TECH_ECCFILENOTEXISTS      = -400;    {cannot find the selected ECC file}
   ERR_TECH_INCOMPATIBLEECC       = -401;    {ECC file not compatible with the channel firmware}
   ERR_TECH_ECCFILECORRUPTED      = -402;    {ECC file corrupted}
   ERR_TECH_LOADTECHNIQUEFAILED   = -403;    {cannot load the ECC file}
   ERR_TECH_DATACORRUPTED         = -404;    {data returned by the instrument are corrupted}
   ERR_TECH_MEMFULL               = -405;    {cannot load techniques : full memory}

   {Devices constants (used by the function BL_CONNECT)}
   KBIO_DEV_VMP     = 0;
   KBIO_DEV_VMP2    = 1;
   KBIO_DEV_MPG     = 2;
   KBIO_DEV_BISTAT  = 3;
   KBIO_DEV_MCS200  = 4;
   KBIO_DEV_VMP3    = 5;
   KBIO_DEV_VSP     = 6;
   KBIO_DEV_HCP803  = 7;
   KBIO_DEV_EPP400  = 8;
   KBIO_DEV_EPP4000 = 9;
   KBIO_DEV_BISTAT2 = 10;
   KBIO_DEV_FCT150S = 11;
   KBIO_DEV_VMP300  = 12;
   KBIO_DEV_SP50    = 13;
   KBIO_DEV_SP150   = 14;
   KBIO_DEV_FCT50S  = 15;
   KBIO_DEV_SP300   = 16;
   KBIO_DEV_CLB500  = 17;
   KBIO_DEV_HCP1005 = 18;
   KBIO_DEV_CLB2000 = 19;
   KBIO_DEV_VSP300  = 20;
   KBIO_DEV_SP200   = 21;
   KBIO_DEV_MPG2    = 22;
   KBIO_DEV_SP100   = 23;
   KBIO_DEV_MOSLED  = 24;
   KBIO_DEV_SP240   = 27;
   KBIO_DEV_BP300 = 32; {BP-300 (techno VMP-300)}

   KBIO_DEV_VMP3E = 33; {VMP-3e (16 channels) (techno VMP3 ** not controled by kernel ***)}  //???
   KBIO_DEV_VSP3E = 34; {VSP-3e (8 channels) (techno VMP3 ** not controled by kernel ***)}   //???
   KBIO_DEV_SP50E = 35; {SP-50E (** not controled by kernel ***)}                             //???
   KBIO_DEV_SP150E = 36; {SP-150E (** not controled by kernel ***)}                            //???
   KBIO_DEV_UNKNOWN = 255;

   {Firmware code constants (used by the structure TCHANNELINFOS)}
   KBIO_FIRM_NONE    = 0;
   KBIO_FIRM_INTERPR = 1;
   KBIO_FIRM_UNKNOWN = 4;
   KBIO_FIRM_KERNEL  = 5;
   KBIO_FIRM_INVALID = 8;
   KBIO_FIRM_ECAL    = 10;

   {Amplifier code constants (used by the structure TCHANNELINFOS)}
   KBIO_AMPL_NONE     = 0;
   KBIO_AMPL_2A       = 1;
   KBIO_AMPL_1A       = 2;
   KBIO_AMPL_5A       = 3;
   KBIO_AMPL_10A      = 4;
   KBIO_AMPL_20A      = 5;
   KBIO_AMPL_HEUS     = 6;
   KBIO_AMPL_LC       = 7;
   KBIO_AMPL_80A      = 8;
   KBIO_AMPL_4AI      = 9;
   KBIO_AMPL_PAC      = 10;
   KBIO_AMPL_4AI_VSP  = 11;
   KBIO_AMPL_LC_VSP   = 12;
   KBIO_AMPL_UNDEF    = 13;
   KBIO_AMPL_MUIC     = 14;
   KBIO_AMPL_NONE_GIL = 15;
   KBIO_AMPL_8AI      = 16;
   KBIO_AMPL_LB500    = 17;
   KBIO_AMPL_100A5V   = 18;
   KBIO_AMPL_LB2000   = 19;
   KBIO_AMPL_1A48V    = 20;
   KBIO_AMPL_4A10V    = 21;

   {Option error codes}
   KBIO_OPT_NOERR          = 0;       {Option no error}
   KBIO_OPT_CHANGE         = 1;       {Option change}
   KBIO_OPT_4A10V_ERR      = 100;     {Amplifier 4A10V error}
   KBIO_OPT_4A10V_OVRTEMP  = 101;     {Amplifier 4A10V overload temperature}
   KBIO_OPT_4A10V_BADPOW   = 102;     {Amplifier 4A10V invalid power}
   KBIO_OPT_4A10V_POWFAIL  = 103;     {Amplifier 4A10V power fail}
   KBIO_OPT_1A48V_ERR      = 200;     {Amplifier 1A48V error}
   KBIO_OPT_1A48V_OVRTEMP  = 201;     {Amplifier 1A48V overload temperature}
   KBIO_OPT_1A48V_BADPOW   = 202;     {Amplifier 1A48V invalid power}
   KBIO_OPT_1A48V_POWFAIL  = 203;     {Amplifier 1A48V power fail}

   {I Range constants (used by the structures TDATAINFOS and TECCPARAMGEN)}
   KBIO_IRANGE_100pA   = 0;
   KBIO_IRANGE_1nA     = 1;
   KBIO_IRANGE_10nA    = 2;
   KBIO_IRANGE_100nA   = 3;
   KBIO_IRANGE_1uA     = 4;
   KBIO_IRANGE_10uA    = 5;
   KBIO_IRANGE_100uA   = 6;
   KBIO_IRANGE_1mA     = 7;
   KBIO_IRANGE_10mA    = 8;
   KBIO_IRANGE_100mA   = 9;
   KBIO_IRANGE_1A      = 10;
   KBIO_IRANGE_BOOSTER = 11;
   KBIO_IRANGE_AUTO    = 12;
   KBIO_IRANGE_10pA    = 13; {IRANGE_100pA + Igain x10}
   KBIO_IRANGE_1pA     = 14; {IRANGE_100pA + Igain x100}

   {E Range constants (used by the structures TDATAINFOS and TECCPARAMGEN)}
   KBIO_ERANGE_2_5  = 0;     {±2.5V}
   KBIO_ERANGE_5    = 1;     {±5V}
   KBIO_ERANGE_10   = 2;     {±10V}
   KBIO_ERANGE_AUTO = 3;     {auto}

   {Bandwidth constants (used by the structures TDATAINFOS and TECCPARAMGEN)}
   KBIO_BW_1 = 1;
   KBIO_BW_2 = 2;
   KBIO_BW_3 = 3;
   KBIO_BW_4 = 4;
   KBIO_BW_5 = 5;
   KBIO_BW_6 = 6;
   KBIO_BW_7 = 7;
   KBIO_BW_8 = 8;
   KBIO_BW_9 = 9;

   {E/I gain constants}
   KBIO_GAIN_1    = 0;
   KBIO_GAIN_10   = 1;
   KBIO_GAIN_100  = 2;
   KBIO_GAIN_1000 = 3;

   {E/I filter constants}
   KBIO_FILTER_NONE  = 0;
   KBIO_FILTER_50KHZ = 1;
   KBIO_FILTER_1KHZ  = 2;
   KBIO_FILTER_5HZ   = 3;

   {Coulometry constants}
   KBIO_COUL_SOFT = 0;
   KBIO_COUL_HARD = 1;

   {Electrode connection constants}
   KBIO_CONN_STD      = 0;
   KBIO_CONN_CETOGRND = 1;
   KBIO_CONN_WETOGRND = 2;
   KBIO_CONN_HV       = 3;

   {Controled potential mode constants}
   KBIO_REF21     = 0;
   KBIO_REF31     = 1;
   KBIO_REF32     = 2;
   KBIO_REF32DIFF = 3;

   {Channel mode constants}
   KBIO_MODE_GROUNDED = 0;
   KBIO_MODE_FLOATING = 1;

   {LC measurement constants}
   KBIO_BOOST_NOISE  = 0;
   KBIO_BOOST_SPEED = 1;

   {Technique ID constants (used by the structure TDATAINFOS)}
   KBIO_TECHID_NONE            = 0;
   KBIO_TECHID_OCV	          = 100;
   KBIO_TECHID_CA	             = 101;
   KBIO_TECHID_CP	             = 102;
   KBIO_TECHID_CV	             = 103;
   KBIO_TECHID_PEIS            = 104;
   KBIO_TECHID_POTPULSE	       = 105;
   KBIO_TECHID_GALPULSE        = 106;
   KBIO_TECHID_GEIS	          = 107;
   KBIO_TECHID_STACKPEIS_SLAVE = 108;
   KBIO_TECHID_STACKPEIS       = 109;
   KBIO_TECHID_CPOWER	       = 110;
   KBIO_TECHID_CLOAD	          = 111;
   KBIO_TECHID_FCT	          = 112;
   KBIO_TECHID_SPEIS	          = 113;
   KBIO_TECHID_SGEIS	          = 114;
   KBIO_TECHID_STACKPDYN       = 115;
   KBIO_TECHID_STACKPDYN_SLAVE = 116;
   KBIO_TECHID_STACKGDYN       = 117;
   KBIO_TECHID_STACKGEIS_SLAVE = 118;
   KBIO_TECHID_STACKGEIS       = 119;
   KBIO_TECHID_STACKGDYN_SLAVE = 120;
   KBIO_TECHID_CPO	          = 121;
   KBIO_TECHID_CGA	          = 122;
   KBIO_TECHID_COKINE	       = 123;
   KBIO_TECHID_PDYN            = 124;
   KBIO_TECHID_GDYN            = 125;
   KBIO_TECHID_CVA             = 126;
   KBIO_TECHID_DPV             = 127;
   KBIO_TECHID_SWV             = 128;
   KBIO_TECHID_NPV             = 129;
   KBIO_TECHID_RNPV            = 130;
   KBIO_TECHID_DNPV            = 131;
   KBIO_TECHID_DPA             = 132;
   KBIO_TECHID_EVT             = 133;
   KBIO_TECHID_LP	             = 134;
   KBIO_TECHID_GC	             = 135;
   KBIO_TECHID_CPP             = 136;
   KBIO_TECHID_PDP             = 137;
   KBIO_TECHID_PSP	          = 138;
   KBIO_TECHID_ZRA	          = 139;
   KBIO_TECHID_MIR	          = 140;
   KBIO_TECHID_PZIR	          = 141;
   KBIO_TECHID_GZIR	          = 142;
   KBIO_TECHID_LOOP 	          = 150;
   KBIO_TECHID_TO 	          = 151;
   KBIO_TECHID_TI 	          = 152;
   KBIO_TECHID_TOS 	          = 153;
   KBIO_TECHID_MUX 	          = 154;
   KBIO_TECHID_CPLIMIT         = 155;
   KBIO_TECHID_GDYNLIMIT       = 156;
   KBIO_TECHID_CALIMIT         = 157;
   KBIO_TECHID_PDYNLIMIT       = 158;
   KBIO_TECHID_LASV            = 159;
   KBIO_TECHID_MUXLOOP         = 160;
   KBIO_TECHID_ABS 	          = 1000;
   KBIO_TECHID_FLUO 	          = 1001;
   KBIO_TECHID_RABS            = 1002;
   KBIO_TECHID_RFLUO           = 1003;
   KBIO_TECHID_RDABS 	       = 1004;
   KBIO_TECHID_DABS 	          = 1005;
   KBIO_TECHID_ABSFLUO 	       = 1006;
   KBIO_TECHID_RAFABS          = 1007;
   KBIO_TECHID_RAFFLUO          = 1008;

   EXP_GRP_EXPRESS_GAL = [KBIO_TECHID_CP, KBIO_TECHID_GEIS,
                           KBIO_TECHID_SGEIS, KBIO_TECHID_STACKGDYN, KBIO_TECHID_GDYN, KBIO_TECHID_GZIR,
                           KBIO_TECHID_CPLIMIT, KBIO_TECHID_GDYNLIMIT]; {Galvano techniques}

   {Channel state constants (used by the structures TDATAINFOS and TECCPARAMGEN)}
   KBIO_STATE_STOP  = 0;
   KBIO_STATE_RUN   = 1;
   KBIO_STATE_PAUSE = 2;

   {Parameter type constants (used by the structure TECCPARAM and TEccParam_LV)}
   PARAM_INT32   = 0;
   PARAM_BOOLEAN = 1;
   PARAM_SINGLE  = 2;

   {Separator for EccParams}
   SEPARATOR = ';';

type
    PPAnsiChar   = array of array of ansichar;
    TArrayDouble = array of Double;

   {Device informations.
    WARNING : record aligned on 32 bits}
   TDeviceInfos = record
      DeviceCode        : int32;          {Device}
	   RAMsize           : int32;			   {RAM size (MBytes)}
	   CPU               : int32;         	{Computer board cpu (68040, 68060)}
	   NumberOfChannels  : int32;		 	   {number of channels}
      NumberOfSlots     : int32;		 	   {number of slots}
      FirmwareVersion   : int32;          {Communication firmware version}
      FirmwareDate_yyyy : int32;          {Communication firmware date YYYY}
      FirmwareDate_mm   : int32;          {Communication firmware date MM}
      FirmwareDate_dd   : int32;          {Communication firmware date DD}
      HTdisplayOn		   : int32;	         {Allow hyperterminal prints (true/false)}
      NbOfConnectedPC   : int32;			   {Number of connected PC}
   end;
   PDeviceInfos = ^TDeviceInfos;

   {Channel informations.
    WARNING : record aligned on 32 bits}
   TChannelInfos = record
      Channel           : int32;          {Channel (0-based)}
      BoardVersion      : int32;          {Board version}
      BoardSerialNumber : int32;          {Board serial number}
      FirmwareCode      : int32;          {Firmware code}
      FirmwareVersion   : int32;          {Firmware version}
      XilinxVersion     : int32;          {Xilinx version}
      AmpCode           : int32;          {Amplifier code}
      NbAmp             : int32;          {Nb Amplifiers 4A}
      LCboard           : int32;          {Low Current board}
      Zboard            : int32;          {EIS board}
      MUXboard          : int32;          {MUX board}
      GPRAboard         : int32;          {Generateur Programmable Rampe Analogique board}
      MemSize           : int32;          {Memory size (in bytes)}
      MemFilled         : int32;          {Memory filled (in bytes)}
      State             : int32;          {Channel state (run/stop/pause)}
      MaxIRange         : int32;          {Max I range allowed}
      MinIRange         : int32;          {Min I range allowed}
      MaxBandwidth      : int32;          {Max bandwidth allowed}
      NbOfTechniques    : int32;          {Number of techniques loaded}
   end;
   PChannelInfos = ^TChannelInfos;

   {Current values.
    WARNING : record aligned on 32 bits}
   TCurrentValues = record
      State             : int32;          {Channel state (run/stop/pause)}
      MemFilled         : int32;          {Memory filled (bytes)}
      TimeBase          : single;         {Timebase (s)}
      Ewe               : single;         {Ewe (V)}
      EweRangeMin       : single;         {Ewe min range (V)}
      EweRangeMax       : single;         {Ewe max range (V)}
      Ece               : single;         {Ece (V)}
      EceRangeMin       : single;         {Ece min range (V)}
      EceRangeMax       : single;         {Ece max range (V)}
      Eoverflow         : int32;          {E overflow}
      I                 : single;         {I (A)}
      IRange            : int32;          {I range}
      Ioverflow         : int32;          {I overflow}
      ElapsedTime       : single;         {Elapsed time (s)}
      Freq              : single;         {Frequency (Hz)}
      Rcomp             : single;         {R compensation (Ohm)}
      Saturation        : int32;          {E or/and I saturation}
      OptErr            : int32;          {Option error code}
      OptPos            : int32;          {Option position}
   end;
   PCurrentValues = ^TCurrentValues;

   {Current values for BioKine.
    WARNING : record aligned on 32 bits}
   TCurrentValuesBk = record
      State             : int32;          {Channel state (run/stop/pause)}
      MemFilled         : int32;          {Memory filled (bytes)}
      TimeBase          : single;         {Timebase (s)}
      ElapsedTime       : single;         {Elapsed time (s)}
      PHout             : single;         {PHout (V)}
      PMout             : single;         {PMout (V)}
      HVMON             : single;         {Hv Monitor (V)}
      ledbCode          : int32;          {LedA code}
      ledaCode          : int32;          {LedB code}
      phCode            : int32;          {PH code}
      pmCode            : int32;          {PM code}
      HVMAX             : single;         {Hv Max (V)}
      PhSat             : int32;          {PH or/and PM saturation}
      PmSat             : int32;          {PH or/and PM saturation}
      Saturation        : int32;          {PH or/and PM saturation}
      RefPh             : single;         {Valeur de la reference de la ph (V)}
      RefPm             : single;         {Valeur de la reference du pm (V)}
      RefokPh           : int32;
      RefokPm           : int32;
      HT0RefPm          : single;
      Int0RefPh         : single;
      Int0RefPm         : single;
      AUXIN             : single;
   end;
   PCurrentValuesBk = ^TCurrentValuesBk;

   {Data informations.
    WARNING : record aligned on 32 bits}
   TDataInfos = record
      IRQskipped        : int32;          {Number of IRQ skipped}
      NbRaws            : int32;          {Number of raws into the data buffer}
      NbCols            : int32;          {Number of columns into the data buffer}
      TechniqueIndex    : int32;          {Technique index (0-based)}
      TechniqueID       : int32;          {Technique ID}
      ProcessIndex      : int32;          {Process index (0-based)}
      loop              : int32;          {Loop number}
      StartTime         : double;         {Start time (s)}
      MuxPad            : int32;          {Multiplexeur pad}
   end;
   PDataInfos = ^TDataInfos;

   {Data buffer.
    WARNING : record aligned on 32 bits}
   TDataBuffer = array[1..1000] of uint32;
   PDataBuffer = ^TDataBuffer;

   {Elementary technique parameter.
    WARNING : record aligned on 32 bits}
   TEccParam = record
      ParamStr          : array[1..64] of ansichar;    {string who defines the parameter}
      ParamType         : int32;          {Parameter type (0=int32, 1=boolean, 2=single)}
      ParamVal          : int32;          {Parameter value (WARNING : numerical value)}
      ParamIndex        : int32;          {Parameter index (0-based)}
   end;
   PEccParam = ^TEccParam;
   TDynArrayofEccParam = array of TEccParam;

   {Technique parameters.
    WARNING : record aligned on 32 bits}
   TEccParams = record
      len               : int32;          {Length of the array pParams^[]}
      pParams           : PEccParam;      {Pointer on the first record who defines the parameters}
   end;

   {Elementary technique parameter (define for LabVIEW compatibility)}
   TArrayOfChar_LV = record               {Array of ansichar}
      dimSize        : int32;             {length of the array}
      FirstChar      : ansichar;              {first element in the array of ansichar}
   end;
   PArrayOfChar_LV = ^TArrayOfChar_LV;
   PPArrayOfChar_LV = ^PArrayOfChar_LV;
   TEccParam_LV = record
      ppParamStr_LV  : PPArrayOfChar_LV;  {string who defines the parameter}
      ParamType      : int32;             {Parameter type (0=int32, 1=boolean, 2=single)}
      ParamVal       : int32;             {Parameter value}
      ParamIndex     : int32;             {parameter index}
   end;
   PEccParam_LV = ^TEccParam_LV;
   {Array of elementary parameters TEccParam_LV (define for LabVIEW compatibility)}
   TEccParams_LV = record
      dimSize           : int32;          {length of the array}
      FirstEccParam_LV  : TEccParam_LV;   {first element in the array}
   end;
   PEccParams_LV = ^TEccParams_LV;
   PPEccParams_LV = ^PEccParams_LV;

   {Experiment informations.
    WARNING : record aligned on 32 bits}
   TExperimentInfos = record
      Group        : int32;
      PCidentifier : int32;
      TimeHMS      : int32;
      TimeYMD      : int32;
      FileName     : array[1..256] of ansichar;
   end;
   PExperimentInfos = ^TExperimentInfos;

   {Hardware configuration
    WARNING : record aligned on 32 bits}
   THardwareConf = record
      Conn   : int32;   {Electrode connection}
      Ground : int32;   {Instrument ground}
   end;
   PHardwareConf = ^THardwareConf;


   {General functions}
   function BL_GetLibVersion( pVersion : pansichar; {(out) version of the library (C-string)}
                              psize    : puint32    {(in/out) size of the string}
                             ): int32; stdcall;     {(out) cf. error codes}
                             external ECLIB_DLL;

   function BL_GetVolumeSerialNumber: uint32; stdcall; external ECLIB_DLL;

   function BL_GetErrorMsg( errorcode : int32;     {(in) error code}
                            pmsg      : pansichar; {(out) message (C-string)}
                            psize     : puint32    {(in/out) size of the message}
                          ): int32; stdcall;       {(out) cf. error codes}
                          external ECLIB_DLL;

   {Communication functions}
   function BL_Connect( pstr    : PAnsiChar;    {(in) IP address or USB port (C-string)}
                        TimeOut : uint8;        {(in) communication timeout (sec)}
                        pID     : pint32;       {(out) device identifier (1-based)}
                        pInfos  : PDeviceInfos  {(out) device informations}
                       ): int32; stdcall;       {(out) cf. error codes}
                       external ECLIB_DLL;

   function BL_Disconnect( ID: int32            {(in) device identifier}
                         ): int32; stdcall;     {(out) cf. error codes}
                         external ECLIB_DLL;

   function BL_TestConnection( ID: int32            {(in) device identifier}
                              ): int32; stdcall;    {(out) cf. error codes}
                              external ECLIB_DLL;

   function BL_TestCommSpeed( ID         : int32;   {(in) device identifier}
                              channel    : uint8;   {(in) selected channel (0->15)}
                              spd_rcvt   : pint32;  {(out) device communication speed (ms)}
                              spd_kernel : pint32   {(out) channel communication speed (ms)}
                             ): int32; stdcall;     {(out) cf. error codes}
                             external ECLIB_DLL;

   function BL_GetUSBdeviceinfos( USBindex     : uint32;    {(in) USB device index}
                                  pcompany     : pansichar; {(out) company name}
                                  pcompanysize : puint32;   {(in/out) size of company name}
                                  pdevice      : pansichar; {(out) device name}
                                  pdevicesize  : puint32;   {(in/out) size of device name}
                                  pSN          : pansichar; {(out) serial number}
                                  pSNsize      : puint32    {(in/out) size of serial number}
                                 ): boolean; stdcall;
                                 external ECLIB_DLL;

   {Firmware functions}
   function BL_LoadFirmware( ID          : int32;       {(in) device identifier}
                             pChannels   : puint8;      {(in) selected channels}
                             pResults    : pint32;      {(out) results for each channels}
                             length      : uint8;       {(in) length of the arrays pChannels^[] and pResults^[]}
                             ShowGauge   : boolean;     {(in) show the gauge during transfer}
                             ForceLoad   : boolean;     {(in) force load the firmware}
                             BinFile     : PAnsiChar;   {(in) bin file    (nil for default file)}
                             XlxFile     : PAnsiChar    {(in) xilinx file (nil for default file)}
                            ): int32; stdcall;          {(out) cf. error codes}
                            external ECLIB_DLL;

   {Channel informations functions}
   function BL_GetChannelsPlugged( ID         : int32;  {(in) device identifier}
                                   pChPlugged : puint8; {(out) array of channels plugged}
                                   Size       : uint8   {(in) size of the array}
                                  ): int32; stdcall;    {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_IsChannelPlugged( ID : int32;            {(in) device identifier}
                                 ch : uint8             {(in) selected channel (0->15)}
                                ): boolean; stdcall;    {(out) true/false}
                                external ECLIB_DLL;

   function BL_GetChannelInfos( ID      : int32;        {(in) device identifier}
                                ch      : uint8;        {(in) selected channel (0->15)}
                                pInfos  : PChannelInfos {(out) channel infos}
                               ): int32; stdcall;       {(out) cf. error codes}
                               external ECLIB_DLL;

   function BL_GetMessage( ID    : int32;        {(in) device identifier}
                           ch    : uint8;        {(in) selected channel (0->15)}
                           pMsg  : pansichar;    {(out) message (C-string)}
                           psize : puint32       {(in/out) size of the message}
                          ): int32; stdcall;     {(out) cf. error codes}
                          external ECLIB_DLL;

   {Technique functions}
   function BL_LoadTechnique( ID             : int32;      {(in) device identifier}
                              channel        : uint8;      {(in) selected channel (0->15)}
                              pFName         : pansichar;  {(in) file name of the ecc file (C-string)}
                              Params         : TEccParams; {(in) Technique parameters}
                              FirstTechnique : boolean;    {(in) TRUE if first technique loaded}
                              LastTechnique  : boolean;    {(in) TRUE if last technique loaded}
                              DisplayParams  : boolean     {(in) Display parameters sent (for debugging purpose)}
                             ): int32; stdcall;            {(out) cf. error codes}
                             external ECLIB_DLL;

   function BL_LoadTechnique_LV( ID             : int32;          {(in) device identifier}
                                 channel        : uint8;          {(in) selected channel (0->15)}
                                 pFName         : pansichar;      {(in) file name of the ecc file (C-string)}
                                 HdlParams      : PPEccParams_LV; {(in) Technique parameters}
                                 FirstTechnique : boolean;        {(in) TRUE if first technique loaded}
                                 LastTechnique  : boolean;        {(in) TRUE if last technique loaded}
                                 DisplayParams  : boolean         {(in) Display parameters (for debugging purpose)}
                                ): int32; stdcall;                {(out) cf. error codes}
                                external ECLIB_DLL;

   function BL_LoadTechnique_VEE (ID            : int32;         {(in) device identifier}
                                 channel        : uint8;         {(in) channel selected (0->15)}
                                 pFName         : PAnsiChar;     {(in) file name of the ecc file (C-string)}
                                 appParams      : PPAnsiChar;    {(in) Vee Pro array handle, i.e. pointer to pointer of char,
                                 FirstTechnique : boolean;        {(in) if TRUE the index used to load the technique are freed before}
                                 LastTechnique  : boolean;        {(in) if TRUE the technique(s) loaded is(are) built}
                                 DisplayParams  : boolean         {(in) Display parameters (for debugging purpose)}
                                 ): int32; stdcall;               {(out) cf. error codes}
                                external ECLIB_DLL;

   function BL_DefineBoolParameter( lbl    : pansichar;   {(in) Label (C-string)}
                                    value  : boolean;     {(in) Value}
                                    index  : int32;       {(in) Index}
                                    pParam : PEccParam    {(out) Parameter record}
                                   ): int32; stdcall;     {(out) cf. error codes}
                                   external ECLIB_DLL;

   function BL_DefineSglParameter( lbl    : pansichar;    {(in) Label (C-string)}
                                   value  : single;       {(in) Value}
                                   index  : int32;        {(in) Index}
                                   pParam : PEccParam     {(out) Parameter record}
                                  ): int32; stdcall;      {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_DefineIntParameter( lbl    : pansichar;    {(in) Label (C-string)}
                                   value  : int32;        {(in) Value}
                                   index  : int32;        {(in) Index}
                                   pParam : PEccParam     {(out) Parameter record}
                                  ): int32; stdcall;      {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_UpdateParameters(    ID          : int32;       {(in) device identifier}
                                    channel     : uint8;       {(in) channel selected (0->15)}
                                    TechIndx    : int32;       {Index of technique to read}
                                    Params      : TEccParams;  {(in) Technique parameters}
                                    EccFileName : PansiChar    {(in) Ecc file name}
                                ): int32; stdcall;             {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_UpdateParameters_VEE(ID          : int32;       {(in) device identifier}
                                    channel     : uint8;       {(in) channel selected (0->15)}
                                    TechIndx    : int32;       {Index of technique to update}
                                    appParams   : PPAnsiChar;  {(in) Technique parameters}
                                    EccFileName : pansichar    {(in) Ecc file name}
                              ): int32; stdcall;               {(out) cf. error codes}
                                  external ECLIB_DLL;

   {Start/stop functions}
   function BL_StartChannels( ID        : int32;     {(in) device identifier}
                              pChannels : puint8;    {(in) selected channels }
                              pResults  : pint32;    {(out) results for each channels}
                              length    : uint8      {(in) length of the arrays pChannels^[] and pResults^[]}
                             ): int32; stdcall;      {(out) cf. error codes}
                             external ECLIB_DLL;

   function BL_StartChannel( ID      : int32;      {(in) device identifier}
                             channel : uint8       {(in) selected channel (0->15)}
                            ): int32; stdcall;     {(out) cf. error codes}
                            external ECLIB_DLL;

   function BL_StopChannels( ID        : int32;    {(in) device identifier}
                             pChannels : puint8;   {(in) selected channels }
                             pResults  : pint32;   {(out) results for each channels}
                             length    : uint8     {(in) length of the arrays pChannels^[] and pResults^[]}
                            ): int32; stdcall;     {(out) cf. error codes}
                            external ECLIB_DLL;

   function BL_StopChannel( ID      : int32;       {(in) device identifier}
                            channel : uint8        {(in) selected channel (0->15)}
                           ): int32; stdcall;      {(out) cf. error codes}
                           external ECLIB_DLL;

   {Data functions}
   function BL_GetCurrentValues( ID        : int32;          {(in) device identifier}
                                 channel   : uint8;          {(in) selected channel (0->15)}
                                 pValues   : PCurrentValues  {(out) current values}
                                ): int32; stdcall;           {(out) cf. error codes}
                                external ECLIB_DLL;

   function BL_GetData( ID        : int32;         {(in) device identifier}
                        channel   : uint8;         {(in) selected channel (0->15)}
                        pBuf      : PDataBuffer;   {(out) data buffer}
                        pInfos    : PDataInfos;    {(out) data informations}
                        pValues   : PCurrentValues {(out) current values}
                       ): int32; stdcall;          {(out) cf. error codes}
                       external ECLIB_DLL;

   function BL_GetFCTData( ID        : int32;         {(in) device identifier}
                           channel   : uint8;         {(in) selected channel (0->15)}
                           pBuf      : PDataBuffer;   {(out) data buffer}
                           pInfos    : PDataInfos;    {(out) data informations}
                           pValues   : PCurrentValues {(out) current values}
                          ): int32; stdcall;          {(out) cf. error codes}
                          external ECLIB_DLL;

   function BL_GetData_VEE( ID       : int32;         {(in) device identifier}
                           channel   : uint8;         {(in) channel selected (0->15)}
                           pBuf      : PDataBuffer;   {(out) data buffer}
                           pInfos    : TArrayDouble;  {(out) data informations}
                           pValues   : TArrayDouble   {(out) current values}
                        ): int32; stdcall;            {(out) cf. error codes}
                          external ECLIB_DLL;

   function BL_ConvertNumericIntoSingle( num  : uint32;         {(in) numeric value (32bits)}
                                         psgl : psingle         {(out) single}
                                        ): int32; stdcall;      {(out) cf. error codes}
                                        external ECLIB_DLL;

   function BL_GetCurrentValuesBk( ID        : int32;            {(in) device identifier}
                                   channel   : uint8;            {(in) selected channel (0->15)}
                                   pValues   : PCurrentValuesBk  {(out) current values}
                                  ): int32; stdcall;             {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_GetDataBk( ID        : int32;             {(in) device identifier}
                          channel   : uint8;             {(in) selected channel (0->15)}
                          pBuf      : PDataBuffer;       {(out) data buffer}
                          pInfos    : PDataInfos;        {(out) data informations}
                          pValues   : PCurrentValuesBk   {(out) current values}
                         ): int32; stdcall;              {(out) cf. error codes}
                         external ECLIB_DLL;

   {Hardware functions}
   function BL_SetHardConf( ID       : int32;             {(in) device identifier}
                            channel  : uint8;             {(in) selected channel (0->15)}
                            hardConf : THardwareConf      {(in) hardware configuration}
                           ): int32; stdcall;             {(out) cf. error codes}
                           external ECLIB_DLL;

   function BL_GetHardConf( ID        : int32;             {(in) device identifier}
                            channel   : uint8;             {(in) selected channel (0->15)}
                            pHardConf : PHardwareConf      {(out) hardware configuration}
                           ): int32; stdcall;             {(out) cf. error codes}
                           external ECLIB_DLL;

   function BL_GetOptErr( ID      : int32;      {(in) device identifier}
                          channel : uint8;      {(in) selected channel (0->15)}
                          pOptErr : pint32;     {(out) Option error code}
                          pOptPos : pint32      {(out) Option position}
                         ): int32; stdcall;     {(out) cf. error codes}
                         external ECLIB_DLL;

   {Miscellaneous functions}
   function BL_SetExperimentInfos( ID        : int32;           {(in) device identifier}
                                   channel   : uint8;           {(in) selected channel (0->15)}
                                   ExpInfos  : TExperimentInfos {(in) Experiment informations}
                                  ): int32; stdcall;            {(out) cf. error codes}
                                  external ECLIB_DLL;

   function BL_GetExperimentInfos( ID        : int32;           {(in) device identifier}
                                   channel   : uint8;           {(in) selected channel (0->15)}
                                   pExpInfos : PExperimentInfos {(out) Experiment informations}
                                  ): int32; stdcall;            {(out) cf. error codes}
                                  external ECLIB_DLL;
                                     
   function BL_LoadFlash( ID        : int32;     {(in) device identifier}
                          pfname    : pansichar; {(in) flash file name (C-string)}
                          ShowGauge : boolean    {(in) show a gauge during transfer}
                         ): int32; stdcall;      {(out) cf. error codes}
                         external ECLIB_DLL;

  function BL_IsVMP4Device( DevCode        : int32     {(in) device identifier}
                         ): boolean;      {(out) cf. error codes}
                         external ECLIB_DLL; //works in 64bits but not in 32 bits (DevCode is not well passed to DLL)

implementation

end.

