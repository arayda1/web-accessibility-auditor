# Web Accessibility Auditor

A command-line tool that scans a public web page with Playwright and axe-core, then creates JSON and HTML reports.

## What it checks
The scanner runs automated axe-core rules tagged for WCAG 2.0 A/AA and WCAG 2.1 A/AA. It reports issue IDs, impact, descriptions, help links, and affected selectors.

## Requirements
- Python 3.10+
- Internet connection for installing dependencies and loading axe-core
- Chromium browser installed through Playwright

## Setup on Windows PowerShell
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run a scan
```powershell
python audit.py https://example.com
```

Reports are written to the `reports` folder:
- `accessibility-report.json`
- `accessibility-report.html`

## Important limitations
Automated tools cannot detect every accessibility issue. Keyboard-only navigation, screen-reader behavior, meaningful alt text, logical focus order, captions, and user experience require manual evaluation. A clean automated report is not proof of full WCAG compliance.

## Tech stack
Python, Playwright, Chromium, axe-core, JSON, HTML, GitHub Actions.
