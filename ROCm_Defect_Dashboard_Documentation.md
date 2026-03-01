# App Defect Dashboard — Project Documentation

**Version:** 1.1
**Last Updated:** 28 Feb 2026
**Domain:** Software Development | Defect Tracking & Analytics

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Data Model](#4-data-model)
5. [App Taxonomy & Classification](#5-app-taxonomy--classification)
6. [Organizational Hierarchy](#6-organizational-hierarchy)
7. [Web Dashboard (dashboard.py)](#7-web-dashboard-dashboardpy)
8. [Excel Dashboard (generate_excel.py)](#8-excel-dashboard-generate_excelpy)
9. [Data Generator (generate_data.py)](#9-data-generator-generate_datapy)
10. [Installation & Setup](#10-installation--setup)
11. [Running the Project](#11-running-the-project)
12. [Dashboard Features Reference](#12-dashboard-features-reference)
13. [Color Coding Reference](#13-color-coding-reference)
14. [Dark / Light Theme Toggle](#14-dark--light-theme-toggle)
15. [System Architecture](#15-system-architecture)
16. [Excel Dashboard Screenshots](#16-excel-dashboard-screenshots)

---

## 1. Project Overview

The **App Defect Dashboard** is an internal analytics tool for tracking, visualizing, and analyzing software defects across your application platform. It provides two complementary output formats:

| Output | Tool | Audience |
|--------|------|----------|
| **Interactive Web Dashboard** | `dashboard.py` | Engineering teams, daily standups, real-time filtering |
| **Excel Dashboard** | `generate_excel.py` | Management reports, offline sharing, Confluence attachments |

The dashboard ingests defect data from a CSV file (`defects.csv`) and renders KPI cards, trend charts, distribution charts, and a full searchable defect log — all filterable by date range, director, priority, severity, status, and triage assignment.

### Key Capabilities

- **6 KPI cards** showing real-time totals: Total, Open, S1 Blockers, Critical (P1), In Progress, Resolved/Closed
- **9 interactive charts** covering week-on-week trends, director ownership, triage assignments, severity/priority distributions, status breakdown, top assignees, and release targeting
- **Full defect table** with native sort, filter, and pagination
- **Cross-filters** — every dropdown/date picker updates all charts and the table simultaneously
- **Excel export** with embedded charts, a director summary table, pivot sheets, and a color-coded data sheet

---

## 2. Technology Stack

| Layer | Library / Tool | Version |
|-------|---------------|---------|
| Web Framework | [Plotly Dash](https://dash.plotly.com/) | ≥ 2.14.0 |
| Charting | Plotly Express | ≥ 5.18.0 |
| Data Manipulation | Pandas | ≥ 2.0.0 |
| Numerical Utilities | NumPy | ≥ 1.24.0 |
| Excel Generation | openpyxl | ≥ 3.1.0 |
| Runtime | Python | 3.9+ |

All dependencies are declared in `requirements.txt`.

---

## 3. Project Structure

```
Defect_Dashboard/
│
├── dashboard.py            # Interactive web dashboard (Plotly Dash)
├── generate_excel.py       # Excel dashboard generator (openpyxl)
├── generate_data.py        # Synthetic defect data generator
│
├── defects.csv             # Defect dataset (220 records, 26-week span)
├── ROCm_Defect_Dashboard.xlsx  # Pre-generated Excel dashboard
│
├── requirements.txt        # Python dependencies
│
└── *.png                   # Dashboard screenshots
```

### File Descriptions

| File | Purpose |
|------|---------|
| `dashboard.py` | Main Dash application. Loads `defects.csv`, defines UI layout, and implements a single reactive callback that updates all 9 charts + KPIs + table on filter change. |
| `generate_excel.py` | Reads `defects.csv` and writes a multi-sheet `.xlsx` file with an auto-sizing dashboard sheet, charts, a color-coded data sheet, and summary pivot tables. |
| `generate_data.py` | Produces 220 synthetic, realistic defect records spanning the last 26 weeks. Used for demo/testing. Run once to regenerate `defects.csv`. |
| `defects.csv` | The primary data source consumed by both the dashboard and the Excel generator. |
| `ROCm_Defect_Dashboard.xlsx` | The pre-built Excel output. Can be opened in Excel without Python installed. |

---

## 4. Data Model

`defects.csv` contains **220 defect records** across **16 columns**:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Defect_ID` | String | Unique identifier | `ROCm-1001` |
| `Title` | String | Short description of the defect | `HIP Runtime: Crash observed on MI300X when calling hipMalloc` |
| `Created_Date` | Date (`YYYY-MM-DD`) | Date the defect was filed | `2025-09-15` |
| `Created_By` | String | Team member who filed it | `Priya Sharma` |
| `Priority` | Enum | Business priority | `Critical`, `High`, `Medium`, `Low` |
| `Severity` | Enum | Technical impact | `S1 - Blocker`, `S2 - Critical`, `S3 - Major`, `S4 - Minor` |
| `Status` | Enum | Current workflow state | `Open`, `In Progress`, `In Review`, `Resolved`, `Closed`, `Won't Fix` |
| `Triage_Category` | String | Technical area of the defect | `HIP Runtime`, `ROCBlas / Math Libraries`, etc. |
| `Triage_Assignment` | String | Engineering team responsible | `Runtime Team`, `Compiler Team`, etc. |
| `Director` | String | Director who owns the team | `SAM`, `Kumar`, `Philips`, `Suma`, `Ravi` |
| `Assignee` | String | Individual working the defect | `Marcus Johnson` (empty if unassigned/Open) |
| `Component` | String | Derived short component name | `HIP Runtime`, `Compiler`, etc. |
| `Target_Release` | String | Target fix release | `ROCm 6.3`, `ROCm 7.0`, `Backlog` |
| `Found_In_Release` | String | Release where defect was found | `ROCm 6.1`, `ROCm 6.2`, `ROCm 6.3` |
| `Last_Updated_Date` | Date (`YYYY-MM-DD`) | Most recent update timestamp | `2025-11-02` |
| `Resolution` | String | Closure reason (empty if open) | `Fixed`, `Won't Fix`, `Duplicate`, `Cannot Reproduce`, `By Design` |

### Priority–Severity Mapping

The data enforces a logical relationship between priority and severity:

| Priority | Allowed Severities |
|----------|--------------------|
| Critical | S1 - Blocker, S2 - Critical |
| High | S2 - Critical, S3 - Major |
| Medium | S3 - Major, S4 - Minor |
| Low | S4 - Minor |

### Status–Assignee Rule

- Defects with status **Open** have no assignee (empty `Assignee` field).
- All other statuses (`In Progress`, `In Review`, `Resolved`, `Closed`, `Won't Fix`) have an assigned team member.

---

## 5. App Taxonomy & Classification

### Triage Categories (Technical Areas)

| Triage Category | Engineering Team |
|-----------------|-----------------|
| HIP Runtime | Runtime Team |
| ROCBlas / Math Libraries | Math Libraries Team |
| Compiler (rocm-llvm / HIP-Clang) | Compiler Team |
| ROCm-SMI / Monitoring | Tools & Infra Team |
| ROCm Installer / Packaging | Release Engineering |
| MIOpen | Math Libraries Team |
| RCCL (Comms) | Runtime Team |
| rocSPARSE | Math Libraries Team |
| rocFFT | Math Libraries Team |
| Documentation | Documentation Team |
| Performance / Profiling | Tools & Infra Team |
| ROCm Debugger (ROCgdb) | Tools & Infra Team |
| Driver / KFD | Driver Team |

### Priority Distribution (Weighted)

| Priority | Weight (%) | Approximate Share |
|----------|-----------|-------------------|
| Low | 25% | ~55 defects |
| Medium | 45% | ~99 defects |
| High | 22% | ~48 defects |
| Critical | 8% | ~18 defects |

### Status Distribution (Weighted)

| Status | Weight (%) | Approximate Count |
|--------|-----------|-------------------|
| Open | 28% | ~62 |
| In Progress | 22% | ~48 |
| Resolved | 22% | ~48 |
| Closed | 12% | ~26 |
| In Review | 10% | ~22 |
| Won't Fix | 6% | ~13 |

---

## 6. Organizational Hierarchy

The dashboard tracks defect ownership at the Director level, with each director owning one or more engineering teams:

| Director | Teams Owned | Dashboard Color |
|----------|------------|----------------|
| **SAM** | Driver Team, Compiler Team, Runtime Team | Purple `#7c3aed` |
| **Kumar** | Math Libraries Team | Cyan `#06b6d4` |
| **Philips** | Tools & Infra Team | Emerald `#10b981` |
| **Suma** | Release Engineering | Amber `#f59e0b` |
| **Ravi** | Documentation Team | Pink `#ec4899` |

### Team Members (15 total)

Alex Chen, Priya Sharma, Marcus Johnson, Aisha Patel, David Kim, Rania Hassan, Tyler Brooks, Mei Liu, Carlos Rivera, Fatima Al-Zahra, Jake Thompson, Yuki Tanaka, Suman Dey, Ivan Petrov, Leila Nouri

---

## 7. Web Dashboard (`dashboard.py`)

### How to Launch

```bash
python dashboard.py
# Then open: http://127.0.0.1:8050
```

### UI Layout

![Dashboard UI Layout — Visual Wireframe](ui_layout.png)

*The dashboard is a dark-themed single-page application. From top to bottom: navy header with theme toggle, filter bar (6 dropdowns), 6 colour-coded KPI cards, a 2-column chart grid (4 rows, 10 charts total), and a paginated defect data table.*

### Filter Controls

| Filter | Component | Behavior |
|--------|-----------|----------|
| Date Range | `DatePickerRange` | Filters by `Created_Date`; defaults to full dataset range |
| Director | Multi-select Dropdown | Filters by `Director` field |
| Priority | Multi-select Dropdown | Filters by `Priority` field |
| Severity | Multi-select Dropdown | Filters by `Severity` field |
| Status | Multi-select Dropdown | Filters by `Status` field |
| Triage Assignment | Multi-select Dropdown | Filters by `Triage_Assignment` (team) |

All filters are **AND-combined** — selecting multiple values within a filter uses OR logic; values across different filters use AND logic.

### KPI Cards

| KPI | Color | Condition |
|-----|-------|-----------|
| Total Defects | White | All records in filtered set |
| Open | Red | `Status == "Open"` |
| S1 Blockers | Red | `Severity == "S1 - Blocker"` |
| Critical Priority | Orange | `Priority == "Critical"` |
| In Progress | Yellow | `Status == "In Progress"` |
| Resolved / Closed | Green | `Status in ["Resolved", "Closed"]` |

### Charts

| Chart ID | Chart Type | X-Axis | Color Dimension | Description |
|----------|-----------|--------|-----------------|-------------|
| `chart-wow` | Stacked Bar | Week Label | Priority | Weekly defect creation trend by priority |
| `chart-director` | Horizontal Bar | Count | Severity | Defect count per director, split by severity |
| `chart-triage` | Horizontal Bar | Count | Status | Defect count per team, split by status |
| `chart-priority` | Donut Pie | — | Priority | Priority distribution |
| `chart-severity` | Donut Pie | — | Severity | Severity distribution |
| `chart-category` | Horizontal Bar | Count | — (purple) | Defects by triage category |
| `chart-status` | Vertical Bar | Status | Status | Status breakdown |
| `chart-assignee` | Horizontal Bar | Open Issues | — (purple) | Top 10 assignees with open issues |
| `chart-wow-director` | Line + Markers | Week Label | Director | Weekly trend per director |
| `chart-release` | Vertical Bar | Release | — (cyan) | Distribution of target releases |

### Reactive Callback

The application uses a **single Dash callback** (`update_all`) that:
1. Receives 7 filter inputs (date range + 5 dropdowns)
2. Applies all filters via `apply_filters()`
3. Computes all KPIs, table data, and 9 chart figures
4. Returns 13 outputs simultaneously

This ensures all visual elements stay perfectly synchronized on every filter change.

### Visual Theme

| Token | Value | Usage |
|-------|-------|-------|
| `BG` | `#0f1117` | Page background |
| `CARD` | `#1a1f2e` | Card/chart backgrounds |
| `BORDER` | `#2d3748` | Card borders, grid lines |
| `TEXT` | `#e2e8f0` | Primary text |
| `SUBTEXT` | `#94a3b8` | Labels, secondary text |
| `ACCENT` | `#7c3aed` | Header accent, highlight bars |

---

## 8. Excel Dashboard (`generate_excel.py`)

### How to Generate

```bash
python generate_excel.py
# Output: ROCm_Defect_Dashboard.xlsx
```

The Excel file requires **no Python to view** — it opens directly in Microsoft Excel.

### Workbook Structure

| Sheet | Visibility | Content |
|-------|-----------|---------|
| `Dashboard` | Visible | KPI cards, Director Summary table, 9 embedded charts |
| `Defects` | Visible | Full color-coded defect log (220 rows, 16 columns, auto-filter) |
| `Summary` | Visible | Pivot tables: Priority, Severity, Status, Director breakdown, 8-week trend |
| `_WoW` | Hidden | Week-on-Week data by Priority (chart source) |
| `_Dir` | Hidden | Director × Severity data (chart source) |
| `_Triage` | Hidden | Triage Assignment × Status data (chart source) |
| `_WDir` | Hidden | Week-on-Week data by Director (chart source) |
| `_Counts` | Hidden | Priority, Severity, Status, Category, Assignee, Release counts (chart sources) |

### Dashboard Sheet Layout

**Rows 1–5:** Navy banner with title "ROCm Defect Dashboard" and generation date
**Rows 6–9:** 6 KPI cards (columns B–G), color-coded by metric type
**Rows 11–18:** Director Summary Table (Director, Teams, Total, Open, Critical, Resolved)
**Row 19:** Spacer
**Rows 20+:** Embedded charts in a 2-column layout

### Embedded Charts

| Chart | Type | Position | Description |
|-------|------|----------|-------------|
| WoW by Priority | Stacked Column | B20 | Weekly issues by priority |
| Director by Severity | Stacked Bar (horizontal) | I20 | Director defect load by severity |
| Triage by Status | Stacked Bar (horizontal) | B40 | Team workload by status |
| Priority Distribution | Pie | I40 | Priority share |
| Severity Distribution | Pie | L40 | Severity share |
| WoW by Director | Line | B60 | Director trend over time |
| Status Breakdown | Column | I60 | Issues per status |
| Top Triage Categories | Bar (horizontal) | B76 | Most defect-prone components |
| Top Assignees | Bar (horizontal) | I76 | Engineers with most open issues |

### Defects Sheet

- **Freeze panes** at row 2 (header stays visible while scrolling)
- **Auto-filter** enabled on all 16 columns
- **Conditional color fills** per cell:
  - Priority column: red → orange → yellow → green gradient
  - Severity column: same gradient
  - Status column: red (Open), orange (In Progress), yellow (In Review), green (Resolved), gray (Closed), purple (Won't Fix)
  - Director column: color-coded by director identity
- Alternating row backgrounds (white / light gray)

### Summary Sheet

Contains static pivot tables (no Python required to read):

| Table | Location | Columns |
|-------|----------|---------|
| Issues by Priority | Row 1, Col 1 | Priority, Count |
| Issues by Severity | Row 1, Col 4 | Severity, Count |
| Issues by Status | Row 1, Col 7 | Status, Count |
| Director Breakdown | Row 10, Col 1 | Director, Total, Open, Critical, In Progress, Resolved |
| Issues by Triage Category | Row 10, Col 8 | Triage Category, Count |
| Recent 8-Week Trend | Row 20, Col 1 | Week, Critical, High, Medium, Low |

---

## 9. Data Generator (`generate_data.py`)

Run once to (re)generate `defects.csv` with fresh synthetic data:

```bash
python generate_data.py
# Output: defects.csv  (220 records, 16 columns)
```

### Generation Logic

| Aspect | Detail |
|--------|--------|
| Record count | 220 defects |
| Date range | Last 26 weeks from 28 Feb 2026 (i.e., Sep 2025 – Feb 2026) |
| Random seed | Fixed (`42`) for reproducibility |
| Priority | Weighted random: 8% Critical, 22% High, 45% Medium, 25% Low |
| Severity | Derived from priority (e.g., Critical → S1 or S2 only) |
| Status | Weighted random: 28% Open, 22% In Progress, 10% In Review, 22% Resolved, 12% Closed, 6% Won't Fix |
| Title | 15 realistic templates using ROCm API names and release versions |
| Assignee | Empty for Open status; random team member otherwise |
| Resolution | Empty for open statuses; one of Fixed / Won't Fix / Duplicate / Cannot Reproduce / By Design |
| Last Updated | Random date between `Created_Date` and `END_DATE` |

### API Names Used in Titles

`hipMalloc`, `hipLaunchKernelGGL`, `rocblas_gemm`, `miopen_conv`, `rccl_allreduce`, `hipFFT_plan`, `hipGraphCreate`, `rocblas_trsm`, `hipDeviceSynchronize`, `rocsparseDcsrmv`, `hipStreamCreate`

---

## 10. Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Navigate to project directory
cd /path/to/Defect_Dashboard

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Regenerate the dataset
python generate_data.py

# 5. (Optional) Regenerate the Excel file
python generate_excel.py
```

### `requirements.txt`

```
dash>=2.14.0
pandas>=2.0.0
plotly>=5.18.0
numpy>=1.24.0
openpyxl>=3.1.0
```

---

## 11. Running the Project

### Option A — Web Dashboard

```bash
python dashboard.py
```

Open a browser and go to: **http://127.0.0.1:8050**

The server runs in debug mode by default. To change the port, edit the last line of `dashboard.py`:
```python
app.run(debug=True, host="127.0.0.1", port=8050)
```

### Option B — Excel Dashboard

```bash
python generate_excel.py
```

This overwrites `ROCm_Defect_Dashboard.xlsx` in the same directory. Open the file in Microsoft Excel (version 2016 or later recommended for best chart rendering).

### Option C — Regenerate Sample Data

```bash
python generate_data.py
```

This overwrites `defects.csv`. Re-run `generate_excel.py` afterwards if you also want a fresh Excel file.

---

## 12. Dashboard Features Reference

### Sorting & Filtering in the Defect Table

The web dashboard table supports:
- **Column-level sort** (click column headers) — ascending/descending
- **Column-level filter** using Dash's native `filter_action="native"` (type filter expressions in the text boxes under each header)
- **Pagination** — 15 records per page

### Filter Expression Examples (Defect Table)

| Goal | Filter Box Column | Expression |
|------|------------------|------------|
| Show only Critical defects | Priority | `= Critical` |
| Show Open and In Progress | Status | `= Open \|\| = In Progress` |
| Show defects assigned to Alex | Assignee | `contains Alex` |

### Date Range Behavior

- Default date range spans the **full dataset** (earliest to latest `Created_Date`)
- Changing the date range filters all KPIs, charts, and the defect table
- The date picker displays dates in `DD MMM YYYY` format (e.g., `01 Sep 2025`)

---

## 13. Color Coding Reference

### Priority Colors

| Priority | Web (Hex) | Excel Fill | Excel Font |
|----------|-----------|-----------|-----------|
| Critical | `#ef4444` (red) | `FADBD8` | `C0392B` |
| High | `#f97316` (orange) | `FDEBD0` | `E67E22` |
| Medium | `#eab308` (yellow) | `FEF9E7` | `D4AC0D` |
| Low | `#22c55e` (green) | `EAFAF1` | `27AE60` |

### Severity Colors

| Severity | Web (Hex) | Excel Fill |
|----------|-----------|-----------|
| S1 - Blocker | `#ef4444` | `FADBD8` |
| S2 - Critical | `#f97316` | `FDEBD0` |
| S3 - Major | `#eab308` | `FEF9E7` |
| S4 - Minor | `#22c55e` | `EAFAF1` |

### Status Colors

| Status | Web (Hex) | Excel Fill |
|--------|-----------|-----------|
| Open | `#ef4444` | `FADBD8` |
| In Progress | `#f97316` | `FDEBD0` |
| In Review | `#eab308` | `FEF9E7` |
| Resolved | `#22c55e` | `EAFAF1` |
| Closed | `#6b7280` | `ECF0F1` |
| Won't Fix | `#8b5cf6` | `F4ECF7` |

### Director Colors (Web)

| Director | Color |
|----------|-------|
| SAM | `#7c3aed` (purple) |
| Kumar | `#06b6d4` (cyan) |
| Philips | `#10b981` (emerald) |
| Suma | `#f59e0b` (amber) |
| Ravi | `#ec4899` (pink) |

---

## 14. Dark / Light Theme Toggle

### Overview

The web dashboard (`dashboard.py`) supports a full **Dark / Light theme toggle** that instantly re-renders all containers, charts, tables, and the header without a page reload.

### How It Works

| Component | Mechanism |
|-----------|-----------|
| Theme state | `dcc.Store(id="theme", data="dark")` — persists current theme in the browser |
| Toggle button | `html.Div(id="theme-btn")` in the header — click to flip the theme |
| Callback 1 | `toggle_theme` — flips `"dark"` ↔ `"light"` in the store on each click |
| Callback 2 | `update_all` — takes `theme` as an `Input`; rebuilds all 10 chart figures and all container inline styles in one pass |

### Theme Palette

| Token | Dark Mode | Light Mode |
|-------|-----------|------------|
| Page background | `#0f1117` | `#F0F4F8` |
| Card background | `#1a1f2e` | `#FFFFFF` |
| Secondary card | `#13172a` | `#E8EDF5` |
| Border | `#2d3748` | `#CBD5E0` |
| Primary text | `#e2e8f0` | `#1A202C` |
| Secondary text | `#94a3b8` | `#4A5568` |
| Accent (purple) | `#7c3aed` | `#5B21B6` |
| Grid lines | `#2d3748` | `#E2E8F0` |
| Table header | `#212840` | `#4A5568` |
| Table odd rows | `#151929` | `#F7FAFC` |

### Toggle Button States

| Current Theme | Button Shows | Action |
|---------------|-------------|--------|
| Dark | `☀  Light Mode` | Click → switches to Light |
| Light | `🌙  Dark Mode` | Click → switches to Dark |

### Screenshots

#### Dark Mode
![Dark Mode Dashboard](screenshot_dark.png)

*Dark mode features a deep navy/charcoal background (`#0f1117`), purple accent borders, and light text — ideal for low-light environments and extended use.*

#### Light Mode
![Light Mode Dashboard](screenshot_light.png)

*Light mode uses a clean off-white background (`#F0F4F8`) with dark text and subtle grey borders — ideal for presentations and daylight use.*

### CSS Transitions

A global CSS transition is injected via `app.index_string` to produce smooth 0.25 s color fades between themes:

```css
* {
  box-sizing: border-box;
  transition: background-color 0.25s, color 0.2s, border-color 0.2s;
}
```

### What Updates on Theme Change

- Page wrapper background and font color
- Header bar background and accent border
- Filter bar background
- Brand text and subtitle colors
- Toggle button fill, border, and label
- All 10 chart `paper_bgcolor`, `plot_bgcolor`, axis/grid colors, legend text
- All chart panel card backgrounds and borders
- Defect table: header fill, cell fill, row striping
- Table count label color

---

## 15. System Architecture

The diagram below shows the full data and execution flow of the ROCm Defect Dashboard system.

![ROCm Defect Dashboard — System Architecture](architecture.png)

*Data flow: `generate_data.py` seeds `defects.csv`, which is consumed by both the Plotly Dash web app and the openpyxl Excel generator. The Excel file is further enhanced by `add_excel_theme.py` (VBA macro injection) to produce the macro-enabled `.xlsm` with dark/light toggle.*

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Synthetic data (seed=42) | Reproducible demos without exposing real defect data |
| Plotly Dash 4.0 | Single-page reactive app; callbacks handle all filtering |
| `dcc.Store` for theme | Browser-side state; no server round-trip for theme switch |
| openpyxl (no xlsxwriter) | Pure Python; supports both write and read; no COM dependency for generation |
| win32com for VBA injection | Only way to programmatically add macro code + shape buttons to .xlsm |
| CSV as shared data layer | Both dashboard.py and generate_excel.py read the same file |

---

## 16. Excel Dashboard Screenshots

The Excel workbook (`ROCm_Defect_Dashboard.xlsm`) contains three sheets with embedded charts and a Dark/Light theme toggle button.

### Dashboard Sheet — Header & KPIs

![Excel Dashboard Header and KPI Cards](xl_dash_top.png)

*The Dashboard sheet opens with the navy banner, 6 KPI metric cards (colour-coded by severity/count), and the Director Summary table. The Dark/Light theme toggle button sits in the top-right area.*

### Dashboard Sheet — Trend & Director Overview

![Excel Dashboard Charts Row 1 — WoW Trend and Director Overview](xl_dash_ch1.png)

*Row 1 of charts: **Week-over-Week Defect Trend** (stacked bar by severity) and **Director × Severity Overview** (grouped bar).*

### Dashboard Sheet — Triage & WoW by Director

![Excel Dashboard Charts Row 2 — Triage and WoW by Director](xl_dash_ch2.png)

*Row 2: **Triage Status Breakdown** (stacked bar showing Open/In-Progress/Resolved/Closed split per triage stage) and **WoW Trend by Director** (multi-line chart).*

### Dashboard Sheet — Priority, Severity & Status

![Excel Dashboard Charts Row 3 — Priority, Severity and Status](xl_dash_ch3.png)

*Row 3: **Status Distribution** (bar), **Priority Distribution** (pie), **Severity Distribution** (pie).*

### Dashboard Sheet — Top Categories & Assignees

![Excel Dashboard Charts Row 4 — Top Categories and Assignees](xl_dash_ch4.png)

*Row 4: **Top 8 Defect Categories** (horizontal bar) and **Top 8 Assignees by Open Defects** (horizontal bar).*

### Defects Sheet

![Excel Defects Sheet — Raw Data](xl_defects.png)

*The Defects sheet contains all 220 raw defect records with full column formatting: colour-coded priority, severity, and status columns; freeze-panes on the header row; auto-filter enabled.*

### Summary Sheet

![Excel Summary Sheet — Pivot Table](xl_summary.png)

*The Summary sheet presents a pivot-style breakdown of defect counts by Director, Priority, and Status, giving an at-a-glance executive view.*

---

*Document updated for Confluence — ROCm Defect Dashboard v1.1 — Architecture diagram and Excel screenshots added*
