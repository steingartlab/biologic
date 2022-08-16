
#pragma once

#ifndef _BLWRAP_H_
#define _BLWRAP_H_

#include "targetver.h"
#include <afx.h>
#include <BLStructs.h>

/*
 * Bio-Logic Header file for ECLib C/C++ interface (dynamic version)
 */


/* forward declaration, see at the end of the file for the structure definition */
typedef struct _TEClibFunctions TEClibFunctions;
typedef unsigned char uint8;


/**
 * \defgroup lifecycle_functions Lifecycle Functions
 * Lifecycle management, use these functions early and at the end
 * in your code to load/unload the DLL.
 *
 * Short example:
 \code

 TECLibFunctions *functions = 0;
 if( BL_Init( _T("ECLib.dll"), &functions ) == ERR_NOERROR ){
     char version[64];
     unsigned int size = 64;
     // now you can use the function pointers
     functions->BL_GetLibVersion( version, &size );
 }
 BL_End();
 // functions pointer is now invalid

 \endcode
 *
 * @{
 */


/**
 * \brief This function initializes a \ref _TEClibFunctions structure and returns a pointer to it.
 *
 * \note You should use this function at the very beginning of your program. Provided that
 * you give it a good path, you will get in return a pointer to a TECLibFunctions
 * structure that you will be able to use throughout your program to communicate with 
 * the Bio Logic instruments.
 * If the function fails, you should make sure not to use any BL_* function pointers.
 *
 * @param eclibPath the full path of the ECLib DLL, including the DLL name
 * @param functions reference to a pointer which will get the value of the initialized structure.
 * @return \ref ERR_NOERROR if successful, \ref ERR_GEN_INVALIDPARAMETERS or \ref ERR_GEN_FUNCTIONFAILED in case of errors.
 */
TErrorCodes_e BL_Init( const CString& eclibPath, TEClibFunctions*& function );

/**
 * This function releases the DLL that was loaded in \ref BL_Init and clears out 
 * the internal \ref _TEClibFunctions structure.
 * Call this at the end of your program to make sure that all resources are freed.
 * @return \ref ERR_NOERROR
 */
TErrorCodes_e BL_End( void );

/** \ingroup structures
 * @{ */


/** Pointer to a \ref BL_GetLibVersion function */
typedef int    (__stdcall *BL_GETLIBVERSION_FP)( char* pVersion, unsigned int* psize );
/** Pointer to a \ref BL_GetVolumeSerialNumber function */
typedef unsigned int   (__stdcall *BL_GETVOLUMESERIALNUMBER_FP)( void );
/** Pointer to a \ref BL_GetErrorMsg function */
typedef int    (__stdcall *BL_GETERRORMSG_FP)( int errorcode, char* pmsg, unsigned int* psize );

/** Pointer to a \ref BL_Connect function */
typedef int  (__stdcall *BL_CONNECT_FP)( const char* address, uint8 timeout, int* pID, TDeviceInfos_t* pInfos );
/** Pointer to a \ref BL_Disconnect function */
typedef int  (__stdcall *BL_DISCONNECT_FP)( int ID );
/** Pointer to a \ref BL_TestConnection function */
typedef int  (__stdcall *BL_TESTCONNECTION_FP)( int ID );
/** Pointer to a \ref BL_TestCommSpeed function */
typedef int  (__stdcall *BL_TESTCOMMSPEED_FP)( int ID, uint8 channel, int* spd_rcvt, int* spd_kernel);
/** Pointer to a \ref BL_GetUSBdeviceinfos function */
typedef bool   (__stdcall *BL_GETUSBDEVICEINFOS_FP)(unsigned int USBindex, char* pcompany, unsigned int* pcompanysize, char* pdevice,  unsigned int* pdevicesize, char* pSN, unsigned int* pSNsize );

/** Pointer to a \ref BL_LoadFirmware function */
typedef int (__stdcall *BL_LOADFIRMWARE_FP)( int ID, uint8* pChannels, int* pResults, uint8 Length, bool ShowGauge, bool ForceReload, const char* BinFile, const char* XlxFile );

