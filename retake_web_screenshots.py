"""
Retakes dark + light mode screenshots of the live Dash app.
Run AFTER dashboard.py is already serving on http://127.0.0.1:8050
"""
from playwright.sync_api import sync_playwright
import pathlib, time

HERE = pathlib.Path(__file__).parent
SHOTS = HERE / "screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto("http://127.0.0.1:8050")

    # Wait for KPI cards to load
    page.wait_for_function(
        "() => document.querySelectorAll('#kpi-row > div').length >= 6",
        timeout=15000
    )
    time.sleep(1.5)

    # Dark mode screenshot
    page.screenshot(path=str(SHOTS / "screenshot_dark.png"), full_page=False)
    print(f"  screenshot_dark.png  ({(SHOTS/'screenshot_dark.png').stat().st_size:,} bytes)")

    # Click theme toggle → light mode
    page.click("#theme-btn")
    time.sleep(1.2)
    page.screenshot(path=str(SHOTS / "screenshot_light.png"), full_page=False)
    print(f"  screenshot_light.png  ({(SHOTS/'screenshot_light.png').stat().st_size:,} bytes)")

    browser.close()

print("Done.")
