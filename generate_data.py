"""
App Defect Tracker — Dummy Data Generator
Generates ~200 realistic defect records spanning the last 26 weeks.
Run once: python generate_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

random.seed(42)
np.random.seed(42)

# ── Team Members ───────────────────────────────────────────────────────────────
TEAM_MEMBERS = [
    "Alex Chen", "Priya Sharma", "Marcus Johnson", "Aisha Patel",
    "David Kim", "Rania Hassan", "Tyler Brooks", "Mei Liu",
    "Carlos Rivera", "Fatima Al-Zahra", "Jake Thompson", "Yuki Tanaka",
    "Suman Dey", "Ivan Petrov", "Leila Nouri",
]

# ── App Taxonomy ──────────────────────────────────────────────────────────────
TRIAGE_CATEGORIES = [
    "Runtime",
    "Math Libraries",
    "Compiler",
    "App Monitoring",
    "App Installer",
    "ML Inference",
    "Communications",
    "Sparse Computing",
    "Signal Processing",
    "Documentation",
    "Performance / Profiling",
    "App Debugger",
    "Driver",
]

TRIAGE_ASSIGNMENTS = [
    "Driver Team",
    "Compiler Team",
    "Math Libraries Team",
    "Runtime Team",
    "Tools & Infra Team",
    "Documentation Team",
    "Release Engineering",
]

CATEGORY_TO_TEAM = {
    "Runtime":                "Runtime Team",
    "Math Libraries":         "Math Libraries Team",
    "Compiler":               "Compiler Team",
    "App Monitoring":         "Tools & Infra Team",
    "App Installer":          "Release Engineering",
    "ML Inference":           "Math Libraries Team",
    "Communications":         "Runtime Team",
    "Sparse Computing":       "Math Libraries Team",
    "Signal Processing":      "Math Libraries Team",
    "Documentation":          "Documentation Team",
    "Performance / Profiling":"Tools & Infra Team",
    "App Debugger":           "Tools & Infra Team",
    "Driver":                 "Driver Team",
}

# Director ownership
TEAM_TO_DIRECTOR = {
    "Driver Team":          "SAM",
    "Compiler Team":        "SAM",
    "Runtime Team":         "SAM",
    "Math Libraries Team":  "Kumar",
    "Tools & Infra Team":   "Philips",
    "Release Engineering":  "Suma",
    "Documentation Team":   "Ravi",
}

PRIORITIES       = ["Critical", "High", "Medium", "Low"]
PRIORITY_WEIGHTS = [8, 22, 45, 25]

SEVERITIES      = ["S1 - Blocker", "S2 - Critical", "S3 - Major", "S4 - Minor"]
PRIORITY_TO_SEV = {
    "Critical": ["S1 - Blocker", "S2 - Critical"],
    "High":     ["S2 - Critical", "S3 - Major"],
    "Medium":   ["S3 - Major",    "S4 - Minor"],
    "Low":      ["S4 - Minor"],
}

STATUSES       = ["Open", "In Progress", "In Review", "Resolved", "Closed", "Won't Fix"]
STATUS_WEIGHTS = [28, 22, 10, 22, 12, 6]

RESOLUTIONS = ["Fixed", "Won't Fix", "Duplicate", "Cannot Reproduce", "By Design"]

RELEASES = ["v6.2", "v6.3", "v6.4", "v7.0", "Backlog"]
FOUND_IN = ["v6.1", "v6.2", "v6.3"]

# ── Defect Title Templates ─────────────────────────────────────────────────────
TITLE_TEMPLATES = [
    "{cat}: Crash observed on multi-GPU node when calling {api}",
    "{cat}: Performance regression after upgrading to {rel}",
    "{cat}: Memory leak in {api} under stress workload",
    "{cat}: Build failure on Ubuntu 22.04 with {rel}",
    "{cat}: Incorrect result from {api} for large input tensors",
    "{cat}: API {api} not returning expected error code",
    "{cat}: Hang detected in multi-device {api} launch",
    "{cat}: Installer fails silently on RHEL 9.x",
    "{cat}: Documentation missing for {api} edge cases",
    "{cat}: Monitoring tool reports wrong device temperature",
    "{cat}: Debugger breakpoints not hitting in device code",
    "{cat}: AllReduce giving wrong result with 8 devices",
    "{cat}: FFT output is NaN for specific input dimensions",
    "{cat}: Kernel launch overhead increased by 2x in {rel}",
    "{cat}: Event timing reports negative duration",
]

APIS = [
    "allocMemory", "launchKernel", "matrixGemm", "inferenceConv",
    "allReduce", "signalPlan", "createGraph", "solveTrsm",
    "syncDevice", "sparseMv", "createStream",
]

# ── Date Range: last 26 weeks ─────────────────────────────────────────────────
END_DATE   = datetime(2026, 2, 28)
START_DATE = END_DATE - timedelta(weeks=26)


def random_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def build_title(cat: str) -> str:
    tmpl = random.choice(TITLE_TEMPLATES)
    api  = random.choice(APIS)
    rel  = random.choice(FOUND_IN)
    return tmpl.format(cat=cat.split("/")[0].strip(), api=api, rel=rel)


# ── Simulate realistic weekly spikes ─────────────────────────────────────────
def weighted_created_date() -> datetime:
    day_offset = int(np.random.choice(
        range(0, 182),
        p=np.clip(
            np.random.dirichlet(np.ones(182)) * 182,
            0, None
        ) / sum(np.clip(
            np.random.dirichlet(np.ones(182)) * 182,
            0, None
        ))
    ))
    return START_DATE + timedelta(days=day_offset)


records = []
for i in range(1, 221):
    created  = random_date(START_DATE, END_DATE)
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
    severity = random.choice(PRIORITY_TO_SEV[priority])
    status   = random.choices(STATUSES,   weights=STATUS_WEIGHTS)[0]
    category = random.choice(TRIAGE_CATEGORIES)
    team     = CATEGORY_TO_TEAM[category]

    days_elapsed = (END_DATE - created).days
    last_updated = created + timedelta(days=random.randint(0, max(1, days_elapsed)))

    open_statuses = {"Open", "In Progress", "In Review"}
    assignee   = random.choice(TEAM_MEMBERS) if status not in {"Open"} else ""
    resolution = "" if status in open_statuses else random.choice(RESOLUTIONS)

    records.append({
        "Defect_ID":         f"APP-{1000 + i}",
        "Title":             build_title(category),
        "Created_Date":      created.strftime("%Y-%m-%d"),
        "Created_By":        random.choice(TEAM_MEMBERS),
        "Priority":          priority,
        "Severity":          severity,
        "Status":            status,
        "Triage_Category":   category,
        "Triage_Assignment": team,
        "Director":          TEAM_TO_DIRECTOR[team],
        "Assignee":          assignee,
        "Component":         category.split("/")[0].strip().split("(")[0].strip(),
        "Target_Release":    random.choice(RELEASES),
        "Found_In_Release":  random.choice(FOUND_IN),
        "Last_Updated_Date": last_updated.strftime("%Y-%m-%d"),
        "Resolution":        resolution,
    })

df = pd.DataFrame(records)
df.to_csv("defects.csv", index=False)

print(f"Generated {len(df)} defect records -> defects.csv")
print(f"\nColumn list:\n  {', '.join(df.columns)}")
print(f"\nSample:\n{df.head(3).to_string()}")