/** Pointer to a \ref BL_IsChannelPlugged function */
typedef bool   (__stdcall *BL_ISCHANNELPLUGGED_FP)( int ID, uint8 ch );
/** Pointer to a \ref BL_GetChannelsPlugged function */
typedef int  (__stdcall *BL_GETCHANNELSPLUGGED_FP)( int ID, uint8* pChPlugged, uint8 Size );
/** Pointer to a \ref BL_GetChannelInfos function */
typedef int  (__stdcall *BL_GETCHANNELINFOS_FP)( int ID, uint8 ch, TChannelInfos_t* infos );
/** Pointer to a \ref BL_GetMessage function */
typedef int  (__stdcall *BL_GETMESSAGE_FP)( int ID, uint8 ch, char* msg, unsigned int* size );
/** Pointer to a \ref BL_GetHardConf function */
typedef int  (__stdcall *BL_GETHARDCONF_FP)(int ID, uint8 ch, THardwareConf_t* pHardConf );
/** Pointer to a \ref BL_SetHardConf function */
typedef int  (__stdcall *BL_SETHARDCONF_FP)(int ID, uint8 ch, THardwareConf_t HardConf );

/** Pointer to a \ref BL_LoadTechnique function */
typedef int (__stdcall *BL_LOADTECHNIQUE_FP)( int ID, uint8 channel, const char* pFName, TEccParams_t Params, bool FirstTechnique, bool LastTechnique, bool DisplayParams );
/** Pointer to a \ref BL_DefineBoolParameter function */
typedef int (__stdcall *BL_DEFINEBOOLPARAMETER_FP)( const char* lbl, bool  value, int index, TEccParam_t* pParam );
/** Pointer to a \ref BL_DefineSglParameter function */
typedef int (__stdcall *BL_DEFINESGLPARAMETER_FP)(const char* lbl, float value, int index, TEccParam_t* pParam );
/** Pointer to a \ref BL_DefineIntParameter function */
typedef int (__stdcall *BL_DEFINEINTPARAMETER_FP)(const char* lbl,  int   value, int index, TEccParam_t* pParam );
/** Pointer to a \ref BL_UpdateParameters function */
typedef int (__stdcall *BL_UPDATEPARAMETERS_FP)( int ID, uint8 channel, int TechIndx, TEccParams_t Params, const char* EccFileName );

/** Pointer to a \ref BL_StartChannel function */
typedef int  (__stdcall *BL_STARTCHANNEL_FP)( int ID, uint8 channel );
/** Pointer to a \ref BL_StartChannels function */
typedef int  (__stdcall *BL_STARTCHANNELS_FP)( int ID, uint8* pChannels, int* pResults, uint8 length );
/** Pointer to a \ref BL_StopChannel function */
typedef int  (__stdcall *BL_STOPCHANNEL_FP)( int ID, uint8 channel );
/** Pointer to a \ref BL_StopChannels function */
typedef int  (__stdcall *BL_STOPCHANNELS_FP)( int ID, uint8* pChannels, int* pResults, uint8 length );

/** Pointer to a \ref BL_GetCurrentValues function */
typedef int  (__stdcall *BL_GETCURRENTVALUES_FP)( int ID, uint8 channel, TCurrentValues_t* pValues );
/** Pointer to a \ref BL_GetData function */
typedef int  (__stdcall *BL_GETDATA_FP)( int ID, uint8 channel, TDataBuffer_t* pBuf, TDataInfos_t* pInfos, TCurrentValues_t* pValues );
/** Pointer to a \ref BL_GetFCTData function */
typedef int  (__stdcall *BL_GETFCTDATA_FP)( int ID, uint8 channel, TDataBuffer_t* pBuf, TDataInfos_t* pInfos, TCurrentValues_t* pValues );
/** Pointer to a \ref BL_ConvertNumericIntoSingle function */
typedef int  (__stdcall *BL_CONVERTNUMERICINTOSINGLE_FP)( unsigned int num, float* psgl );

/** Pointer to a \ref BL_SetExperimentInfos function */
typedef int  (__stdcall *BL_SETEXPERIMENTINFOS_FP)( int ID, uint8 channel, TExperimentInfos_t TExpInfos );
/** Pointer to a \ref BL_GetExperimentInfos function */
typedef int  (__stdcall *BL_GETEXPERIMENTINFOS_FP)( int ID, uint8 channel, TExperimentInfos_t* TExpInfos );
/** Pointer to a \ref BL_SendMsg function */
typedef int  (__stdcall *BL_SENDMSG_FP)( int ID, uint8 ch, void* pBuf, unsigned int* pLen );
/** Pointer to a \ref BL_LoadFlash function */
typedef int  (__stdcall *BL_LOADFLASH_FP)( int ID, const char* pfname, bool ShowGauge );


/**
 * @}
 * \ingroup lifecycle_functions
 * This structure holds information about the DLL file that is loaded
 * when \ref BL_Init is called, and a function pointer to all the functions
 * described in this header file.
 *
 * In your program, the usual way of interacting with the ECLib package is by using this
 * structure and the function pointers it contains.
 *
 */
