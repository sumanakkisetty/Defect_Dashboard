"""
Generates two PNG diagram images:
  diagrams/ui_layout.png      — Visual wireframe of the web dashboard
  diagrams/architecture.png   — System architecture flowchart

Run: python generate_diagrams.py
"""
from PIL import Image, ImageDraw, ImageFont
import pathlib, os

HERE  = pathlib.Path(__file__).parent
OUT   = HERE / "diagrams"
OUT.mkdir(exist_ok=True)

# ── Font helpers ─────────────────────────────────────────────────────────────
def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf"   if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf"     if not bold else "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/verdana.ttf",
    ]
    for p in candidates:
        if pathlib.Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ── Color palette ─────────────────────────────────────────────────────────────
NAVY    = "#1B2631"
PURPLE  = "#7c3aed"
PURPLE2 = "#5B21B6"
DARK    = "#0f1117"
CARD    = "#1a1f2e"
BORDER  = "#2d3748"
TEXT    = "#e2e8f0"
SUB     = "#94a3b8"
WHITE   = "#ffffff"
RED     = "#E53E3E"
ORANGE  = "#DD6B20"
YELLOW  = "#D69E2E"
GREEN   = "#38A169"
CYAN    = "#0BC5EA"
GREY    = "#4A5568"

# helper – rounded rectangle (Pillow < 9.2 compat)
def rrect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = radius
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill,
                           outline=outline, width=width)

def center_text(draw, text, x, y, f, fill, anchor="mm"):
    draw.text((x, y), text, font=f, fill=fill, anchor=anchor)

# ════════════════════════════════════════════════════════════════════════════════
#  1.  UI LAYOUT DIAGRAM
# ════════════════════════════════════════════════════════════════════════════════
W, H = 1200, 1000
img = Image.new("RGB", (W, H), DARK)
d   = ImageDraw.Draw(img)

fB18 = font(18, bold=True)
fB14 = font(14, bold=True)
fB12 = font(12, bold=True)
f11  = font(11)
f10  = font(10)
f9   = font(9)

PAD = 24

# ── outer chrome ─────────────────────────────────────────────────────────────
rrect(d, [PAD, PAD, W-PAD, H-PAD], 12, fill=CARD, outline=BORDER, width=2)

