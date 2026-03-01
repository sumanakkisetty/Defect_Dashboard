"""
Adds Dark / Light theme toggle button + VBA macro to App_Defect_Dashboard.xlsx
Saves the result as App_Defect_Dashboard.xlsm

Run AFTER generate_excel.py:
    python add_excel_theme.py
"""

import win32com.client as win32
import os, time

XLSX = os.path.abspath("App_Defect_Dashboard.xlsx")
XLSM = os.path.abspath("App_Defect_Dashboard.xlsm")

VBA_CODE = r'''
Option Explicit
Dim gTheme As String   ' "dark" (default) or "light"

' ─────────────────────────────────────────────────────────────────────
'  Entry point — called by the toggle button
' ─────────────────────────────────────────────────────────────────────
Sub ToggleTheme()
    If gTheme = "" Then gTheme = "dark"
    If gTheme = "dark" Then
        gTheme = "light"
        Call ApplyLightTheme
    Else
        gTheme = "dark"
        Call ApplyDarkTheme
    End If
End Sub

' ─────────────────────────────────────────────────────────────────────
'  DARK THEME
' ─────────────────────────────────────────────────────────────────────
Sub ApplyDarkTheme()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Dashboard")
    Application.ScreenUpdating = False

    ' ── Page base background ──────────────────────────────────────────
    ws.Cells.Interior.Color = RGB(15, 17, 23)       ' #0f1117

    ' ── Banner rows 1-5  (keep navy in both themes) ──────────────────
    Dim r As Long, c As Long
    For r = 1 To 5
        For c = 2 To 15
            ws.Cells(r, c).Interior.Color = RGB(27, 38, 59)
            ws.Cells(r, c).Font.Color     = RGB(255, 255, 255)
        Next c
    Next r
    ws.Range("B2:O2").Font.Color = RGB(255, 255, 255)

    ' ── KPI cards rows 6-9 cols B-G  (semantic colors stay) ─────────
    ' keep their existing fill — just fix font white
    Dim kpiCols As Variant
    kpiCols = Array("B","C","D","E","F","G")
    Dim col As Variant
    For Each col In kpiCols
        For r = 6 To 9
            ws.Range(col & r).Font.Color = RGB(255, 255, 255)
        Next r
    Next col

    ' ── Director Summary table rows 11-18 ────────────────────────────
    ws.Range("B11:G11").Interior.Color = RGB(46, 64, 87)
    ws.Range("B11:G11").Font.Color     = RGB(255, 255, 255)
    ws.Range("B12:G12").Interior.Color = RGB(44, 52, 80)
    ws.Range("B12:G12").Font.Color     = RGB(255, 255, 255)
    For r = 13 To 18
        If r Mod 2 = 0 Then
            ws.Range("B" & r & ":G" & r).Interior.Color = RGB(21, 25, 41)
        Else
            ws.Range("B" & r & ":G" & r).Interior.Color = RGB(26, 31, 46)
        End If
        ws.Range("B" & r & ":G" & r).Font.Color = RGB(226, 232, 240)
    Next r
    ' Director name cells keep their colour-coded font

    ' ── Charts ───────────────────────────────────────────────────────
    Dim cht As ChartObject
    For Each cht In ws.ChartObjects
        With cht.Chart
            .ChartArea.Interior.Color      = RGB(26, 31, 46)
            .ChartArea.Border.Color        = RGB(45, 55, 72)
            .ChartArea.Font.Color          = RGB(226, 232, 240)
            .PlotArea.Interior.Color       = RGB(26, 31, 46)
            .PlotArea.Border.Color         = RGB(45, 55, 72)
            On Error Resume Next
            .Axes(xlValue).TickLabels.Font.Color = RGB(226, 232, 240)
            .Axes(xlCategory).TickLabels.Font.Color = RGB(226, 232, 240)
            .Legend.Font.Color = RGB(226, 232, 240)
            On Error GoTo 0
        End With
    Next cht

    ' ── Toggle button ─────────────────────────────────────────────────
    With ws.Shapes("ThemeToggleBtn")
        .Fill.ForeColor.RGB                             = RGB(26, 31, 46)
        .Line.ForeColor.RGB                             = RGB(124, 58, 237)
        .TextFrame2.TextRange.Font.Fill.ForeColor.RGB   = RGB(226, 232, 240)
        .TextFrame2.TextRange.Characters.Text           = Chr(9728) & "  Light Mode"
    End With

    Application.ScreenUpdating = True
End Sub

' ─────────────────────────────────────────────────────────────────────
'  LIGHT THEME
' ─────────────────────────────────────────────────────────────────────
Sub ApplyLightTheme()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("Dashboard")
    Application.ScreenUpdating = False

    ' ── Page base background ──────────────────────────────────────────
    ws.Cells.Interior.Color = RGB(240, 244, 248)    ' #F0F4F8

    ' ── Banner rows 1-5 (keep navy) ──────────────────────────────────
    Dim r As Long, c As Long
    For r = 1 To 5
        For c = 2 To 15
            ws.Cells(r, c).Interior.Color = RGB(27, 38, 59)
            ws.Cells(r, c).Font.Color     = RGB(255, 255, 255)
        Next c
    Next r

    ' ── KPI cards — font white (works on coloured backgrounds) ───────
    Dim kpiCols As Variant
    kpiCols = Array("B","C","D","E","F","G")
    Dim col As Variant
    For Each col In kpiCols
        For r = 6 To 9
            ws.Range(col & r).Font.Color = RGB(255, 255, 255)
        Next r
    Next col

    ' ── Director Summary table rows 11-18 ────────────────────────────
    ws.Range("B11:G11").Interior.Color = RGB(46, 64, 87)
    ws.Range("B11:G11").Font.Color     = RGB(255, 255, 255)
    ws.Range("B12:G12").Interior.Color = RGB(74, 85, 104)
    ws.Range("B12:G12").Font.Color     = RGB(255, 255, 255)
    For r = 13 To 18
        If r Mod 2 = 0 Then
            ws.Range("B" & r & ":G" & r).Interior.Color = RGB(247, 250, 252)
        Else
            ws.Range("B" & r & ":G" & r).Interior.Color = RGB(255, 255, 255)
        End If
        ws.Range("B" & r & ":G" & r).Font.Color = RGB(26, 32, 44)
    Next r

    ' ── Charts ───────────────────────────────────────────────────────
    Dim cht As ChartObject
    For Each cht In ws.ChartObjects
        With cht.Chart
            .ChartArea.Interior.Color      = RGB(255, 255, 255)
            .ChartArea.Border.Color        = RGB(203, 213, 224)
            .ChartArea.Font.Color          = RGB(26, 32, 44)
            .PlotArea.Interior.Color       = RGB(255, 255, 255)
            .PlotArea.Border.Color         = RGB(203, 213, 224)
            On Error Resume Next
            .Axes(xlValue).TickLabels.Font.Color   = RGB(26, 32, 44)
            .Axes(xlCategory).TickLabels.Font.Color = RGB(26, 32, 44)
            .Legend.Font.Color = RGB(26, 32, 44)
            On Error GoTo 0
        End With
    Next cht

    ' ── Toggle button ─────────────────────────────────────────────────
    With ws.Shapes("ThemeToggleBtn")
        .Fill.ForeColor.RGB                             = RGB(255, 255, 255)
        .Line.ForeColor.RGB                             = RGB(91, 33, 182)
        .TextFrame2.TextRange.Font.Fill.ForeColor.RGB   = RGB(26, 32, 44)
        .TextFrame2.TextRange.Characters.Text           = Chr(9790) & "  Dark Mode"
    End With

    Application.ScreenUpdating = True
End Sub
'''

