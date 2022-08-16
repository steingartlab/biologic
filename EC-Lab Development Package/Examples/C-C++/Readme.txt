================================================================================
    ECLab Development Package: C/C++ examples
================================================================================

This folder contains examples about how to use the ECLib DLL within a C code.

Here is a short description of the structure of this folder:

- lib/                  : Folder where the C-specific files are placed
    * ECLib.lib         : Use this file to link you application with ECLib.dll
    * BLFunctions.h     : C Header declaring the C bindings to ECLib.dll
    * BLStructs.h       : C Header declaring the C structures for ECLib.dll

- VisualStudio/         : Example for VisualStudio
    * MFCStaticLink/    : C++ example using the ECLib.lib and static link
    * MFCDynamicDLLCall/: C++ example using dynamic DLL loading

/////////////////////////////////////////////////////////////////////////////


You can refer to the Examples' Readme files for more informations on how these 
examples work, and in the code which is documented.