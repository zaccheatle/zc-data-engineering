'Project Summary
    '1.) This code will convert the BB FBI Template into the gl transactions template.
    '2.) SHORTKEYS:
        'alt F11 to open VBA editor
        'F8 to run code line by line
        'F5 to run entire code

Public Sub import_FBI_data()


Dim FileToOpen As Variant
Dim OpenBook As Workbook

Dim wsSource As Worksheet
Dim wsDest As Worksheet

Dim i As Long
Dim j As Long
Dim lastrow1 As Long
Dim MY_LAST_ROW As Long


On Error Resume Next
    
    Application.ScreenUpdating = False
    
    'Pop up to allow user to select which file they want to use as the source
    FileToOpen = Application.GetOpenFilename(Title:="Browse for your File & Import Range", FileFilter:="Excel Files (*.xls*),*xls*")
    If FileToOpen <> False Then
        'Set variables for the source and destination workbooks.worksheets
        Set OpenBook = Application.Workbooks.Open(FileToOpen)
        Set wsSource = OpenBook.Worksheets("Template")
        Set wsDest = ThisWorkbook.Worksheets("gl_transactions")
        
        'Clear contents of destination range
        wsDest.Range("A2:A10000").EntireRow.ClearContents
        
        'Identify last row and column of the source workbook and starting point for the loop
        lastrow1 = wsSource.Cells(Rows.Count, 1).End(xlUp).Offset(-3, 0).Row
        lastcol = wsSource.Cells(5, Columns.Count).End(xlToLeft).Offset(0, -1).Column
            
        'Loop through every row and column starting in row 6 column D and copy over any data that isn't blank with the associated values
        For i = 6 To lastrow1 Step 1
            For j = 4 To lastcol Step 1
                If Not IsEmpty(Cells(i, j)) Then
                'Skip cell if it is = 0 or begins with a space
                    If Cells(i, j) <> 0# And Not Cells(i, j) Like " *" Then
                        amount = wsSource.Cells(i, j).Value
                        fund_code = wsSource.Cells(i, 2).Value
                        account_num = wsSource.Cells(4, j).Value
                        post_code = wsSource.Cells(3, 1).Value
                        Description = wsSource.Cells(5, j).Value
                    
                        'Identify last row of destination workbook
                        MY_LAST_ROW = wsDest.Cells(Rows.Count, 1).End(xlUp).Offset(1, 0).Row
                    
                        'Identify where FBI data will copy to in destination workbook
                        With wsDest
                            wsDest.Cells(MY_LAST_ROW, 4).Value = amount
                            wsDest.Cells(MY_LAST_ROW, 2).Value = fund_code
                            wsDest.Cells(MY_LAST_ROW, 3).Value = account_num
                            wsDest.Cells(MY_LAST_ROW, 1).Value = post_code
                            wsDest.Cells(MY_LAST_ROW, 5).Value = Description
                        End With
                    End If
                End If
            Next j
        Next i
        
        'Display a message indicating successful import
        MsgBox "Import successful"
        
    Else
        'Display a message indicating no file was selected
        MsgBox "No file was selected"
    End If
    
    If Not OpenBook Is Nothing Then
        OpenBook.Close False
    End If
    
    Application.ScreenUpdating = True
    
    On Error GoTo 0
    
End Sub
