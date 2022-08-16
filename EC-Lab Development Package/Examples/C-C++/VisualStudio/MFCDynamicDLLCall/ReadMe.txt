================================================================================
    ECLab Development Package: MFC Sample Project Overview
================================================================================

This MFCSample application was created using the standard Visual Studio wizard
to demonstrate how to use the ECLib DLL file from the EC Lab Development package.
This application uses a Dialog-based interface which might not be suitable
for a larger application, but is sufficient to show how to use the C/C++
interfaces to the ECLib DLL.

This file contains a summary of what you will find in each of the files that
make up the MFCSample code base.

The solution file is from Visual Studio 2012, but is compatible with Visual 
Studio 2010 SP1. Older versions of Visual Studio will require to re-create a 
project from scratch, but the code should be compatible.

/////////////////////////////////////////////////////////////////////////////

Important files:

MFCSampleDlg.h, MFCSampleDlg.cpp - the dialog
    These files contain the CMFCSampleDlg class.  This class defines
    the behavior of your application's main dialog.  The dialog's template is
    in MFCSample.rc, which can be edited in Microsoft Visual C++. 
    This is the class where all the program mechanics are taking place:
        - connecting to the Bio Logic instrument
        - configuring the channel Techniques and starting the acquisition
        - consuming the data coming from the device.
    It uses threads to consume data without blocking the main windows.

BLWrap.h / BLWrap.cpp - The interface files to the ECLib DLL
    These two files define a certain amount of function pointers which are used
    to communicate with the ECLib DLL. You can see in the CPP file that the DLL
    is opened and the symbols of all the functions are linked to a function 
    pointer in the BL_init() function. This should be your entry point.
    The functions themselves are the one described in the ECLab development
    package.

BLStructs.h - Bio Logic definitions
    This file is located in the ../../lib/ directory.
    In this file are laid all the structures and enumerations that the ECLib 
    API uses. They correspond to their Delphi equivalent that are described
    in the ECLab development package manual, but with the C types.

/////////////////////////////////////////////////////////////////////////////

Other standard files:

MFCSample.vcxproj
    This is the main project file for VC++ projects generated using an application wizard.
    It contains information about the version of Visual C++ that generated the file, and
    information about the platforms, configurations, and project features selected with the
    application wizard.

MFCSample.vcxproj.filters
    This is the filters file for VC++ projects generated using an Application Wizard. 
    It contains information about the association between the files in your project 
    and the filters. This association is used in the IDE to show grouping of files with
    similar extensions under a specific node (for e.g. ".cpp" files are associated with the
    "Source Files" filter).

MFCSample.h
    This file defines the "main" class that will be in charge of setting up the Windows APIs
    to display the MFCSampleDlg dialog. There is no Bio-Logic specific code in this file.

MFCSample.cpp
    This is the main application source file that contains the application
    class CMFCSampleApp. There is no Bio-Logic specific code in this file.

MFCSample.rc
    This is a listing of all of the Microsoft Windows resources that the
    program uses.  It includes the icons, bitmaps, and cursors that are stored
    in the RES subdirectory.  This file can be directly edited in Microsoft
    Visual C++.

res\MFCSample.ico
    This is an icon file, which is used as the application's icon.  This
    icon is included by the main resource file MFCSample.rc.

res\MFCSample.rc2
    This file contains resources that are not edited by Microsoft
    Visual C++. You should place all resources not editable by
    the resource editor in this file.

StdAfx.h, StdAfx.cpp
    These files are used to build a precompiled header (PCH) file
    named MFCSample.pch and a precompiled types file named StdAfx.obj.
    Note that the precompilation has been disabled in this project.

Resource.h
    This is the standard header file, which defines new resource IDs.
    Microsoft Visual C++ reads and updates this file automatically.

MFCSample.manifest
	Application manifest files are used by Windows XP to describe an applications
	dependency on specific versions of Side-by-Side assemblies. The loader uses this
	information to load the appropriate assembly from the assembly cache or private
	from the application. The Application manifest  maybe included for redistribution
	as an external .manifest file that is installed in the same folder as the application
	executable or it may be included in the executable in the form of a resource.