# ── 1. Header bar ────────────────────────────────────────────────────────────
HX0, HY0, HX1, HY1 = PAD, PAD, W-PAD, PAD+70
rrect(d, [HX0, HY0, HX1, HY1], 12, fill=NAVY, outline=PURPLE, width=3)
center_text(d, "App Defect Dashboard", W//2, HY0+24, fB18, WHITE)
center_text(d, "Software Development  |  Defect Tracking & Analytics", W//2, HY0+50, f11, SUB)
# toggle btn
rrect(d, [W-PAD-130, HY0+18, W-PAD-6, HY0+52], 8, fill=CARD, outline=PURPLE, width=2)
center_text(d, "☀  Light Mode", W-PAD-68, HY0+35, f10, TEXT)

# ── 2. Filter bar ────────────────────────────────────────────────────────────
FY0, FY1 = HY1+8, HY1+58
rrect(d, [PAD, FY0, W-PAD, FY1], 8, fill="#13172a", outline=BORDER, width=1)
filters = ["Date Range", "Director", "Priority", "Severity", "Status", "Triage"]
slot_w  = (W - 2*PAD - 12*(len(filters)-1)) // len(filters)
for i, label in enumerate(filters):
    fx0 = PAD + 8 + i*(slot_w+12)
    fx1 = fx0 + slot_w - 4
    rrect(d, [fx0, FY0+8, fx1, FY1-8], 5, fill=CARD, outline=BORDER, width=1)
    center_text(d, label, (fx0+fx1)//2, (FY0+FY1)//2, f10, SUB)

# ── 3. KPI row ───────────────────────────────────────────────────────────────
KY0, KY1 = FY1+8, FY1+90
kpis = [
    ("Total Defects",    "220",  GREY),
    ("Open",             "89",   RED),
    ("S1 Blockers",      "18",   RED),
    ("Critical",         "32",   ORANGE),
    ("In Progress",      "45",   YELLOW),
    ("Resolved / Closed","87",   GREEN),
]
kw = (W - 2*PAD - 10*5) // 6
for i, (label, val, col) in enumerate(kpis):
    kx0 = PAD + 8 + i*(kw+10)
    kx1 = kx0 + kw - 4
    rrect(d, [kx0, KY0, kx1, KY1], 8, fill=col, outline="#ffffff22", width=1)
    center_text(d, val,   (kx0+kx1)//2, KY0+32, fB18, WHITE)
    center_text(d, label, (kx0+kx1)//2, KY1-18, f9,   WHITE)

# ── 4. Chart grid ────────────────────────────────────────────────────────────
CY0 = KY1 + 8
CW2 = (W - 2*PAD - 8) // 2   # half width
ROW_H = 168

charts = [
    # row 0
    [("chart-wow",  "Week-over-Week Trend", "Stacked Bar  |  by Priority", "col-span"),
     ("chart-director", "Defects by Director", "Grouped Bar  |  by Severity", "right")],
    # row 1
    [("chart-triage", "Triage × Status", "Stacked Bar  |  by Team", "left"),
     ("chart-wow-dir","WoW by Director", "Multi-line  |  per Director", "right")],
    # row 2
    [("chart-status",  "Status Breakdown", "Vertical Bar", "left"),
     ("chart-priority","Priority Dist.", "Donut Pie", "mid"),
     ("chart-severity","Severity Dist.", "Donut Pie", "right")],
    # row 3
    [("chart-category","Top Categories", "Horizontal Bar", "left"),
     ("chart-assignee","Top Assignees", "Horizontal Bar  |  Open issues", "right")],
]

cy = CY0
for row in charts:
    if len(row) == 2:
        # two equal columns
        for col_idx, (cid, title, sub, _) in enumerate(row):
            cx0 = PAD + col_idx*(CW2+8)
            cx1 = cx0 + CW2
            rrect(d, [cx0, cy, cx1, cy+ROW_H], 10, fill=CARD, outline=BORDER, width=1)
            # mini chart icon area
            rrect(d, [cx0+10, cy+32, cx1-10, cy+ROW_H-10], 6,
                  fill=DARK, outline=BORDER, width=1)
            # draw tiny placeholder bars / lines
            inner_w = cx1-cx0-20
            inner_h = ROW_H - 42
            ix0, iy0 = cx0+10, cy+32
            if "Bar" in sub:
                bw = inner_w // 10
                for bi in range(8):
                    bh = int(inner_h * (0.3 + 0.5 * ((bi*3+1) % 7) / 6))
                    bx = ix0+8+bi*(bw+4)
                    col_fill = [PURPLE, RED, ORANGE, YELLOW, GREEN, CYAN, PURPLE2, GREY][bi % 8]
                    d.rectangle([bx, iy0+inner_h-bh, bx+bw, iy0+inner_h-2], fill=col_fill)
            elif "line" in sub.lower() or "Line" in sub:
                pts = [(ix0+8+i*22, iy0+inner_h-20 - int(inner_h*0.5*abs((i-4)/4))) for i in range(9)]
                d.line(pts, fill=CYAN, width=2)
                for pt in pts[::2]:
                    d.ellipse([pt[0]-3,pt[1]-3,pt[0]+3,pt[1]+3], fill=CYAN)
            elif "Donut" in sub or "Pie" in sub:
                cx_ = ix0 + inner_w//2
                cy_ = iy0 + inner_h//2
                r   = min(inner_w, inner_h)//2 - 8
                slices = [(90, 130, RED), (130, 220, ORANGE), (220, 310, YELLOW),
                          (310, 360, GREEN), (0, 90, PURPLE)]
                for s, e, col_s in slices:
                    d.pieslice([cx_-r, cy_-r, cx_+r, cy_+r], s, e, fill=col_s)
                d.ellipse([cx_-r//2, cy_-r//2, cx_+r//2, cy_+r//2], fill=DARK)
            # title + subtitle
            center_text(d, title, (cx0+cx1)//2, cy+14, fB12, TEXT)
            center_text(d, sub,   (cx0+cx1)//2, cy+26, f9,  SUB)
    elif len(row) == 3:
        # three columns: left wide, two narrow pies
        left_w  = int(CW2 * 1.05)
        pie_w   = (W - 2*PAD - left_w - 16) // 2
        for col_idx, (cid, title, sub, _) in enumerate(row):
            if col_idx == 0:
                cx0, cx1 = PAD, PAD + left_w
            elif col_idx == 1:
                cx0 = PAD + left_w + 8
                cx1 = cx0 + pie_w
            else:
                cx0 = PAD + left_w + 8 + pie_w + 8
                cx1 = W - PAD
            rrect(d, [cx0, cy, cx1, cy+ROW_H], 10, fill=CARD, outline=BORDER, width=1)
            rrect(d, [cx0+10, cy+32, cx1-10, cy+ROW_H-10], 6,
                  fill=DARK, outline=BORDER, width=1)
            inner_w = cx1-cx0-20
            inner_h = ROW_H - 42
            ix0, iy0 = cx0+10, cy+32
            if "Bar" in sub:
                bw = max(inner_w // 10, 8)
                for bi in range(7):
                    bh = int(inner_h * (0.25 + 0.5 * ((bi*2+3)%7)/6))
                    bx = ix0+6+bi*(bw+4)
                    col_fill = [GREEN, YELLOW, ORANGE, RED, PURPLE, CYAN, GREY][bi%7]
                    d.rectangle([bx, iy0+inner_h-bh, bx+bw, iy0+inner_h-2], fill=col_fill)
            elif "Donut" in sub or "Pie" in sub:
                cx_ = ix0 + inner_w//2
                cy_ = iy0 + inner_h//2
                r   = min(inner_w, inner_h)//2 - 4
                slices = [(90, 180, PURPLE), (180, 290, RED), (290, 360, ORANGE), (0, 90, YELLOW)]
                for s, e, col_s in slices:
                    d.pieslice([cx_-r, cy_-r, cx_+r, cy_+r], s, e, fill=col_s)
                d.ellipse([cx_-r//2, cy_-r//2, cx_+r//2, cy_+r//2], fill=DARK)
            center_text(d, title, (cx0+cx1)//2, cy+14, fB12, TEXT)
            center_text(d, sub,   (cx0+cx1)//2, cy+26, f9,  SUB)
    cy += ROW_H + 8

# ── 5. Defect Table ──────────────────────────────────────────────────────────
TY0 = cy
TY1 = H - PAD - 4
rrect(d, [PAD, TY0, W-PAD, TY1], 10, fill=CARD, outline=BORDER, width=1)
# header row
rrect(d, [PAD, TY0, W-PAD, TY0+28], 10, fill=NAVY, outline=None)
cols_tbl = ["ID","Title","Priority","Severity","Status","Director","Assignee","Release","Updated"]
col_w = (W - 2*PAD - 10) // len(cols_tbl)
for ci, c in enumerate(cols_tbl):
    center_text(d, c, PAD+8+ci*col_w+col_w//2, TY0+14, fB12, WHITE)
# sample rows
row_fills = [DARK, "#1e2535"]
for ri in range(3):
    ry = TY0 + 28 + ri*22
    d.rectangle([PAD+1, ry, W-PAD-1, ry+22], fill=row_fills[ri%2])
    sample = ["DEF-001","Kernel hangs on gfx1100","S1 - Blocker","Critical","Open","Alice","Bob","ROCm 6.3","Feb 28"]
    for ci, v in enumerate(sample[:len(cols_tbl)]):
        cx_ = PAD+8+ci*col_w+col_w//2
        fill_txt = RED if v in ("S1 - Blocker","Critical","Open") else TEXT
        center_text(d, v, cx_, ry+11, f9, fill_txt)
center_text(d, "Defect Log  —  220 records  |  15 rows/page  |  Sortable & Filterable",
            W//2, TY0+14 if TY1-TY0 < 40 else (TY0+TY1)//2 if ri == -1 else TY0+14,
            fB12, WHITE)

img.save(OUT / "ui_layout.png")
print(f"  ui_layout.png  ({(OUT/'ui_layout.png').stat().st_size:,} bytes)")


# ════════════════════════════════════════════════════════════════════════════════
#  2.  ARCHITECTURE DIAGRAM
# ════════════════════════════════════════════════════════════════════════════════
AW, AH = 1200, 820
ai  = Image.new("RGB", (AW, AH), "#0d1117")
ad  = ImageDraw.Draw(ai)

fB16 = font(16, bold=True)
fB13 = font(13, bold=True)
f12  = font(12)
f11b = font(11, bold=True)
f10a = font(10)

# background gradient-feel rectangles
ad.rectangle([0, 0, AW, AH], fill="#0d1117")
for i in range(10):
    ad.rectangle([0, i*AH//10, AW, (i+1)*AH//10],
                 fill=f"#{hex(13+i)[2:].zfill(2)}{hex(17+i)[2:].zfill(2)}{hex(23+i)[2:].zfill(2)}")

# title bar
ad.rectangle([0, 0, AW, 52], fill=NAVY)
ad.rectangle([0, 50, AW, 54], fill=PURPLE)
center_text(ad, "App Defect Dashboard  —  System Architecture", AW//2, 26, fB16, WHITE)

# ── BOX helper ───────────────────────────────────────────────────────────────
def box(x, y, w, h, title, lines=(), color=CARD, border=BORDER, title_bg=NAVY):
    rrect(ad, [x, y, x+w, y+h], 10, fill=color, outline=border, width=2)
    ad.rectangle([x+2, y+2, x+w-2, y+32], fill=title_bg)
    center_text(ad, title, x+w//2, y+17, fB13, WHITE)
    for i, line in enumerate(lines):
        ad.text((x+12, y+38+i*16), line, font=f10a, fill=SUB)

def arrow(x0, y0, x1, y1, label=""):
    """Draw an arrow from (x0,y0) → (x1,y1)."""
    ad.line([(x0, y0), (x1, y1)], fill=PURPLE, width=2)
    # arrowhead
    import math
    angle = math.atan2(y1-y0, x1-x0)
    sz = 10
    for da in (+0.4, -0.4):
        ax = x1 - sz*math.cos(angle-da)
        ay = y1 - sz*math.sin(angle-da)
        ad.line([(x1,y1),(int(ax),int(ay))], fill=PURPLE, width=2)
    if label:
        mx, my = (x0+x1)//2, (y0+y1)//2
        ad.text((mx+4, my-12), label, font=f10a, fill=PURPLE)

def varrow(x, y0, y1, label=""):
    arrow(x, y0, x, y1, label)

def harrow(x0, y, x1, label=""):
    arrow(x0, y, x1, y, label)

# ── Layout coordinates ────────────────────────────────────────────────────────
#
#   [generate_data.py]          (top center)
#          |
#       defects.csv             (center)
#         / \
#   [dashboard.py]   [generate_excel.py]
#        |                   |
#   [Browser]           [.xlsx]
#                           |
#                    [add_excel_theme.py]
#                           |
#                       [.xlsm]
#

# generate_data.py — top center
GDX, GDY, GDW, GDH = 450, 72, 300, 90
box(GDX, GDY, GDW, GDH, "generate_data.py",
    ["• 220 synthetic defect records",
     "• 16 columns, seed=42",
     "• ROCm taxonomy rules"],
    color="#1a2744", border=CYAN, title_bg="#0e2040")

# defects.csv — center
CVX, CVY, CVW, CVH = 450, 230, 300, 70
box(CVX, CVY, CVW, CVH, "defects.csv",
    ["• 220 rows × 16 columns",
     "• Shared data source"],
    color="#1a2744", border=GREEN, title_bg="#0a2a1a")

# arrow: generate_data → defects.csv
varrow(CVX+CVW//2, GDY+GDH, CVY, "writes")

# dashboard.py — left
DBX, DBY, DBW, DBH = 60, 380, 380, 180
box(DBX, DBY, DBW, DBH, "dashboard.py  (Plotly Dash 4.0)",
    ["• Header + theme toggle button",
     "• Date/Director/Priority filters",
     "• 6 KPI metric cards",
     "• 10 interactive Plotly charts",
     "• Director summary table",
     "• Dark / Light theme (dcc.Store)"],
    color=CARD, border=PURPLE, title_bg="#2d1a6b")

# generate_excel.py — right
EXX, EXY, EXW, EXH = 760, 380, 380, 180
box(EXX, EXY, EXW, EXH, "generate_excel.py  (openpyxl)",
    ["• Dashboard sheet (charts + KPIs)",
     "• Summary sheet (pivot tables)",
     "• Defects sheet (220 rows)",
     "• 10 embedded openpyxl charts",
     "• 5 hidden data-source sheets",
     "• Colour-coded cell formatting"],
    color=CARD, border=ORANGE, title_bg="#4a2500")

# arrows: defects.csv → dashboard.py  and  defects.csv → generate_excel.py
# left branch
arrow(CVX, CVY+CVH//2, DBX+DBW, DBY+DBH//2, "reads")
# right branch
arrow(CVX+CVW, CVY+CVH//2, EXX, EXY+EXH//2, "reads")

# Browser — left bottom
BRX, BRY, BRW, BRH = 60, 630, 380, 120
box(BRX, BRY, BRW, BRH, "Browser  —  http://127.0.0.1:8050",
    ["• Live reactive Dash app",
     "• Filters trigger single callback",
     "• All charts update instantly",
     "• Theme toggle: 0.25 s CSS fade"],
    color="#0a1a0a", border=GREEN, title_bg="#0a3a0a")

varrow(DBX+DBW//2, DBY+DBH, BRY, "runs on")

# .xlsx — right bottom
XLSX2X, XLSX2Y, XLSX2W, XLSX2H = 760, 630, 180, 70
box(XLSX2X, XLSX2Y, XLSX2W, XLSX2H, "  .xlsx",
    ["• ROCm_Defect_Dashboard.xlsx"],
    color="#1a1500", border=ORANGE, title_bg="#3a2800")

varrow(EXX+EXW//2, EXY+EXH, XLSX2Y, "writes")

# add_excel_theme.py
ATX, ATY, ATW, ATH = 960, 630, 180, 70
box(ATX, ATY, ATW, ATH, "add_excel_theme.py",
    ["• Injects VBA macro",
     "• Adds toggle button"],
    color=CARD, border=PURPLE, title_bg="#2d1a6b")

harrow(XLSX2X+XLSX2W, XLSX2Y+XLSX2H//2, ATX, "")
ad.text((XLSX2X+XLSX2W+4, XLSX2Y+XLSX2H//2-18), "input", font=f10a, fill=SUB)

# .xlsm — far right bottom
XLSMX, XLSMY, XLSMW, XLSMH = 960, 760, 180, 52
box(XLSMX, XLSMY, XLSMW, XLSMH, "  .xlsm",
    ["ROCm_Defect_Dashboard.xlsm"],
    color="#0a1500", border=GREEN, title_bg="#0a3a0a")

varrow(ATX+ATW//2, ATY+ATH, XLSMY, "saves")

# ── Legend ────────────────────────────────────────────────────────────────────
lx, ly = 40, AH - 90
ad.text((lx, ly), "Legend:", font=fB13, fill=TEXT)
items = [
    (CYAN,   "Data Generator"),
    (GREEN,  "Data / Output file"),
    (PURPLE, "Python application"),
    (ORANGE, "Excel artifact"),
]
for i, (col, label) in enumerate(items):
    sx = lx + i*190
    ad.rounded_rectangle([sx, ly+22, sx+14, ly+36], radius=3, fill=col)
    ad.text((sx+20, ly+22), label, font=f10a, fill=SUB)

ai.save(OUT / "architecture.png")
print(f"  architecture.png  ({(OUT/'architecture.png').stat().st_size:,} bytes)")
print("\nDiagrams saved to:", OUT)
