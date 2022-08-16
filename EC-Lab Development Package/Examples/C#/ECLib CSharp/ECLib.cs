using System;
using System.Runtime.InteropServices;

namespace ECLibSharpExample
{
    public class ECLib
    {
        /* 
         * This file is here to serve as a bridge between the ECLab DLL and the C# code.
         * It defines all the functions and constants needed to use the DLL, and makes the necessary
         * adjustments where needed (see BL_DefineXXXParameter() functions, for instance).
         */
        public const string DLL_Path = @"C:\Sources\Electrochimie\OEM_PACKAGE\Trunk\EC-Lab Development Package\EClib.dll";

        [DllImport(DLL_Path)] public static extern int BL_GetVolumeSerialNumber();
    
        [DllImport(DLL_Path)] public static extern ErrorCode BL_Disconnect(int id);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_Connect(string server, byte timeout, ref int connection_id, ref DeviceInfo pInfos);


        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetLibVersion([MarshalAs(UnmanagedType.LPArray)] byte[] pVersion, ref int psize);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetErrorMsg(int errorcode, [MarshalAs(UnmanagedType.LPArray)] byte[] pmsg, ref int psize);

        [DllImport(DLL_Path)] public static extern ErrorCode BL_TestConnection(int ID);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_TestCommSpeed(int ID, byte channel, ref int spd_rcvt, ref int spd_kernel);
        [DllImport(DLL_Path)]
        public static extern bool BL_GetUSBdeviceinfos(ref int USBindex,
            byte[] pcompany, ref int pcompanysize,
            byte[] pdevice, ref int pdevicesize,
            byte[] pSN, ref int pSNsize);

        [DllImport(DLL_Path)] public static extern ErrorCode BL_LoadFirmware(int ID, byte[] pChannels, int[] pResults, byte Length, bool ShowGauge, bool ForceReload, string BinFile, string XlxFile);

        [DllImport(DLL_Path)] public static extern bool      BL_IsChannelPlugged(int ID, byte ch);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetModulesPlugged(int ID, byte[] pChPlugged, byte Size);

        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetChannelsPlugged(int ID, byte[] pChPlugged, byte Size);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetChannelInfos(int ID, byte ch, ref ChannelInfo pInfos);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetMessage(int ID, byte ch, [MarshalAs(UnmanagedType.LPArray)] byte[] msg, ref int size);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetHardConf(int ID, byte ch, HardwareConf pHardConf);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_SetHardConf(int ID, byte ch, HardwareConf HardConf);


        [DllImport(DLL_Path)] public static extern ErrorCode BL_LoadTechnique(int ID, byte channel, string pFName, EccParams pparams, bool FirstTechnique, bool LastTechnique, bool DisplayParams);
        
        /**
         * These 3 functions are using an IntPtr instead of an ECCParam reference. 
         * This is because the ECCParams (note the 's') is not Marshalable easily and have to be allocated
         * through the Marshal.AllocHGlobal() function. See the example usage in ECLibDialog.cs.
         */
        [DllImport(DLL_Path)] public static extern ErrorCode BL_DefineBoolParameter(string lbl, bool value, int index, IntPtr pParam);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_DefineSglParameter(string lbl, float value, int index, IntPtr pParam);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_DefineIntParameter(string lbl, int value, int index, IntPtr pParam);


        [DllImport(DLL_Path)] public static extern ErrorCode BL_UpdateParameters(int ID, byte channel, int TechIndx, EccParams pparams, string EccFileName);
        

        [DllImport(DLL_Path)] public static extern ErrorCode BL_StartChannel(int ID, byte channel);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_StartChannels(int ID, byte[] pChannels, ref int pResults, byte length);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_StopChannel(int ID, byte channel);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_StopChannels(int ID, byte[] pChannels, ref int pResults, byte length);


        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetCurrentValues(int ID, byte channel, ref CurrentValues pValues);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetData(int ID, byte channel, [MarshalAs(UnmanagedType.LPArray, SizeConst=1000)] int[] buf, ref DataInfos pInfos, ref CurrentValues pValues);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_GetFCTData(int ID, byte channel, [MarshalAs(UnmanagedType.LPArray, SizeConst=1000)] int[] buf, ref DataInfos pInfos, ref CurrentValues pValues);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_ConvertNumericIntoSingle( int num, ref float psgl);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_SendMsg(int ID, byte ch, byte[] pBuf, ref int pLen);
        [DllImport(DLL_Path)] public static extern ErrorCode BL_LoafFlash(int ID, string pfname, bool ShowGauge);

