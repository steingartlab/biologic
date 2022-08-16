
// MFCSample.cpp : Defines the class behaviors for the application.
//

#include "stdafx.h"
#include "MFCSample.h"
#include "MFCSampleDlg.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// CMFCSampleApp

BEGIN_MESSAGE_MAP(CMFCSampleApp, CWinApp)
END_MESSAGE_MAP()


CMFCSampleApp::CMFCSampleApp()
{
}

CMFCSampleApp theApp;

BOOL CMFCSampleApp::InitInstance()
{
    INITCOMMONCONTROLSEX InitCtrls;
    InitCtrls.dwSize = sizeof(InitCtrls);
    InitCtrls.dwICC = ICC_WIN95_CLASSES;
    InitCommonControlsEx(&InitCtrls);
    
    CWinApp::InitInstance();

    // Activate "Windows Native" visual manager for enabling themes in MFC controls
    CMFCVisualManager::SetDefaultManager(RUNTIME_CLASS(CMFCVisualManagerWindows));

    CMFCSample dlg;
    m_pMainWnd = &dlg;
    dlg.DoModal();
    
    return FALSE;
}

