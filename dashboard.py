"""
ROCm Defect Dashboard  —  with Dark / Light theme toggle
Run: python dashboard.py  →  open http://127.0.0.1:8050
"""

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import warnings
warnings.filterwarnings("ignore")

# ── Data ───────────────────────────────────────────────────────────────────────
df = pd.read_csv("defects.csv", parse_dates=["Created_Date", "Last_Updated_Date"])
df["Week_Start"] = df["Created_Date"].dt.to_period("W").apply(lambda p: p.start_time)
df["Week_Label"] = df["Week_Start"].dt.strftime("%d %b")

PRIORITY_ORDER = ["Critical", "High", "Medium", "Low"]
SEVERITY_ORDER = ["S1 - Blocker", "S2 - Critical", "S3 - Major", "S4 - Minor"]
STATUS_ORDER   = ["Open", "In Progress", "In Review", "Resolved", "Closed", "Won't Fix"]

PRIORITY_COLORS = {"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#22c55e"}
SEVERITY_COLORS = {"S1 - Blocker":"#ef4444","S2 - Critical":"#f97316",
                   "S3 - Major":"#eab308","S4 - Minor":"#22c55e"}
STATUS_COLORS   = {"Open":"#ef4444","In Progress":"#f97316","In Review":"#eab308",
                   "Resolved":"#22c55e","Closed":"#6b7280","Won't Fix":"#8b5cf6"}
DIRECTOR_COLORS = {"SAM":"#7c3aed","Kumar":"#06b6d4","Philips":"#10b981",
                   "Suma":"#f59e0b","Ravi":"#ec4899"}

# ── Theme Definitions ──────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "BG":           "#0f1117",
        "CARD":         "#1a1f2e",
        "CARD2":        "#13172a",
        "BORDER":       "#2d3748",
        "TEXT":         "#e2e8f0",
        "SUBTEXT":      "#94a3b8",
        "ACCENT":       "#7c3aed",
        "GRID":         "#2d3748",
        "TBL_HEADER":   "#212840",
        "TBL_ODD":      "#151929",
        "TBL_EVEN":     "#1a1f2e",
        "BTN_BG":       "#1a1f2e",
        "BTN_BORDER":   "#7c3aed",
        "BTN_TEXT":     "#e2e8f0",
        "BTN_ICON":     "☀",
        "BTN_LABEL":    "Light Mode",
        "HEADER_BORDER":"#7c3aed",
        "SEL_BG":       "#1e2535",
        "SEL_HOVER":    "#2d3748",
    },
    "light": {
        "BG":           "#F0F4F8",
        "CARD":         "#FFFFFF",
        "CARD2":        "#E8EDF5",
        "BORDER":       "#CBD5E0",
        "TEXT":         "#1A202C",
        "SUBTEXT":      "#4A5568",
        "ACCENT":       "#5B21B6",
        "GRID":         "#E2E8F0",
        "TBL_HEADER":   "#4A5568",
        "TBL_ODD":      "#F7FAFC",
        "TBL_EVEN":     "#FFFFFF",
        "BTN_BG":       "#FFFFFF",
        "BTN_BORDER":   "#5B21B6",
        "BTN_TEXT":     "#1A202C",
        "BTN_ICON":     "🌙",
        "BTN_LABEL":    "Dark Mode",
        "HEADER_BORDER":"#5B21B6",
        "SEL_BG":       "#FFFFFF",
        "SEL_HOVER":    "#EEF2FF",
    },
}

def T(theme_name: str) -> dict:
    return THEMES[theme_name]

# ── App ────────────────────────────────────────────────────────────────────────
app = Dash(__name__, title="ROCm Defect Dashboard")

# Inject base CSS (theme-switcher overrides via inline styles)
app.index_string = app.index_string.replace("<head>", """<head><style>
* { box-sizing: border-box; transition: background-color 0.25s, color 0.2s, border-color 0.2s; }
body { margin: 0; font-family: Inter, 'Segoe UI', sans-serif; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #4a5568; border-radius: 3px; }
/* Dropdown overrides injected dynamically via style prop */
.Select-control { border-radius: 6px !important; }
.Select-menu-outer { z-index: 9999 !important; }
</style>""")