        /* ***********************************************
         * Helper to determine if a device is VMP4 or VMP3
         * *********************************************** */
        public static bool is_vmp4(DeviceType dev)
        {
            DeviceType[] vmp4_devices = 
            {
                DeviceType.KBIO_DEV_SP200,  DeviceType.KBIO_DEV_SP300,
                DeviceType.KBIO_DEV_VSP300, DeviceType.KBIO_DEV_VMP300, 
                DeviceType.KBIO_DEV_SP240           
            };
            foreach (DeviceType d in vmp4_devices)
                if (dev == d) return true;
            return false;
        }

        /* **********************
         * Structures definitions
         * ********************** */

        // Default layout is Sequential, so no need to set the [StructLayout] attribute
        public struct DeviceInfo
        {
            public DeviceType DeviceCode;
            public int RAMSize;
            public int CPU;
            public int NumberOfChannels;
            public int NumberOfSlots;
            public int FirmwareVersion;
            public int FirmwareDate_yyyy;
            public int FirmwareDate_mm;
            public int FirmwareDate_dd;
            public int HTdisplayOn;
            public int NbOfConnectedPC;
        }

        public struct ChannelInfo
        {
            public int Channel;
            public int BoardVersion;
            public int BoardSerialNumber;
            public FirmwareCode FirmwareCode;  /* (see section 4.2 in the documentation for constants used) */
            public int FirmwareVersion; /* Firmware version */
            public int XilinxVersion;
            public AmplifierType AmpCode;
            public int NbAmps;
            public int Lcboard;
            public int Zboard;
            public int RESERVED;
            public int RESERVED2;
            public int MemSize;  /* Memory size (in bytes) */
            public int MemFilled;  /* Memory filled (in bytes) */
            public ChannelState State;  /* (see section 4.2 in the documentation for constants used) */
            public IntensityRange MaxIRange;  /* (see section 4.2 in the documentation for constants used) */
            public IntensityRange MinIRange;  /* Minimum I range allowed (see section 4.2 in the documentation for constants used) */
            public Bandwidth MaxBandwidth; /* Maximum bandwidth allowed (see section 4.2 in the documentation for constants used) */
            public int NbOfTechniques; /* Number of techniques loaded */
        }

        public struct CurrentValues
        {
            public ChannelState State; /* int Channel state : run/stop/pause (see section 4.2 in the documentation for constants used) */
            public int MemFilled; /* int Memory filled (in bytes) */
            public float TimeBase; /* single Time base (s) */
            public float Ewe; /* single Working electrode potential (V) */
            public float EweRangeMin; /* single Ewe min range (V) */
            public float EweRangeMax; /* single Ewe max range (V) */
            public float Ece; /* single Counter electrode potential (V) */
            public float EceRangeMin; /* single Ece min range (V) */
            public float EceRangeMax; /* single Ece max range (V) */
            public int Eoverflow; /* int Potential overflow */
            public float I; /* single Current value (A) */
            public IntensityRange IRange; /* int Current range (see section 4.2 in the documentation for constants used) */
            public int Ioverflow; /* int Current overflow */
            public float ElapsedTime; /* single Elapsed time (s) */
            public float Freq; /* single Frequency (Hz) */
            public float Rcomp; /* single R compensation (Ohm) */
            public int Saturation; /* int E or/and I saturation */
            public int OptErr;
            public int OptPos;
        }

