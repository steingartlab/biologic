#include "BLWrap.h"

#include <WinBase.h>
#include <atlbase.h>
#include <stdio.h>


static BOOL initialized = false;
static TEClibFunctions  ECLib;

/* This function returns 0 if the procedure was found, 1 otherwise */
static INT32 BL_getProcFor( FARPROC *procedure, const char* procedure_name, HMODULE dll ){
    INT32 status = 1;
    if( dll && procedure_name && procedure )
    {
        *procedure = GetProcAddress( dll, procedure_name );
        if( !*procedure ){
            printf("Could not find the procedure '%s' in the DLL file.\n", procedure_name );
        } else {
            status = 0; /* all good */
        }
    }
    return status;
}

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
TErrorCodes_e BL_Init( const CString &eclibPath, TEClibFunctions*& functions )
{
    if( eclibPath.IsEmpty() ) return ERR_GEN_INVALIDPARAMETERS;

    TErrorCodes_e status = BL_End(); /* protection against multiple calls */

    ECLib.hECLibDll = LoadLibrary(eclibPath);

    if( ECLib.hECLibDll != 0 ){
        BOOL error = false;

        /* Try to get all the procedures addresses from the DLL. */
#define GET_PROC( name ) BL_getProcFor( (FARPROC *)&(ECLib.name), #name, ECLib.hECLibDll )
        error |= GET_PROC( BL_GetLibVersion );
        // error |= BL_getProcFor( (FARPROC *)&(ECLib.BL_GetLibVersion), "BL_GetLibVersion", ECLib.hECLibDll );
        error |= GET_PROC( BL_GetVolumeSerialNumber );
        error |= GET_PROC( BL_GetErrorMsg );
        error |= GET_PROC( BL_Connect );
        error |= GET_PROC( BL_Disconnect );
        error |= GET_PROC( BL_TestConnection );
        error |= GET_PROC( BL_TestCommSpeed );
        error |= GET_PROC( BL_GetUSBdeviceinfos );
        error |= GET_PROC( BL_LoadFirmware );
        error |= GET_PROC( BL_IsChannelPlugged );
        error |= GET_PROC( BL_GetChannelsPlugged );
        error |= GET_PROC( BL_GetChannelInfos );
        error |= GET_PROC( BL_GetMessage );
        error |= GET_PROC( BL_GetHardConf );
        error |= GET_PROC( BL_SetHardConf );
        error |= GET_PROC( BL_LoadTechnique );
        error |= GET_PROC( BL_DefineBoolParameter );
        error |= GET_PROC( BL_DefineSglParameter );
        error |= GET_PROC( BL_DefineIntParameter );
        error |= GET_PROC( BL_UpdateParameters );
        error |= GET_PROC( BL_StartChannel );
        error |= GET_PROC( BL_StartChannels );
        error |= GET_PROC( BL_StopChannel );
        error |= GET_PROC( BL_StopChannels );
        error |= GET_PROC( BL_GetCurrentValues );
        error |= GET_PROC( BL_GetData );
        error |= GET_PROC( BL_GetFCTData );
        error |= GET_PROC( BL_ConvertNumericIntoSingle );
        error |= GET_PROC( BL_SetExperimentInfos );
        error |= GET_PROC( BL_GetExperimentInfos );
        error |= GET_PROC( BL_SendMsg );
        error |= GET_PROC( BL_LoadFlash );

        if( error ){
            printf("An error occured while retrieving the DLL functions. You should abort.\n");
            status = ERR_GEN_FUNCTIONFAILED;
        } else {
            functions = &ECLib;
        }
    } else {
        status = ERR_GEN_FUNCTIONFAILED;
    }

    initialized = true;

    return status;
}

/**
 * This function releases the DLL that was loaded in \ref BL_Init and clears out 
 * the internal \ref _TEClibFunctions structure.
 * Call this at the end of your program to make sure that all resources are freed.
 * @return \ref ERR_NOERROR
 */
TErrorCodes_e BL_End( void ){
    
    if( initialized && ECLib.hECLibDll != 0 ){
        FreeLibrary( ECLib.hECLibDll );
    }
    memset(&ECLib, 0, sizeof( TEClibFunctions ) );

    initialized = false;

    return ERR_NOERROR;
}
