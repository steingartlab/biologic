object fVMPadddevice: TfVMPadddevice
  Left = 272
  Top = 204
  BorderStyle = bsDialog
  Caption = 'New Device'
  ClientHeight = 270
  ClientWidth = 347
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  KeyPreview = True
  OldCreateOrder = False
  Position = poScreenCenter
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object PanelDevice: TPanel
    Left = -10
    Top = 8
    Width = 558
    Height = 258
    BevelOuter = bvNone
    Ctl3D = True
    Font.Charset = DEFAULT_CHARSET
    Font.Color = clWindowText
    Font.Height = -12
    Font.Name = 'MS Sans Serif'
    Font.Style = []
    ParentColor = True
    ParentCtl3D = False
    ParentFont = False
    TabOrder = 0
    DesignSize = (
      558
      258)
    object GroupBox5: TGroupBox
      Left = 27
      Top = 0
      Width = 302
      Height = 182
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clBlack
      Font.Height = -12
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ParentFont = False
      TabOrder = 0
      object btnRefresh: TSpeedButton
        Left = 205
        Top = 155
        Width = 60
        Height = 22
        Caption = 'Refresh'
        Font.Charset = DEFAULT_CHARSET
        Font.Color = clBlack
        Font.Height = -12
        Font.Name = 'MS Sans Serif'
        Font.Style = []
        ParentFont = False
        Transparent = False
        OnClick = btnRefreshClick
      end
      object lblOnLine: TLabel
        Left = 29
        Top = 17
        Width = 39
        Height = 13
        Caption = 'On-line :'
      end
      object StringGridDevices: TStringGrid
        Left = 29
        Top = 38
        Width = 252
        Height = 115
        ColCount = 2
        DefaultRowHeight = 16
        FixedCols = 0
        RowCount = 2
        GridLineWidth = 0
        Options = [goFixedVertLine, goFixedHorzLine, goVertLine, goHorzLine, goRowSelect]
        TabOrder = 0
        ColWidths = (
          100
          119)
      end
    end
    object btnSelectDevice: TBitBtn
      Left = 106
      Top = 219
      Width = 75
      Height = 25
      Anchors = [akTop, akRight]
      Caption = 'Select'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ModalResult = 1
      ParentFont = False
      TabOrder = 1
      OnClick = btnSelectDeviceClick
    end
    object btnClose: TBitBtn
      Left = 187
      Top = 219
      Width = 75
      Height = 25
      Anchors = [akTop, akRight]
      Caption = 'Cancel'
      Default = True
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Height = -12
      Font.Name = 'MS Sans Serif'
      Font.Style = []
      ModalResult = 2
      ParentFont = False
      TabOrder = 2
    end
  end
end