struct _TEClibFunctions
{
    HMODULE hECLibDll; /*!<  handle to the ECLib DLL (which is obtained by using LoadLibrary() from the Windows API */

    /* function pointers */
    BL_GETLIBVERSION_FP         BL_GetLibVersion;           /*!< function pointer to the BL_GetLibVersion function */
    BL_GETVOLUMESERIALNUMBER_FP BL_GetVolumeSerialNumber;   /*!< function pointer to the BL_GetVolumeSerialNumber function */
    BL_GETERRORMSG_FP           BL_GetErrorMsg;             /*!< function pointer to the BL_GetErrorMsg function */
    BL_CONNECT_FP               BL_Connect;                 /*!< function pointer to the BL_Connect function */
    BL_DISCONNECT_FP            BL_Disconnect;              /*!< function pointer to the BL_Disconnect function */
    BL_TESTCONNECTION_FP        BL_TestConnection;          /*!< function pointer to the BL_TestConnection function */
    BL_TESTCOMMSPEED_FP         BL_TestCommSpeed;           /*!< function pointer to the BL_TestCommSpeed function */
    BL_GETUSBDEVICEINFOS_FP     BL_GetUSBdeviceinfos;       /*!< function pointer to the BL_GetUSBdeviceinfos function */
    BL_LOADFIRMWARE_FP          BL_LoadFirmware;            /*!< function pointer to the BL_LoadFirmware function */
    BL_ISCHANNELPLUGGED_FP      BL_IsChannelPlugged;        /*!< function pointer to the BL_IsChannelPlugged function */
    BL_GETCHANNELSPLUGGED_FP    BL_GetChannelsPlugged;      /*!< function pointer to the BL_GetChannelsPlugged function */
    BL_GETCHANNELINFOS_FP       BL_GetChannelInfos;         /*!< function pointer to the BL_GetChannelInfos function */
    BL_GETMESSAGE_FP            BL_GetMessage;              /*!< function pointer to the BL_GetMessage function */
    BL_GETHARDCONF_FP           BL_GetHardConf;             /*!< function pointer to the BL_GetHardConf function */
    BL_SETHARDCONF_FP           BL_SetHardConf;             /*!< function pointer to the BL_SetHardConf function */
    BL_LOADTECHNIQUE_FP         BL_LoadTechnique;           /*!< function pointer to the BL_LoadTechnique function */
    BL_DEFINEBOOLPARAMETER_FP   BL_DefineBoolParameter;     /*!< function pointer to the BL_DefineBoolParameter function */
    BL_DEFINESGLPARAMETER_FP    BL_DefineSglParameter;      /*!< function pointer to the BL_DefineSglParameter function */
    BL_DEFINEINTPARAMETER_FP    BL_DefineIntParameter;      /*!< function pointer to the BL_DefineIntParameter function */
    BL_UPDATEPARAMETERS_FP      BL_UpdateParameters;        /*!< function pointer to the BL_UpdateParameters function */
    BL_STARTCHANNEL_FP          BL_StartChannel;            /*!< function pointer to the BL_StartChannel function */
    BL_STARTCHANNELS_FP         BL_StartChannels;           /*!< function pointer to the BL_StartChannels function */
    BL_STOPCHANNEL_FP           BL_StopChannel;             /*!< function pointer to the BL_StopChannel function */
    BL_STOPCHANNELS_FP          BL_StopChannels;            /*!< function pointer to the BL_StopChannels function */
    BL_GETCURRENTVALUES_FP      BL_GetCurrentValues;        /*!< function pointer to the BL_GetCurrentValues function */
    BL_GETDATA_FP               BL_GetData;                 /*!< function pointer to the BL_GetData function */
    BL_GETFCTDATA_FP            BL_GetFCTData;              /*!< function pointer to the BL_GetFCTData function */
    BL_CONVERTNUMERICINTOSINGLE_FP BL_ConvertNumericIntoSingle; /*!< function pointer to the BL_ConvertNumericIntoSingle function */
    BL_SETEXPERIMENTINFOS_FP    BL_SetExperimentInfos;      /*!< function pointer to the BL_SetExperimentInfos function */
    BL_GETEXPERIMENTINFOS_FP    BL_GetExperimentInfos;      /*!< function pointer to the BL_GetExperimentInfos function */
    BL_SENDMSG_FP               BL_SendMsg;                 /*!< function pointer to the BL_SendMsg function */
    BL_LOADFLASH_FP             BL_LoadFlash;               /*!< function pointer to the BL_LoadFlash function */

};

/** @} */

#endif /* _BLWRAP_H_*/
