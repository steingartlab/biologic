
// MFCSampleDlg.h : header file
//

#pragma once

#include <BLFunctions.h>
#include "afxwin.h"
#include "afxcmn.h"

typedef enum {
    XREC_CE   = (1 << 0),
    XREC_AUX1 = (1 << 1),
    XREC_AUX2 = (1 << 2),
    // << 3 reserved
    // << 4 reserved
    XREC_CTL  = (1 << 5),
    XREC_Q    = (1 << 6),
    XREC_IRG  = (1 << 7)
} TExtraRecord_e;


class CMFCSample : public CDialogEx
{
public:
    CMFCSample(CWnd* pParent = NULL);	// standard constructor
    ~CMFCSample();

    enum { IDD = IDD_MFCSAMPLE_DIALOG };

protected:
    virtual void DoDataExchange(CDataExchange* pDX);

protected:

    // thread tasks
    static UINT populateData( PVOID data );
    static UINT getBLMessages( PVOID data );

    void DisplayPopup( const CString &message, BOOL fatal = false);
    void DisplayPopupDisconnect( CString message, int err = ERR_NOERROR );

    void setupChannels();
    void log( PCTSTR message, ... );
    BYTE getCurrentChannel();
    HANDLE createThread( AFX_THREADPROC procedure, bool &stop, uint8 channel );
    void tearDownThread( HANDLE &handle, bool &stop );
    void setupDataList( const CString &technique, bool vmp4, int xrec );
    int  getXrec();

    int insertChronoData( const TDataBuffer_t& dbuf, const TDataInfos_t& inf, const TCurrentValues_t& curr );
    int insertOCVData( const TDataBuffer_t& dbuf, const TDataInfos_t& inf, const TCurrentValues_t& curr );

    // don't handle Dialog controls
    void OnOk() {}; 
    void OnCancel() {};

    // Generated message map functions
    virtual BOOL OnInitDialog();
    afx_msg LRESULT OnUpdateData(WPARAM wp, LPARAM lp);
    afx_msg LRESULT OnPopulateFinished(WPARAM wp, LPARAM lp);
    afx_msg LRESULT OnVMPMessage( WPARAM, LPARAM );

    DECLARE_MESSAGE_MAP()


    // ECLib data
    TDeviceInfos_t      infos;
    INT32               conn_id;
    bool                stop_acq;
    bool                stop_messages;

    HANDLE              msg_thread_handle;
    HANDLE              data_thread_handle;

public:
    // Resources
    afx_msg void OnQuitClicked();
    afx_msg void OnConnectClicked();
    afx_msg void OnInfoClicked();
    afx_msg void OnDisconnectClicked();
    afx_msg void OnChanInfoClicked();
    afx_msg void OnChanCurrentValueClicked();
    afx_msg void OnStartClicked();
    afx_msg void OnStopClicked();
    afx_msg void OnBnClickedButtonCopy();
    CButton     connect_btn;
    CButton     disconnect_btn;
    CButton     start_btn;
    CButton     stop_btn;
    CButton     quit_btn;
    CButton     info_btn;
    CComboBox   channel_list;
    CComboBox   techniques_list;
    CStatic     conn_status;
    CStatic     started_status;
    CEdit       ip_address;
    CEdit       logmsg;
    CEdit       point_count;
    CButton     firmware_checkbox;
    afx_msg void OnChannelSelectionChanged();
    CListCtrl   list_ctrl;
    CButton show_params;
    CButton xrec_ce;
    CButton xrec_aux1;
    CButton xrec_aux2;
    CButton xrec_q;
    CButton xrec_irange;
    CButton xrec_ctrl;
};