        public struct DataInfos
        {
            public int IRQskipped; /* int Number of IRQ skipped */
            public int NbRows; /* int Number of raws into the data buffer, i.e.number of points saved in the data buffer */
            public int NbCols; /* int Number of columns into the data buffer, i.e. number of variables defining a point in the data buffer */
            public int TechniqueIndex; /* int Index (0-based) of the technique who has generated the data. This field is only useful for linked techniques */
            public TechniqueIdentifier TechniqueID; /* int Identifier of the technique who has generated the data. Must be used to identify the data format into the data buffer (see section 4.2 in the documentation for constants used) */
            public int ProcessIndex; /* int Index (0-based) of the process of the technique who has generated the data. Must be used to identify the data format into the data buffer loop int Loop number */
            public int loop; /* Loop number */
            public double StartTime; /* double Start time (s) */
            public int MuxPad;
        }

        unsafe public struct DataBuffer
        {
            public fixed int data[1000];
        }

        unsafe public struct EccParam
        {
            public fixed byte str[64];
            public ParamType type;
            public int value;
            public int index;
        }

        unsafe public struct EccParams
        {
            public int len;
            public IntPtr pparams; // actually ECCParams, but Marshaling will fail if it is declared as public EccParam[] pparams.
        }

        public struct HardwareConf
        {
            public ElectrodeConnection conn;
            public ElectrodeMode mode;
        }


        /* ****************
         * Enum definitions
         * **************** */

        /* 
         * All enums shall have a size of an int (32 bits). 
         * This makes sure that the structures defined above are sized correctly. 
         */

        public enum ParamType : int
        {
            PARAM_INT = 0, /* Parameter type = int */
            PARAM_BOOLEAN = 1, /* Parameter type = boolean */
            PARAM_SINGLE = 2 /* Parameter type = single */
        }

        public enum DeviceType : int
        {
            KBIO_DEV_VMP = 0,       /*!< VMP device */
            KBIO_DEV_VMP2 = 1,      /*!< VMP2 device */
            KBIO_DEV_MPG = 2,       /*!< MPG device */
            KBIO_DEV_BISTAT = 3,    /*!< BISTAT device */
            KBIO_DEV_MCS200 = 4,    /*!< MCS-200 device */
            KBIO_DEV_VMP3 = 5,      /*!< VMP3 device */
            KBIO_DEV_VSP = 6,       /*!< VSP */
            KBIO_DEV_HCP803 = 7,    /*!< HCP-803 */
            KBIO_DEV_EPP400 = 8,    /*!< EPP-400 */
            KBIO_DEV_EPP4000 = 9,   /*!< EPP-4000 */
            KBIO_DEV_BISTAT2 = 10,  /*!< BISTAT 2 */
            KBIO_DEV_FCT150S = 11,  /*!< FCT-150S */
            KBIO_DEV_VMP300 = 12,   /*!< VMP-300 */
            KBIO_DEV_SP50 = 13,     /*!< SP-50 */
            KBIO_DEV_SP150 = 14,    /*!< SP-150 */
            KBIO_DEV_FCT50S = 15,   /*!< FCT-50S */
            KBIO_DEV_SP300 = 16,    /*!< SP300 */
            KBIO_DEV_CLB500 = 17,   /*!< CLB-500 */
            KBIO_DEV_HCP1005 = 18,  /*!< HCP-1005 */
            KBIO_DEV_CLB2000 = 19,  /*!< CLB-2000 */
            KBIO_DEV_VSP300 = 20,   /*!< VSP-300 */
            KBIO_DEV_SP200 = 21,    /*!< SP-200 */
            KBIO_DEV_MPG2 = 22,     /*!< MPG2 */
            KBIO_DEV_SP100 = 23,    /*!< SP-100 */
            KBIO_DEV_MOSLED = 24,   /*!< MOSLED */
            KBIO_DEV_KINEXXX = 25,  /*!< Kinetic device... \warning unused code */
            KBIO_DEV_NIKITA = 26,   /*!< Nikita */
            KBIO_DEV_SP240 = 27,    /*!< SP-240 */
            KBIO_DEV_MPG205 = 28,   /*!< MPG-205 (techno VMP3) \warning not controled by kernel2 */
            KBIO_DEV_MPG210 = 29,   /*!< MPG-210 (techno VMP3) \warning not controled by kernel2 */
            KBIO_DEV_MPG220 = 30,   /*!< MPG-220 (techno VMP3) \warning not controled by kernel2 */
            KBIO_DEV_MPG240 = 31,   /*!< MPG-240 (techno VMP3) \warning not controled by kernel2 */