print("Opening Excel...")
xl  = win32.Dispatch("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

wb  = xl.Workbooks.Open(XLSX)
wsd = wb.Sheets("Dashboard")

# ── Inject VBA module ──────────────────────────────────────────────────────────
vba_proj  = wb.VBProject
vba_comps = vba_proj.VBComponents
mod = vba_comps.Add(1)   # 1 = vbext_ct_StdModule
mod.Name = "ThemeModule"
mod.CodeModule.AddFromString(VBA_CODE)
print("  VBA module injected.")

# ── Add toggle button shape to Dashboard ──────────────────────────────────────
# Position: top-right area of dashboard, around cols I-J row 2-3
# Excel uses Points (1 pt = 1/72 inch). Approximate pixel positions.
# We want it roughly at col I (x≈550), row 2 (y≈30), size 130x28

# Get position from col I row 2
rng = wsd.Range("I2:J3")
left   = rng.Left   + 4
top    = rng.Top    + 4
width  = 135
height = 24

btn = wsd.Shapes.AddShape(
    1,          # msoShapeRoundedRectangle
    left, top, width, height
)
btn.Name = "ThemeToggleBtn"

# Style the button
btn.Fill.ForeColor.RGB              = 0x1a1f2e  # dark bg (BGR order in win32)
btn.Line.ForeColor.RGB              = 0x7c3aed
btn.Line.Weight                     = 1.5

tf = btn.TextFrame2
tf.TextRange.Characters.Text        = "\u2600  Light Mode"
tf.TextRange.Font.Size              = 10
tf.TextRange.Font.Bold              = True
tf.TextRange.Font.Fill.ForeColor.RGB = 0xe2e8f0
tf.MarginLeft  = 8
tf.MarginRight = 8
tf.VerticalAnchor = 3   # msoAnchorMiddle

btn.OnAction = "ThemeModule.ToggleTheme"

print("  Toggle button added.")

# ── Save as .xlsm ─────────────────────────────────────────────────────────────
if os.path.exists(XLSM):
    os.remove(XLSM)

wb.SaveAs(XLSM, FileFormat=52)   # 52 = xlOpenXMLWorkbookMacroEnabled
wb.Close(False)
xl.Quit()

print(f"\nSaved: {XLSM}")
print("  Click 'Light Mode' button on the Dashboard sheet to toggle theme.")
print("  Note: Enable macros when Excel prompts on first open.")