# ── Layout helpers ─────────────────────────────────────────────────────────────
def kpi_card(title, value, sub, color, t):
    return html.Div([
        html.Div(title, style={"color": "rgba(255,255,255,0.75)", "fontSize":"10px",
                               "letterSpacing":"1px","textTransform":"uppercase"}),
        html.Div(value, style={"color": "#fff", "fontSize":"30px",
                               "fontWeight":700,"lineHeight":"1.1"}),
        html.Div(sub,   style={"color": "rgba(255,255,255,0.65)", "fontSize":"11px",
                               "marginTop":"2px"}),
    ], style={
        "background": color, "borderRadius":"8px", "padding":"12px 16px",
        "flex":1, "minWidth":"120px",
        "boxShadow": "0 2px 8px rgba(0,0,0,0.2)" if t == "dark" else "0 2px 8px rgba(0,0,0,0.08)",
    })


def section_label(text, t):
    return html.Div(text, style={
        "color": THEMES[t]["TEXT"], "fontSize":"12px",
        "fontWeight":600, "letterSpacing":"0.4px", "marginBottom":"6px",
    })


def chart_panel(header_text, graph_id, flex=1, height="300px"):
    """Shell card — styles injected per-theme in callback via panel-* IDs."""
    return html.Div([
        html.Div(header_text, id=f"lbl-{graph_id}", style={
            "fontSize":"12px","fontWeight":600,"letterSpacing":"0.4px","marginBottom":"6px",
        }),
        dcc.Graph(id=graph_id, config={"displayModeBar": False}, style={"height": height}),
    ], id=f"panel-{graph_id}", style={"flex": flex, "borderRadius":"8px", "padding":"14px"})


def filter_dropdown(fid, col, placeholder):
    return dcc.Dropdown(
        id=fid,
        options=[{"label": v, "value": v} for v in sorted(df[col].dropna().unique())],
        multi=True, placeholder=placeholder,
        style={"fontSize":"12px"},
    )


def filter_col(label, comp):
    return html.Div([
        html.Label(label, style={"fontSize":"10px","letterSpacing":"1px",
                                 "textTransform":"uppercase","marginBottom":"4px",
                                 "display":"block"}),
        comp,
    ], style={"flex":1,"display":"flex","flexDirection":"column","minWidth":"130px"})


# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div(id="page-wrap", style={"minHeight":"100vh","fontFamily":"Inter,'Segoe UI',sans-serif"}, children=[

    dcc.Store(id="theme", data="dark"),

    # ── Header row ────────────────────────────────────────────────────────────
    html.Div(id="header-div", style={"display":"flex","justifyContent":"space-between",
                                      "alignItems":"center","padding":"16px 28px"}, children=[
        html.Div([
            html.Span("ROCm ", id="brand-accent", style={"fontWeight":800}),
            html.Span("Defect Dashboard", id="brand-text", style={"fontWeight":700}),
        ], style={"fontSize":"22px"}),
        html.Div("Software Development  ·  Defect Tracking & Analytics",
                 id="brand-sub", style={"fontSize":"12px","marginTop":"2px"}),
        # Theme toggle button
        html.Div(id="theme-btn", n_clicks=0, children="☀  Light Mode",
                 style={"cursor":"pointer","borderRadius":"20px","padding":"7px 18px",
                        "fontSize":"12px","fontWeight":600,"userSelect":"none",
                        "whiteSpace":"nowrap","border":"1px solid"}),
    ]),

    # ── Filters ───────────────────────────────────────────────────────────────
    html.Div(id="filter-bar", style={"display":"flex","gap":"14px","padding":"14px 28px",
                                      "alignItems":"flex-end","flexWrap":"wrap"}, children=[
        filter_col("Date Range", dcc.DatePickerRange(
            id="f-date",
            start_date=df["Created_Date"].min().date(),
            end_date=df["Created_Date"].max().date(),
            display_format="DD MMM YYYY", style={"fontSize":"12px"},
        )),
        filter_col("Director",          filter_dropdown("f-director","Director",          "All Directors")),
        filter_col("Priority",          filter_dropdown("f-priority","Priority",           "All Priorities")),
        filter_col("Severity",          filter_dropdown("f-severity","Severity",           "All Severities")),
        filter_col("Status",            filter_dropdown("f-status",  "Status",             "All Statuses")),
        filter_col("Triage Assignment", filter_dropdown("f-triage",  "Triage_Assignment",  "All Teams")),
    ]),

    # ── KPI row ───────────────────────────────────────────────────────────────
    html.Div(id="kpi-row", style={"display":"flex","gap":"10px","padding":"14px 28px","flexWrap":"wrap"}),

    # ── Row 1: WoW + Director ─────────────────────────────────────────────────
    html.Div([
        chart_panel("Week-on-Week Issues Created  (by Priority)", "chart-wow",      flex=2.2, height="300px"),
        chart_panel("Issues by Director  (by Severity)",          "chart-director", flex=1,   height="300px"),
    ], style={"display":"flex","gap":"12px","padding":"0 28px 12px"}),

    # ── Row 2: Triage + Priority donut + Severity donut ───────────────────────
    html.Div([
        chart_panel("Issues by Triage Assignment  (by Status)", "chart-triage",   flex=1.6, height="270px"),
        chart_panel("Issues by Priority",                       "chart-priority", flex=1,   height="270px"),
        chart_panel("Issues by Severity",                       "chart-severity", flex=1,   height="270px"),
    ], style={"display":"flex","gap":"12px","padding":"0 28px 12px"}),

    # ── Row 3: Category + Status + Assignees ──────────────────────────────────
    html.Div([
        chart_panel("Issues by Triage Category",    "chart-category", flex=1.4, height="270px"),
        chart_panel("Status Breakdown",             "chart-status",   flex=1,   height="270px"),
        chart_panel("Top Assignees  (open issues)", "chart-assignee", flex=1.2, height="270px"),
    ], style={"display":"flex","gap":"12px","padding":"0 28px 12px"}),

    # ── Row 4: WoW by Director (line) + Target Release ───────────────────────
    html.Div([
        chart_panel("Week-on-Week Issues by Director", "chart-wow-director", flex=2,   height="250px"),
        chart_panel("Target Release Distribution",     "chart-release",      flex=1,   height="250px"),
    ], style={"display":"flex","gap":"12px","padding":"0 28px 12px"}),

    # ── Defect table ──────────────────────────────────────────────────────────
    html.Div(id="table-panel", style={"padding":"0 28px 30px"}, children=[
        html.Div([
            html.Span("Defect Log", id="tbl-title",
                      style={"fontSize":"14px","fontWeight":600}),
            html.Span(id="table-count",
                      style={"fontSize":"12px","marginLeft":"12px"}),
        ], style={"marginBottom":"10px"}),

        dash_table.DataTable(
            id="defect-table",
            columns=[{"name": c.replace("_"," "), "id": c} for c in [
                "Defect_ID","Title","Created_Date","Created_By",
                "Priority","Severity","Status",
                "Triage_Category","Triage_Assignment","Director","Assignee",
                "Target_Release","Last_Updated_Date",
            ]],
            style_table={"overflowX":"auto"},
            style_data_conditional=[
                {"if":{"filter_query":'{Priority} = "Critical"',"column_id":"Priority"},
                 "color":"#ef4444","fontWeight":700},
                {"if":{"filter_query":'{Priority} = "High"',   "column_id":"Priority"},"color":"#f97316"},
                {"if":{"filter_query":'{Priority} = "Medium"', "column_id":"Priority"},"color":"#eab308"},
                {"if":{"filter_query":'{Priority} = "Low"',    "column_id":"Priority"},"color":"#22c55e"},
                {"if":{"filter_query":'{Status} = "Open"',     "column_id":"Status"},  "color":"#ef4444"},
                {"if":{"filter_query":'{Status} = "Resolved"', "column_id":"Status"},  "color":"#22c55e"},
                {"if":{"filter_query":'{Status} = "Closed"',   "column_id":"Status"},  "color":"#6b7280"},
                {"if":{"filter_query":'{Director} = "SAM"',    "column_id":"Director"},"color":"#7c3aed","fontWeight":600},
                {"if":{"filter_query":'{Director} = "Kumar"',  "column_id":"Director"},"color":"#06b6d4","fontWeight":600},
                {"if":{"filter_query":'{Director} = "Philips"',"column_id":"Director"},"color":"#10b981","fontWeight":600},
                {"if":{"filter_query":'{Director} = "Suma"',   "column_id":"Director"},"color":"#f59e0b","fontWeight":600},
                {"if":{"filter_query":'{Director} = "Ravi"',   "column_id":"Director"},"color":"#ec4899","fontWeight":600},
            ],
            page_size=15, sort_action="native", filter_action="native",
        ),
    ]),
])