            KBIO_DEV_UNKNOWN = 255
        }

        public enum FirmwareCode : int
        {
            KIBIO_FIRM_NONE = 0, /* No firmware loaded */
            KIBIO_FIRM_INTERPR = 1, /* Firmware for EC-Lab® software */
            KIBIO_FIRM_UNKNOWN = 4, /* Unknown firmware loaded */
            KIBIO_FIRM_KERNEL = 5, /* Firmware for the library */
            KIBIO_FIRM_INVALID = 8, /* Invalid firmware loaded */
            KIBIO_FIRM_ECAL = 10 /* Firmware for calibration software */
        }

        public enum AmplifierType : int
        {
            KIBIO_AMPL_NONE = 0,      /*!< No amplifier VMP3 series */
            KIBIO_AMPL_2A = 1,        /*!< Amplifier 2 A VMP3 series */
            KIBIO_AMPL_1A = 2,        /*!< Amplifier 1 A VMP3 series */
            KIBIO_AMPL_5A = 3,        /*!< Amplifier 5 A VMP3 series */
            KIBIO_AMPL_10A = 4,       /*!< Amplifier 10 A VMP3 series */
            KIBIO_AMPL_20A = 5,       /*!< Amplifier 20 A VMP3 series */
            KIBIO_AMPL_HEUS = 6,      /*!< reserved VMP3 series */
            KIBIO_AMPL_LC = 7,        /*!< Low current amplifier VMP3 series */
            KIBIO_AMPL_80A = 8,       /*!< Amplifier 80 A VMP3 series */
            KIBIO_AMPL_4AI = 9,       /*!< Amplifier 4 A VMP3 series */
            KIBIO_AMPL_PAC = 10,      /*!< Fuel Cell Tester VMP3 series */
            KIBIO_AMPL_4AI_VSP = 11,  /*!< Amplifier 4 A (VSP instrument) VMP3 series */
            KIBIO_AMPL_LC_VSP = 12,   /*!< Low current amplifier (VSP instrument) VMP3 series */
            KIBIO_AMPL_UNDEF = 13,    /*!< Undefined amplifier VMP3 series */
            KIBIO_AMPL_MUIC = 14,     /*!< reserved VMP3 series */
            KIBIO_AMPL_NONE_GIL = 15, /*!< No amplifier VMP3 series */
            KIBIO_AMPL_8AI = 16,      /*!< Amplifier 8 A VMP3 series */
            KIBIO_AMPL_LB500 = 17,    /*!< Amplifier LB500 VMP3 series */
            KIBIO_AMPL_100A5V = 18,   /*!< Amplifier 100 A VMP3 series */
            KIBIO_AMPL_LB2000 = 19,   /*!< Amplifier LB2000 VMP3 series */
            KBIO_AMPL_1A48V = 20,     /*!< Amplifier 1A 48V SP-300 series */
            KBIO_AMPL_4A10V = 21,     /*!< Amplifier 4A 10V SP-300 series */
            KBIO_AMPL_5A_MPG2B = 22, /*!< MPG-205 5A amplifier  */
            KBIO_AMPL_10A_MPG2B = 23, /*!< MPG-210 10A amplifier  */
            KBIO_AMPL_20A_MPG2B = 24, /*!< MPG-220 20A amplifier  */
            KBIO_AMPL_40A_MPG2B = 25, /*!< MPG-240 40A amplifier  */
            KBIO_AMPL_COIN_CELL_HOLDER = 26, /*!< coin cell holder */
            KBIO_AMPL4_10A5V = 27, /*!< VMP4 10A/5V amplifier (SP-300 internal amplifier) */
            KBIO_AMPL4_2A30V = 28, /*!< VMP4 2A/30V */
        }

