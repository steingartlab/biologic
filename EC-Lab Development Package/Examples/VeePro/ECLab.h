#include <stdio.h>

/*typedef struct DeviceInfos{
int DeviceCode;
int RAMsize;
int CPU;
int NumberOfChannels;
int NumberOfSlots;
int FirmwareVersion;
int FirmwareDate_yyyy;
int FirmwareDate_mm;
int  FirmwareDate_dd;
int  HTdisplayOn;
int  NbOfConnectedPC;
}TDeviceInfos;

struct TDeviceInfos{
int32 DeviceCode;
int32 RAMsize;
int32 CPU;
int32 NumberOfChannels;
int32 NumberOfSlots;
int32 FirmwareVersion;
int32 FirmwareDate_yyyy;
int32 FirmwareDate_mm;
int32  FirmwareDate_dd;
int32  HTdisplayOn;
int32  NbOfConnectedPC;
};
		struct TChannelInfos
    {
		__int32 Channel;
		__int32 BoardVersion;
	    __int32 BoardSerialNumber;
		__int32 FirmwareVersion;
		__int32 FirmwareCode;
		__int32 XilinxVersion;
		__int32 AmpCode;
		__int32 Zboard;
		__int32 MemSize;
		__int32 MemFilled;
		__int32 State;
		__int32 MaxIRange;
		__int32 MinIRange;
		__int32 MaxBandwith;
		__int32 NbOfTechniques;
	};

		struct   TCurrentValues
	{
		__int32 State;
        __int32 MemFilled;
        float TimeBase;
        float Ewe;
        float EweRangeMin;
        float EweRangeMax;
		float Ece;
        float EceRangeMin;
        float EceRangeMax;
        __int32 EOverFlow;    
        float I;
        __int32 IRange;
        __int32 Ioverflow;
        float ElapsedTime;
        float Freq;
        float Rcomp;

	};

		struct TDataInfos
    {
		__int32 IRQskipped;
		__int32 NbRaws;
	    __int32 NbCols;
		__int32 TechniqueIndex;
		__int32 TechniqueID;
		__int32 ProcessIndex;
		__int32 loop;
		double StartTime;
		TCurrentValues CurrentValues;  
    };

		  struct TECCPARAM
    {
		char ParamStr[64];
		__int32 ParamType;
		__int32 ParamVal;
		__int32 ParamIndex;
	};

		typedef TECCPARAM (*PtrEccParam);

		struct TECCPARAMS
    {
		__int32 len;
		PtrEccParam pECCPARAM;

    };
*/
		int __declspec(dllimport) __stdcall BL_Connect(char* pChar , int timeOut, int* pID, int pInfos[11] );
        int __declspec(dllimport) __stdcall BL_Disconnect(int ID);
        int __declspec(dllimport) __stdcall BL_GetChannelsPlugged(int ID, byte* Channels, int size);
        //int __declspec(dllimport) __stdcall BL_LoadFirmware(int ID, int pChannels[16] , int pResults[16], int length, int ShowGauge, int ForceLoad, char* BinFile, char* XlxFile);
		int __declspec(dllimport) __stdcall BL_LoadFirmware(int ID, byte* pChannels , int* pResults, int length, int ShowGauge, int ForceLoad, char* BinFile, char* XlxFile);
		int __declspec(dllimport) __stdcall BL_LoadTechnique_VEE(int ID, int ch, char* pFName,  char** ppParams, int bFirstTechnique, int bLastTechnique, int bDisplayParams);
		int __declspec(dllimport) __stdcall BL_UpdateParameters_VEE(int ID, int ch, int TechIndx,  char** ppParams, char* FNameEcc);
		int __declspec(dllimport) __stdcall BL_StartChannel(int ID, int Ch);
		int __declspec(dllimport) __stdcall BL_GetData_VEE(int ID, int ch, int PDataBuffer[1000],  double pInfos[24]);
		
  /*      __int32 __declspec(dllimport) __stdcall BL_GetChannelsPlugged(__int32 , unsigned __int8* , unsigned __int8 );
        __int32 __declspec(dllimport) __stdcall BL_IsChannelPlugged(__int32 , unsigned __int8 );
        __int32 __declspec(dllimport) __stdcall BL_LoadFirmware(__int32 , unsigned __int8* , __int32* , unsigned __int8 , bool , bool );
        __int32 __declspec(dllimport) __stdcall BL_GetChannelInfos(__int32 , unsigned __int8*, TChannelInfos* );
        __int32 __declspec(dllimport) __stdcall BL_GetMessage(__int32 , unsigned __int8 , char* ,unsigned  __int32* );
        __int32 __declspec(dllimport) __stdcall BL_LoadTechnique(__int32 ID, unsigned __int8 ch, char* szFilename,  TECCPARAMS Params, bool bFirstTechnique, bool bLastTechnique, bool bDisplayParams);
        __int32 __declspec(dllimport) __stdcall BL_DefineBoolParameter(const char* , bool , __int32 , TECCPARAM* );
		__int32 __declspec(dllimport) __stdcall BL_DefineSglParameter(const char* , float , __int32 , TECCPARAM* );
   		__int32 __declspec(dllimport) __stdcall BL_DefineIntParameter(const char* , __int32 , __int32 , TECCPARAM* );
        __int32 __declspec(dllimport) __stdcall BL_StartChannel(__int32 , unsigned __int8 );
        //__int32 __declspec(dllimport) __stdcall BL_StartChannels(__int32 , unsigned __int8* , __int32* , unsigned __int8 );
        __int32 __declspec(dllimport) __stdcall BL_StopChannel(__int32 , unsigned __int8 );
        //__int32 __declspec(dllimport) __stdcall BL_StopChannels(__int32 , unsigned __int8* , __int32* , unsigned __int8 );
        __int32 __declspec(dllimport) __stdcall BL_GetCurrentValues(__int32 , unsigned __int8 , TCurrentValues* );
        __int32 __declspec(dllimport) __stdcall BL_GetData(__int32 , unsigned __int8 ,unsigned __int32* ,  TDataInfos* );
*/
