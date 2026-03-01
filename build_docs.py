"""Converts ROCm_Defect_Dashboard_Documentation.md -> .html with all images embedded."""
import re, base64, pathlib

HERE        = pathlib.Path(__file__).parent
SHOTS_DIR   = HERE / "screenshots"
DIAGRAMS_DIR= HERE / "diagrams"

def embed_img(path):
    p = pathlib.Path(path)
    if not p.exists():
        return ""
    data = base64.b64encode(p.read_bytes()).decode()
    ext  = p.suffix.lstrip(".").lower()
    mime = "svg+xml" if ext == "svg" else ext
    return f"data:image/{mime};base64,{data}"

# Web dashboard screenshots
dark_src  = embed_img(SHOTS_DIR / "screenshot_dark.png")
light_src = embed_img(SHOTS_DIR / "screenshot_light.png")

# Excel screenshots (filename → data URI)
XL_IMGS = {f: embed_img(SHOTS_DIR / f) for f in [
    "xl_dash_top.png", "xl_dash_ch1.png", "xl_dash_ch2.png",
    "xl_dash_ch3.png", "xl_dash_ch4.png", "xl_defects.png", "xl_summary.png",
]}

# Diagram images
ui_layout_src    = embed_img(DIAGRAMS_DIR / "ui_layout.png")
architecture_src = embed_img(DIAGRAMS_DIR / "architecture.png")

md = (HERE / "ROCm_Defect_Dashboard_Documentation.md").read_text(encoding="utf-8")