        public enum IntensityRange : int
        {
            KBIO_IRANGE_100pA = 0,    /*!< I range 100 pA SP-300 series */
            KBIO_IRANGE_1nA = 1,      /*!< I range 1 nA VMP3 / SP-300 series */
            KBIO_IRANGE_10nA = 2,     /*!< I range 10 nA VMP3 / SP-300 series */
            KBIO_IRANGE_100nA = 3,    /*!< I range 100 nA VMP3 / SP-300 series */
            KBIO_IRANGE_1uA = 4,      /*!< I range 1 uA VMP3 / SP-300 series */
            KBIO_IRANGE_10uA = 5,     /*!< I range 10 uA VMP3 / SP-300 series */
            KBIO_IRANGE_100uA = 6,    /*!< I range 100 uA VMP3 / SP-300 series */
            KBIO_IRANGE_1mA = 7,      /*!< I range 1 mA VMP3 / SP-300 series */
            KBIO_IRANGE_10mA = 8,     /*!< I range 10 mA VMP3 / SP-300 series */
            KBIO_IRANGE_100mA = 9,    /*!< I range 100 mA VMP3 / SP-300 series */
            KBIO_IRANGE_1A = 10,      /*!< I range 1 A VMP3 / SP-300 series */
            KBIO_IRANGE_BOOSTER = 11, /*!< Booster VMP3 / SP-300 series */
            KBIO_IRANGE_AUTO = 12,    /*!< Auto range VMP3 / SP-300 series */
            KBIO_IRANGE_10pA = 13, /*!< IRANGE_100pA + Igain x10 */
            KBIO_IRANGE_1pA = 14, /*!< IRANGE_100pA + Igain x100 */
        }

        public enum VoltageRange : int
        {
            KBIO_ERANGE_2_5 = 0, /* ±2.5 V */
            KBIO_ERANGE_5 = 1, /* ±5 V */
            KBIO_ERANGE_10 = 2, /* ±10 V */
            KBIO_ERANGE_AUTO = 3 /* Auto range */
        }

        public enum OptionError : int
        {
            KBIO_OPT_NOERR = 0,   /*!< Option no error  */
            KBIO_OPT_CHANGE = 1,   /*!< Option change  */
            KBIO_OPT_4A10V_ERR = 100, /*!< Amplifier 4A10V error  */
            KBIO_OPT_4A10V_OVRTEMP = 101, /*!< Amplifier 4A10V overload temperature  */
            KBIO_OPT_4A10V_BADPOW = 102, /*!< Amplifier 4A10V invalid power  */
            KBIO_OPT_4A10V_POWFAIL = 103, /*!< Amplifier 4A10V power fail  */
            KBIO_OPT_1A48V_ERR = 200, /*!< Amplifier 1A48V error  */
            KBIO_OPT_1A48V_OVRTEMP = 201, /*!< Amplifier 1A48V overload temperature  */
            KBIO_OPT_1A48V_BADPOW = 202, /*!< Amplifier 1A48V invalid power  */
            KBIO_OPT_1A48V_POWFAIL = 203, /*!< Amplifier 1A48V power fail  */
            KBIO_OPT_10A5V_ERR = 300, /*!< Amplifier 10A5V error  */
            KBIO_OPT_10A5V_OVRTEMP = 301, /*!< Amplifier 10A5V overload temperature  */
            KBIO_OPT_10A5V_BADPOW = 302, /*!< Amplifier 10A5V invalid power  */
            KBIO_OPT_10A5V_POWFAIL = 303, /*!< Amplifier 10A5V power fail  */
        }

        public enum Bandwidth : int
        {
            KBIO_BW_1 = 1, /*!< Bandwidth #1 */
            KBIO_BW_2 = 2, /*!< Bandwidth #2 */
            KBIO_BW_3 = 3, /*!< Bandwidth #3 */
            KBIO_BW_4 = 4, /*!< Bandwidth #4 */
            KBIO_BW_5 = 5, /*!< Bandwidth #5 */
            KBIO_BW_6 = 6, /*!< Bandwidth #6 */
            KBIO_BW_7 = 7, /*!< Bandwidth #7 */
            KBIO_BW_8 = 8, /*!< Bandwidth #8 (only with SP-300 series) */
            KBIO_BW_9 = 9  /*!< Bandwidth #9 (only with SP-300 series) */
        }

        /** E/I gain constants */
        public enum Gain : int
        {
            KBIO_GAIN_1 = 0,
            KBIO_GAIN_10 = 1,
            KBIO_GAIN_100 = 2,
            KBIO_GAIN_1000 = 3
        }