# ── Callback 1: toggle theme store ────────────────────────────────────────────
@callback(
    Output("theme", "data"),
    Input("theme-btn", "n_clicks"),
    State("theme", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current):
    return "light" if current == "dark" else "dark"


# ── Helper: apply filter mask ─────────────────────────────────────────────────
def apply_filters(start, end, directors, priorities, severities, statuses, triages):
    dff = df[
        (df["Created_Date"] >= pd.to_datetime(start)) &
        (df["Created_Date"] <= pd.to_datetime(end))
    ].copy()
    if directors:  dff = dff[dff["Director"].isin(directors)]
    if priorities: dff = dff[dff["Priority"].isin(priorities)]
    if severities: dff = dff[dff["Severity"].isin(severities)]
    if statuses:   dff = dff[dff["Status"].isin(statuses)]
    if triages:    dff = dff[dff["Triage_Assignment"].isin(triages)]
    return dff


# ── Callback 2: update everything ─────────────────────────────────────────────
PANEL_IDS = [
    "chart-wow","chart-director","chart-triage","chart-priority",
    "chart-severity","chart-category","chart-status","chart-assignee",
    "chart-wow-director","chart-release",
]

@callback(
    # KPI + table
    Output("kpi-row",          "children"),
    Output("table-count",      "children"),
    Output("defect-table",     "data"),
    Output("defect-table",     "style_header"),
    Output("defect-table",     "style_cell"),
    Output("defect-table",     "style_data_conditional"),
    # Charts
    Output("chart-wow",          "figure"),
    Output("chart-director",     "figure"),
    Output("chart-triage",       "figure"),
    Output("chart-priority",     "figure"),
    Output("chart-severity",     "figure"),
    Output("chart-category",     "figure"),
    Output("chart-status",       "figure"),
    Output("chart-assignee",     "figure"),
    Output("chart-wow-director", "figure"),
    Output("chart-release",      "figure"),
    # Containers
    Output("page-wrap",    "style"),
    Output("header-div",   "style"),
    Output("filter-bar",   "style"),
    Output("brand-accent", "style"),
    Output("brand-text",   "style"),
    Output("brand-sub",    "style"),
    Output("theme-btn",    "children"),
    Output("theme-btn",    "style"),
    Output("table-panel",  "style"),
    Output("tbl-title",    "style"),
    Output("table-count",  "style"),
    # Panel cards (10 panels)
    *[Output(f"panel-{pid}", "style") for pid in PANEL_IDS],
    *[Output(f"lbl-{pid}",   "style") for pid in PANEL_IDS],
    # Filter bar label colors
    # Inputs
    Input("theme",       "data"),
    Input("f-date",      "start_date"),
    Input("f-date",      "end_date"),
    Input("f-director",  "value"),
    Input("f-priority",  "value"),
    Input("f-severity",  "value"),
    Input("f-status",    "value"),
    Input("f-triage",    "value"),
)
def update_all(theme_name, start, end, directors, priorities, severities, statuses, triages):
    t = THEMES[theme_name]
    dff = apply_filters(start, end, directors, priorities, severities, statuses, triages)

    total    = len(dff)
    open_cnt = len(dff[dff["Status"] == "Open"])
    crit_cnt = len(dff[dff["Priority"] == "Critical"])
    blocker  = len(dff[dff["Severity"] == "S1 - Blocker"])
    res_cnt  = len(dff[dff["Status"].isin(["Resolved","Closed"])])
    prog_cnt = len(dff[dff["Status"] == "In Progress"])

    # ── Chart layout base ──────────────────────────────────────────────────────
    CL = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=t["TEXT"], family="Inter, Segoe UI, sans-serif", size=11),
        margin=dict(l=10, r=10, t=36, b=10),
    )
    GC = dict(gridcolor=t["GRID"], zerolinecolor=t["GRID"])
    LEG = dict(bgcolor="rgba(0,0,0,0)", font_size=10, font_color=t["TEXT"])

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpi_data = [
        ("Total Defects",    str(total),    "all records",       t["ACCENT"]),
        ("Open",             str(open_cnt), "awaiting action",   "#ef4444"),
        ("S1 Blockers",      str(blocker),  "highest severity",  "#ef4444"),
        ("Critical (P1)",    str(crit_cnt), "priority 1",        "#f97316"),
        ("In Progress",      str(prog_cnt), "being worked on",   "#eab308"),
        ("Resolved/Closed",  str(res_cnt),  "completed",         "#22c55e"),
    ]
    kpis = [kpi_card(title, val, sub, color, theme_name) for title, val, sub, color, *_ in
            [(d[0], d[1], d[2], d[3]) for d in kpi_data]]
    # Fix: unpack properly
    kpis = []
    for title, val, sub, color in [(d[0],d[1],d[2],d[3]) for d in kpi_data]:
        kpis.append(kpi_card(title, val, sub, color, theme_name))

    # ── Table ─────────────────────────────────────────────────────────────────
    cols = ["Defect_ID","Title","Created_Date","Created_By","Priority","Severity","Status",
            "Triage_Category","Triage_Assignment","Director","Assignee","Target_Release","Last_Updated_Date"]
    tbl_rows = dff.sort_values("Created_Date", ascending=False)[cols].to_dict("records")
    for row in tbl_rows:
        row["Created_Date"]      = str(row["Created_Date"])[:10]
        row["Last_Updated_Date"] = str(row["Last_Updated_Date"])[:10]
    tbl_label = f"{total} record{'s' if total != 1 else ''}"

    tbl_header_style = {
        "backgroundColor": t["TBL_HEADER"], "color": t["TEXT"],
        "fontWeight":600, "fontSize":"11px", "border": f"1px solid {t['BORDER']}",
        "letterSpacing":"0.5px",
    }
    tbl_cell_style = {
        "backgroundColor": t["CARD"], "color": t["TEXT"], "fontSize":"11px",
        "border": f"1px solid {t['BORDER']}", "padding":"7px 12px",
        "textOverflow":"ellipsis", "overflow":"hidden", "maxWidth":"220px",
        "fontFamily":"Inter, Segoe UI, sans-serif",
    }
    tbl_conditional = [
        {"if": {"row_index":"odd"}, "backgroundColor": t["TBL_ODD"]},
        {"if":{"filter_query":'{Priority} = "Critical"',"column_id":"Priority"},
         "color":"#ef4444","fontWeight":700},
        {"if":{"filter_query":'{Priority} = "High"',   "column_id":"Priority"},"color":"#f97316"},
        {"if":{"filter_query":'{Priority} = "Medium"', "column_id":"Priority"},"color":"#eab308"},
        {"if":{"filter_query":'{Priority} = "Low"',    "column_id":"Priority"},"color":"#22c55e"},
        {"if":{"filter_query":'{Status} = "Open"',     "column_id":"Status"},  "color":"#ef4444"},
        {"if":{"filter_query":'{Status} = "Resolved"', "column_id":"Status"},  "color":"#22c55e"},
        {"if":{"filter_query":'{Status} = "Closed"',   "column_id":"Status"},  "color":"#6b7280"},
        {"if":{"filter_query":'{Director} = "SAM"',    "column_id":"Director"},"color":"#7c3aed","fontWeight":600},
        {"if":{"filter_query":'{Director} = "Kumar"',  "column_id":"Director"},"color":"#06b6d4","fontWeight":600},
        {"if":{"filter_query":'{Director} = "Philips"',"column_id":"Director"},"color":"#10b981","fontWeight":600},
        {"if":{"filter_query":'{Director} = "Suma"',   "column_id":"Director"},"color":"#f59e0b","fontWeight":600},
        {"if":{"filter_query":'{Director} = "Ravi"',   "column_id":"Director"},"color":"#ec4899","fontWeight":600},
    ]

    # ── Charts ────────────────────────────────────────────────────────────────
    def stacked_bar(data, x, y, color, order, color_map, horiz=False, bargap=0.25):
        cat = {color: order}
        data[color] = pd.Categorical(data[color], categories=order, ordered=True)
        data = data.sort_values([x if not horiz else y, color])
        if horiz:
            fig = px.bar(data, x=y, y=x, color=color, orientation="h",
                         color_discrete_map=color_map, category_orders=cat, barmode="stack")
        else:
            fig = px.bar(data, x=x, y=y, color=color, orientation="v",
                         color_discrete_map=color_map, category_orders=cat, barmode="stack")
        return fig

    # WoW
    wow = (dff.groupby(["Week_Start","Week_Label","Priority"])
              .size().reset_index(name="Count"))
    fig_wow = stacked_bar(wow,"Week_Label","Count","Priority",PRIORITY_ORDER,PRIORITY_COLORS)
    fig_wow.update_layout(**CL, bargap=bargap if False else 0.25,
                          xaxis_title="", yaxis_title="Issues Created",
                          legend=dict(**LEG))
    fig_wow.update_layout(bargap=0.25)
    fig_wow.update_xaxes(**GC, tickfont_size=9, tickangle=-45)
    fig_wow.update_yaxes(**GC)

    # Director × Severity
    dir_data = (dff.groupby(["Director","Severity"]).size().reset_index(name="Count"))
    dir_data["Severity"] = pd.Categorical(dir_data["Severity"], categories=SEVERITY_ORDER, ordered=True)
    dir_data = dir_data.sort_values(["Director","Severity"])
    fig_director = px.bar(dir_data, x="Count", y="Director", color="Severity",
                          orientation="h", color_discrete_map=SEVERITY_COLORS,
                          category_orders={"Severity": SEVERITY_ORDER}, barmode="stack")
    fig_director.update_layout(**CL, xaxis_title="Count", yaxis_title="",
                               legend={**LEG, "orientation": "h", "y": -0.22, "x": 0, "font_size": 9})
    fig_director.update_xaxes(**GC)
    fig_director.update_yaxes(**GC, automargin=True)

    # Triage × Status
    tr_data = (dff.groupby(["Triage_Assignment","Status"]).size().reset_index(name="Count"))
    fig_triage = px.bar(tr_data, x="Count", y="Triage_Assignment", color="Status",
                        orientation="h", color_discrete_map=STATUS_COLORS,
                        category_orders={"Status": STATUS_ORDER}, barmode="stack")
    fig_triage.update_layout(**CL, xaxis_title="Count", yaxis_title="",
                             legend={**LEG, "orientation": "h", "y": -0.22, "x": 0, "font_size": 9})
    fig_triage.update_xaxes(**GC)
    fig_triage.update_yaxes(**GC, automargin=True)

    # Priority donut
    pdata = dff["Priority"].value_counts().reindex(PRIORITY_ORDER, fill_value=0).reset_index()
    pdata.columns = ["Priority","Count"]
    fig_priority = px.pie(pdata, names="Priority", values="Count",
                          color="Priority", color_discrete_map=PRIORITY_COLORS, hole=0.55)
    fig_priority.update_layout(**CL, legend=dict(**LEG))
    fig_priority.update_traces(textinfo="label+percent", textfont_size=10,
                               textfont_color=t["TEXT"])

    # Severity donut
    sev = dff["Severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0).reset_index()
    sev.columns = ["Severity","Count"]
    fig_severity = px.pie(sev, names="Severity", values="Count",
                          color="Severity", color_discrete_map=SEVERITY_COLORS, hole=0.55)
    fig_severity.update_layout(**CL, legend=dict(**LEG))
    fig_severity.update_traces(textinfo="label+percent", textfont_size=10,
                               textfont_color=t["TEXT"])

    # Category bar
    cat_data = dff["Triage_Category"].value_counts().reset_index()
    cat_data.columns = ["Category","Count"]
    fig_category = px.bar(cat_data.sort_values("Count"), x="Count", y="Category",
                          orientation="h", color_discrete_sequence=[t["ACCENT"]])
    fig_category.update_layout(**CL, xaxis_title="Count", yaxis_title="",
                               legend=dict(**LEG))
    fig_category.update_xaxes(**GC)
    fig_category.update_yaxes(**GC, automargin=True)

    # Status bar
    st = dff["Status"].value_counts().reindex(STATUS_ORDER, fill_value=0).reset_index()
    st.columns = ["Status","Count"]
    fig_status = px.bar(st, x="Status", y="Count",
                        color="Status", color_discrete_map=STATUS_COLORS)
    fig_status.update_layout(**CL, showlegend=False, xaxis_title="", yaxis_title="Count")
    fig_status.update_xaxes(**GC)
    fig_status.update_yaxes(**GC)

    # Assignees bar
    open_df = dff[dff["Status"].isin(["Open","In Progress","In Review"]) & (dff["Assignee"] != "")]
    asgn = open_df["Assignee"].value_counts().head(10).reset_index()
    asgn.columns = ["Assignee","Count"]
    fig_assignee = px.bar(asgn.sort_values("Count"), x="Count", y="Assignee",
                          orientation="h", color_discrete_sequence=[t["ACCENT"]])
    fig_assignee.update_layout(**CL, xaxis_title="Open Issues", yaxis_title="",
                               legend=dict(**LEG))
    fig_assignee.update_xaxes(**GC)
    fig_assignee.update_yaxes(**GC, automargin=True)

    # WoW by Director (line)
    wdir = (dff.groupby(["Week_Start","Week_Label","Director"])
               .size().reset_index(name="Count")).sort_values("Week_Start")
    fig_wdir = px.line(wdir, x="Week_Label", y="Count", color="Director",
                       color_discrete_map=DIRECTOR_COLORS, markers=True)
    fig_wdir.update_layout(**CL, xaxis_title="", yaxis_title="Issues Created",
                           legend=dict(**LEG))
    fig_wdir.update_xaxes(**GC, tickfont_size=9, tickangle=-45)
    fig_wdir.update_yaxes(**GC)
    fig_wdir.update_traces(line_width=2, marker_size=5)

    # Release bar
    rel = dff["Target_Release"].value_counts().reset_index()
    rel.columns = ["Release","Count"]
    fig_release = px.bar(rel, x="Release", y="Count",
                         color_discrete_sequence=["#06b6d4"])
    fig_release.update_layout(**CL, xaxis_title="", yaxis_title="Count", legend=dict(**LEG))
    fig_release.update_xaxes(**GC)
    fig_release.update_yaxes(**GC)

    # ── Container styles ──────────────────────────────────────────────────────
    page_style = {
        "background": t["BG"], "minHeight":"100vh",
        "fontFamily":"Inter,'Segoe UI',sans-serif",
    }
    header_style = {
        "display":"flex","justifyContent":"space-between","alignItems":"center",
        "padding":"16px 28px","background":t["CARD"],
        "borderBottom":f"2px solid {t['ACCENT']}",
    }
    filter_style = {
        "display":"flex","gap":"14px","padding":"14px 28px",
        "background":t["CARD2"],"borderBottom":f"1px solid {t['BORDER']}",
        "alignItems":"flex-end","flexWrap":"wrap",
    }
    brand_accent_style = {"color": t["ACCENT"], "fontWeight":800}
    brand_text_style   = {"color": t["TEXT"],   "fontWeight":700}
    brand_sub_style    = {"color": t["SUBTEXT"],"fontSize":"12px","marginTop":"2px"}

    btn_label = f"{t['BTN_ICON']}  {t['BTN_LABEL']}"
    btn_style = {
        "cursor":"pointer","borderRadius":"20px","padding":"7px 18px",
        "fontSize":"12px","fontWeight":600,"userSelect":"none","whiteSpace":"nowrap",
        "background": t["BTN_BG"], "color": t["BTN_TEXT"],
        "border": f"1px solid {t['BTN_BORDER']}",
        "boxShadow": "0 1px 4px rgba(0,0,0,0.15)",
    }

    table_panel_style = {"padding":"0 28px 30px","background":t["BG"]}
    tbl_title_style   = {"fontSize":"14px","fontWeight":600,"color":t["TEXT"]}
    tbl_count_style   = {"fontSize":"12px","marginLeft":"12px","color":t["SUBTEXT"]}

    panel_style = {
        "borderRadius":"8px","padding":"14px",
        "background":t["CARD"],"border":f"1px solid {t['BORDER']}",
        "boxShadow":"0 1px 3px rgba(0,0,0,0.1)" if theme_name=="light" else "none",
    }
    lbl_style = {"color":t["TEXT"],"fontSize":"12px","fontWeight":600,
                 "letterSpacing":"0.4px","marginBottom":"6px"}

    return (
        kpis, tbl_label, tbl_rows,
        tbl_header_style, tbl_cell_style, tbl_conditional,
        fig_wow, fig_director, fig_triage, fig_priority, fig_severity,
        fig_category, fig_status, fig_assignee, fig_wdir, fig_release,
        # containers
        page_style, header_style, filter_style,
        brand_accent_style, brand_text_style, brand_sub_style,
        btn_label, btn_style,
        table_panel_style, tbl_title_style, tbl_count_style,
        # 10 panel styles
        *[dict(panel_style, flex=f) for f in [2.2, 1, 1.6, 1, 1, 1.4, 1, 1.2, 2, 1]],
        # 10 label styles
        *([lbl_style] * 10),
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