# ── minimal Markdown → HTML ─────────────────────────────────────────────────
def md2html(text):
    lines = text.split("\n")
    out = []
    in_table = in_code = in_ul = False
    is_header_row = True

    for line in lines:
        # fenced code
        if line.strip().startswith("```"):
            if not in_code:
                lang = line.strip()[3:].strip()
                out.append(f'<pre><code class="lang-{lang}">')
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            out.append(line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
            continue

        # image dispatch — match any ![alt](filename)
        m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if m:
            cap, fname = m.group(1), m.group(2).strip()
            src = ""
            if fname == "screenshot_dark.png":
                src = dark_src
            elif fname == "screenshot_light.png":
                src = light_src
            elif fname in XL_IMGS:
                src = XL_IMGS[fname]
            elif fname == "ui_layout.png":
                src = ui_layout_src
            elif fname == "architecture.png":
                src = architecture_src
            if src:
                out.append(f'<div class="ss"><img src="{src}" alt="{cap}"><p class="cap">{cap}</p></div>')
                continue

        # HR
        if line.strip() == "---":
            if in_ul: out.append("</ul>"); in_ul = False
            out.append("<hr>"); continue

        # table rows
        if line.strip().startswith("|") and "|" in line[1:]:
            if not in_table:
                if in_ul: out.append("</ul>"); in_ul = False
                out.append('<div class="tw"><table>')
                in_table = True
                is_header_row = True
            if re.match(r"^\|[\s\-:|]+\|", line):  # separator
                is_header_row = False
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            tag = "th" if is_header_row else "td"
            out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        else:
            if in_table:
                out.append("</table></div>"); in_table = False; is_header_row = True

        # headings
        hm = re.match(r"^(#{1,4})\s+(.*)", line)
        if hm:
            if in_ul: out.append("</ul>"); in_ul = False
            lvl = len(hm.group(1)); txt = hm.group(2)
            anch = re.sub(r"[^\w\s-]", "", txt.lower()).replace(" ", "-")
            out.append(f'<h{lvl} id="{anch}">{txt}</h{lvl}>'); continue

        # list item
        if re.match(r"^[-*]\s+", line):
            if not in_ul: out.append("<ul>"); in_ul = True
            item = inline(line.lstrip("-* ").strip())
            out.append(f"<li>{item}</li>"); continue
        elif in_ul and not line.strip():
            out.append("</ul>"); in_ul = False

        if not line.strip():
            out.append(""); continue

        out.append(f"<p>{inline(line)}</p>")

    if in_ul:    out.append("</ul>")
    if in_table: out.append("</table></div>")
    return "\n".join(out)

def inline(t):
    t = re.sub(r"`([^`]+)`",               r"<code>\1</code>",        t)
    t = re.sub(r"\*\*([^*]+)\*\*",         r"<strong>\1</strong>",     t)
    t = re.sub(r"\*([^*]+)\*",             r"<em>\1</em>",             t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>',     t)
    return t

body = md2html(md)

CSS = """
:root{--navy:#1B2631;--accent:#7c3aed;--bg:#f8f9fa;--card:#fff;--text:#1a202c;--sub:#4a5568;--bdr:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Inter,sans-serif;background:var(--bg);color:var(--text);line-height:1.7}
.page{max-width:1100px;margin:0 auto;padding:0 24px 60px}
.hero{background:var(--navy);color:#fff;padding:36px 40px;margin-bottom:36px;border-radius:0 0 12px 12px}
.hero h1{font-size:2rem;font-weight:800;margin-bottom:6px}
.hero p{color:#94a3b8;font-size:.95rem}
.badge{display:inline-block;background:var(--accent);color:#fff;border-radius:12px;padding:2px 10px;font-size:.8rem;font-weight:600;margin-right:8px}
.new-banner{background:#f0fff4;border:1px solid #c6f6d5;border-radius:8px;padding:14px 18px;margin:18px 0 28px}
.new-banner strong{color:#276749}
h1{font-size:1.9rem;font-weight:800;margin:36px 0 12px;color:var(--navy);border-bottom:3px solid var(--accent);padding-bottom:8px}
h2{font-size:1.4rem;font-weight:700;margin:28px 0 10px;color:#2d3748;border-left:4px solid var(--accent);padding-left:12px}
h3{font-size:1.1rem;font-weight:600;margin:20px 0 8px;color:#4a5568}
h4{font-size:1rem;font-weight:600;margin:16px 0 6px;color:#718096}
p{margin-bottom:12px;color:var(--sub)}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
strong{color:var(--text);font-weight:600}
em{color:var(--sub);font-style:italic}
code{background:#edf2f7;color:#c53030;padding:2px 6px;border-radius:4px;font-family:'Cascadia Code','Fira Code',monospace;font-size:.88em}
pre{background:#1e2535;color:#e2e8f0;border-radius:8px;padding:18px 20px;overflow-x:auto;margin:14px 0}
pre code{background:none;color:inherit;padding:0;font-size:.88rem}
.tw{overflow-x:auto;margin:14px 0 18px;border-radius:8px;border:1px solid var(--bdr)}
table{width:100%;border-collapse:collapse;font-size:.9rem}
th{background:var(--navy);color:#fff;padding:10px 14px;text-align:left;font-weight:600;font-size:.85rem}
td{padding:9px 14px;border-bottom:1px solid var(--bdr);vertical-align:top}
tr:last-child td{border-bottom:none}
tr:nth-child(even) td{background:#f7fafc}
ul{padding-left:22px;margin:10px 0 14px}
li{margin-bottom:5px;color:var(--sub)}
hr{border:none;border-top:1px solid var(--bdr);margin:32px 0}
.ss{margin:20px 0 28px;text-align:center}
.ss img{max-width:100%;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15)}
.cap{font-size:.83rem;color:#718096;margin-top:8px;font-style:italic}
"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>App Defect Dashboard — Documentation v1.1</title>
<style>{CSS}</style>
</head>
<body>
<div class="hero">
  <h1>App Defect Dashboard</h1>
  <p>
    <span class="badge">v1.1</span>
    <span class="badge">28 Feb 2026</span>
    Software Development &nbsp;|&nbsp; Defect Tracking &amp; Analytics
  </p>
</div>
<div class="page">
<div class="new-banner">
  <strong>New in v1.1:</strong> Dark / Light theme toggle — all charts, KPI cards, tables, and containers switch instantly with a 0.25 s CSS transition.
</div>
{body}
</div>
</body>
</html>"""

out = HERE / "ROCm_Defect_Dashboard_Documentation.html"
out.write_text(HTML, encoding="utf-8")
print(f"Written: {out}  ({len(HTML):,} bytes)")