        public enum ElectrodeConnection : int
        {
            KBIO_CONN_STD = 0, /* Standard connection */
            KBIO_CONN_CETOGRND = 1, /* CE to ground connection */
            KBIO_CONN_WETOGRND = 2,
            KBIO_CONN_HV = 3,
        }

        public enum ElectrodeMode : int
        {
            KBIO_MODE_GROUNDED = 0, /* Grounded mode */
            KBIO_MODE_FLOATING = 1 /* floating mode */
        }


        /** E/I filter constants */
        public enum FilterCut : int
        {
            KBIO_FILTER_NONE = 0,
            KBIO_FILTER_50KHZ = 1,
            KBIO_FILTER_1KHZ = 2,
            KBIO_FILTER_5HZ = 3,
        }

        public enum TechniqueIdentifier : int
        {
            KBIO_TECHID_NONE = 0,   /*!< None */
            KBIO_TECHID_OCV = 100, /*!< Open Circuit Voltage (Rest) identifier */
            KBIO_TECHID_CA = 101, /*!< Chrono-amperometry identifier */
            KBIO_TECHID_CP = 102, /*!< Chrono-potentiometry identifier */
            KBIO_TECHID_CV = 103, /*!< Cyclic Voltammetry identifier */
            KBIO_TECHID_PEIS = 104, /*!< Potentio Electrochemical Impedance Spectroscopy identifier */
            KBIO_TECHID_POTPULSE = 105, /*!< (unused) */
            KBIO_TECHID_GALPULSE = 106, /*!< (unused) */
            KBIO_TECHID_GEIS = 107, /*!< Galvano Electrochemical Impedance Spectroscopy identifier */
            KBIO_TECHID_STACKPEIS_SLAVE = 108, /*!< Potentio Electrochemical Impedance Spectroscopy on stack identifier */
            KBIO_TECHID_STACKPEIS = 109, /*!< Potentio Electrochemical Impedance Spectroscopy on stack identifier */
            KBIO_TECHID_CPOWER = 110, /*!< Constant Power identifier */
            KBIO_TECHID_CLOAD = 111, /*!< Constant Load identifier */
            KBIO_TECHID_FCT = 112, /*!< (unused) */
            KBIO_TECHID_SPEIS = 113, /*!< Staircase Potentio Electrochemical Impedance Spectroscopy identifier */
            KBIO_TECHID_SGEIS = 114, /*!< Staircase Galvano Electrochemical Impedance Spectroscopy identifier */
            KBIO_TECHID_STACKPDYN = 115, /*!< Potentio dynamic on stack identifier */
            KBIO_TECHID_STACKPDYN_SLAVE = 116, /*!< Potentio dynamic on stack identifier */
            KBIO_TECHID_STACKGDYN = 117, /*!< Galvano dynamic on stack identifier */
            KBIO_TECHID_STACKGEIS_SLAVE = 118, /*!< Galvano Electrochemical Impedance Spectroscopy on stack identifier */
            KBIO_TECHID_STACKGEIS = 119, /*!< Galvano Electrochemical Impedance Spectroscopy on stack identifier */
            KBIO_TECHID_STACKGDYN_SLAVE = 120, /*!< Galvano dynamic on stack identifier */
            KBIO_TECHID_CPO = 121, /*!< (unused) */
            KBIO_TECHID_CGA = 122, /*!< (unused) */
            KBIO_TECHID_COKINE = 123, /*!< (unused) */
            KBIO_TECHID_PDYN = 124, /*!< Potentio dynamic identifier */
            KBIO_TECHID_GDYN = 125, /*!< Galvano dynamic identifier */
            KBIO_TECHID_CVA = 126, /*!< Cyclic Voltammetry Advanced identifier */
            KBIO_TECHID_DPV = 127, /*!< Differential Pulse Voltammetry identifier */
            KBIO_TECHID_SWV = 128, /*!< Square Wave Voltammetry identifier */
            KBIO_TECHID_NPV = 129, /*!< Normal Pulse Voltammetry identifier */
            KBIO_TECHID_RNPV = 130, /*!< Reverse Normal Pulse Voltammetry identifier */
            KBIO_TECHID_DNPV = 131, /*!< Differential Normal Pulse Voltammetry identifier */
            KBIO_TECHID_DPA = 132, /*!< Differential Pulse Amperometry identifier */
            KBIO_TECHID_EVT = 133, /*!< Ecorr vs. time identifier */
            KBIO_TECHID_LP = 134, /*!< Linear Polarization identifier */
            KBIO_TECHID_GC = 135, /*!< Generalized corrosion identifier */
            KBIO_TECHID_CPP = 136, /*!< Cyclic Potentiodynamic Polarization identifier */
            KBIO_TECHID_PDP = 137, /*!< Potentiodynamic Pitting identifier */
            KBIO_TECHID_PSP = 138, /*!< Potentiostatic Pitting identifier */
            KBIO_TECHID_ZRA = 139, /*!< Zero Resistance Ammeter identifier */
            KBIO_TECHID_MIR = 140, /*!< Manual IR identifier */
            KBIO_TECHID_PZIR = 141, /*!< IR Determination with Potentiostatic Impedance identifier */
            KBIO_TECHID_GZIR = 142, /*!< IR Determination with Galvanostatic Impedance identifier */
            KBIO_TECHID_LOOP = 150, /*!< Loop (used for linked techniques) identifier */
            KBIO_TECHID_TO = 151, /*!< Trigger Out identifier */
            KBIO_TECHID_TI = 152, /*!< Trigger In identifier */
            KBIO_TECHID_TOS = 153, /*!< Trigger Set identifier */
            KBIO_TECHID_CPLIMIT = 155, /*!< Chrono-potentiometry with limits identifier */
            KBIO_TECHID_GDYNLIMIT = 156, /*!< Galvano dynamic with limits identifier */
            KBIO_TECHID_CALIMIT = 157, /*!< Chrono-amperometry with limits identifier */
            KBIO_TECHID_PDYNLIMIT = 158, /*!< Potentio dynamic with limits identifier */
            KBIO_TECHID_LASV = 159, /*!< Large amplitude sinusoidal voltammetry */
            KBIO_TECHID_MUXLOOP = 160,
            KBIO_TECHID_CVCA = 161,
            KBIO_TECHID_CVCA_SLAVE = 162,
            KBIO_TECHID_CPCA = 163,
            KBIO_TECHID_CPCA_SLAVE = 164,
            KBIO_TECHID_CACA = 165,
            KBIO_TECHID_CACA_SLAVE = 166,
            KBIO_TECHID_MP = 167, /*!< Modular Pulse */
            KBIO_TECHID_CASG = 169, /*!< Constant amplitude sinusoidal micro galvano polarization */
            KBIO_TECHID_CASP = 170, /*!< Constant amplitude sinusoidal micro potentio polarization */
            KBIO_TECHID_VASP = 171,
            KBIO_TECHID_UCVANALOG = 172,

