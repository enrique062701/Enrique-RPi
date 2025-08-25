object OptionsForm: TOptionsForm
  Left = 329
  Top = 235
  BorderStyle = bsDialog
  Caption = 'Options'
  ClientHeight = 188
  ClientWidth = 262
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -13
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  KeyPreview = True
  OldCreateOrder = False
  Position = poMainFormCenter
  Scaled = False
  OnClose = FormClose
  OnCreate = FormCreate
  OnKeyDown = FormKeyDown
  PixelsPerInch = 120
  TextHeight = 16
  object PortRG: TRadioGroup
    Left = 24
    Top = 24
    Width = 185
    Height = 113
    Caption = 'Communications port'
    Items.Strings = (
      'USB'
      'COM')
    TabOrder = 0
  end
  object COMNoEdit: TEdit
    Left = 88
    Top = 96
    Width = 57
    Height = 25
    TabOrder = 1
    Text = '1'
  end
  object COMUpDown: TUpDown
    Left = 145
    Top = 96
    Width = 20
    Height = 25
    Associate = COMNoEdit
    Min = 1
    Position = 1
    TabOrder = 2
    Wrap = False
  end
end
