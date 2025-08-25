Module Module1

    Sub Main()
        Dim rc = New RC()                       ' RC class instance
        Dim success As Boolean                  ' return code

        Dim devs As List(Of String) = Nothing   ' list of devices
        Dim regs As List(Of String) = Nothing   ' list of device register
        Dim values As List(Of String) = Nothing ' list of allowed device values

        Dim strng As String = ""
        Dim dbl As Double
        Dim timestamp As Integer

        ' without initial Connect() call all other functions will return non OK ErrorCode
        '  Connect() arguments: connection type, "USB HW S/N" / "COM port name" / "TCP IP / host", "path to REMOTECONTROL.CSV file"
        ' success = rc.Connect(rc.ConnectionType.usb, "", "")

        ' paste VB code here

    End Sub

End Module