            KBIO_TECHID_OCVR = 500,
            KBIO_TECHID_CAR = 501,
            KBIO_TECHID_CPR = 502,

            KBIO_TECHID_ABS = 1000,
            KBIO_TECHID_FLUO = 1001,
            KBIO_TECHID_RABS = 1002,
            KBIO_TECHID_RFLUO = 1003,
            KBIO_TECHID_RDABS = 1004,
            KBIO_TECHID_DABS = 1005,
            KBIO_TECHID_ABSFLUO = 1006,
            KBIO_TECHID_RAFABS = 1007,
            KBIO_TECHID_RAFFLUO = 1008,
        }

        public enum ChannelState : int
        {
            KBIO_STATE_STOP = 0, /* Channel is stopped */
            KBIO_STATE_RUN = 1, /* Channel is running */
            KBIO_STATE_PAUSE = 2 /* Channel is paused */
        }

        public enum ErrorCode : int
        {
            ERR_NOERROR = 0,
            /* General error codes */
            ERR_GEN_NOTCONNECTED = -1, /* no instrument connected */
            ERR_GEN_CONNECTIONINPROGRESS = -2, /* connection in progress */
            ERR_GEN_CHANNELNOTPLUGGED = -3, /* selected channel(s) unplugged */
            ERR_GEN_INVALIDPARAMETERS = -4, /* invalid function parameters */
            ERR_GEN_FILENOTEXISTS = -5, /* selected file does not exist */
            ERR_GEN_FUNCTIONFAILED = -6, /* function failed */
            ERR_GEN_NOCHANNELELECTED = -7, /* no channel selected */
            ERR_GEN_INVALIDCONF = -8, /* invalid instrument configuration */
            ERR_GEN_ECLAB_LOADED = -9, /* EC-Lab® firmware loaded on the instrument */
            ERR_GEN_LIBNOTCORRECTLYLOADED = -10, /* library not correctly loaded in memory */
            ERR_GEN_USBLIBRARYERROR = -11, /* USB library not correctly loaded in memory */
            ERR_GEN_FUNCTIONINPROGRESS = -12, /* function of the library already in progress */
            ERR_GEN_CHANNEL_RUNNING = -13, /* selected channel(s) already used */
            ERR_GEN_DEVICE_NOTALLOWED = -14, /* device not allowed */
            ERR_GEN_UPDATEPARAMETERS = -15, /* Invalid update function parameters */


            /* Instrument error codes */
            ERR_INSTR_VMEERROR = -101, /* internal instrument communication failed */
            ERR_INSTR_TOOMANYDATA = -102, /* too many data to transfer from the instrument (device error) */
            ERR_INSTR_RESPNOTPOSSIBLE = -103, /* selected channel(s) unplugged (device error) */
            ERR_INSTR_RESPERROR = -104, /*!< instrument response error */
            ERR_INSTR_MSGSIZEERROR = -105, /*!< invalid message size */

            /* Communication error codes */
            ERR_COMM_COMMFAILED = -200, /* communication failed with the instrument */
            ERR_COMM_CONNECTIONFAILED = -201, /* cannot establish connection with the instrument */
            ERR_COMM_WAITINGACK = -202, /* waiting for the instrument response */
            ERR_COMM_INVALIDIPADDRESS = -203, /* invalid IP address */
            ERR_COMM_ALLOCMEMFAILED = -204, /* cannot allocate memory in the instrument */
            ERR_COMM_LOADFIRMWAREFAILED = -205, /* cannot load firmware into selected channel(s) */
            ERR_COMM_INCOMPATIBLESERVER = -206, /* communication firmware not compatible with the library */
            ERR_COMM_MAXCONNREACHED = -207, /* maximum number of allowed connections reached */


            /* Firmware error codes */
            ERR_FIRM_FIRMFILENOTEXISTS = -300, /* cannot find kernel.bin file */
            ERR_FIRM_FIRMFILEACCESSFAILED = -301, /* cannot read kernel.bin file */
            ERR_FIRM_FIRMINVALIDFILE = -302, /* invalid kernel.bin file */
            ERR_FIRM_FIRMLOADINGFAILED = -303, /* cannot load kernel.bin on the selected channel(s) */
            ERR_FIRM_XILFILENOTEXISTS = -304, /* cannot find x100_01.txt file */
            ERR_FIRM_XILFILEACCESSFAILED = -305, /* cannot read x100_01.txt file */
            ERR_FIRM_XILINVALIDFILE = -306, /* invalid x100_01.txt file */
            ERR_FIRM_XILLOADINGFAILED = -307, /* cannot load x100_01.txt file on the selected channel(s) */
            ERR_FIRM_FIRMWARENOTLOADED = -308, /* no firmware loaded on the selected channel(s) */
            ERR_FIRM_FIRMWAREINCOMPATIBLE = -309, /* loaded firmware not compatible with the library */

            /* Technique error codes */
            ERR_TECH_ECCFILENOTEXISTS = -400, /* cannot find the selected ECC file */
            ERR_TECH_INCOMPATIBLEECC = -401, /* ECC file not compatible with the channel firmware */
            ERR_TECH_ECCFILECORRUPTED = -402, /* ECC file corrupted */
            ERR_TECH_LOADTECHNIQUEFAILED = -403, /* cannot load the ECC file */
            ERR_TECH_DATACORRUPTED = -404, /* data returned by the instrument are corrupted */
            ERR_TECH_MEMFULL = -405 /* cannot load techniques: full memory */
        }

    }
}
