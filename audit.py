import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js"

def scan_website(url: str) -> dict:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.add_script_tag(url=AXE_CDN)
        results = page.evaluate("""async () => {
            return await axe.run(document, {
              runOnly: {
                type: "tag",
                values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
              }
            });
        }""")
        title = page.title()
        browser.close()

    violations = []
    for item in results["violations"]:
        violations.append({
            "id": item["id"],
            "impact": item.get("impact") or "unknown",
            "description": item["description"],
            "help": item["help"],
            "help_url": item["helpUrl"],
            "affected_elements": [
                {
                    "selector": node["target"],
                    "summary": node["failureSummary"]
                }
                for node in item["nodes"]
            ]
        })

    return {
        "url": url,
        "page_title": title,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "tool": "axe-core",
        "violations_count": len(violations),
        "violations": violations
    }

def write_html_report(report: dict, output: Path) -> None:
    cards = []
    for violation in report["violations"]:
        cards.append(
            "<article>"
            f"<h2>{violation['id']} — {violation['impact']}</h2>"
            f"<p>{violation['description']}</p>"
            f"<p><strong>How to fix:</strong> {violation['help']}</p>"
            f"<a href='{violation['help_url']}'>Guidance</a>"
            f"<p>Affected elements: {len(violation['affected_elements'])}</p>"
            "</article>"
        )
    content = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Accessibility Audit</title>
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;line-height:1.5}}
article{{border:1px solid #ccc;border-radius:8px;padding:16px;margin:16px 0}}
small{{color:#555}}
</style></head>
<body>
<h1>Web Accessibility Audit</h1>
<p><strong>URL:</strong> {report['url']}</p>
<p><strong>Page:</strong> {report['page_title']}</p>
<p><strong>Violations:</strong> {report['violations_count']}</p>
<p><small>Scanned at {report['scanned_at']} using axe-core.</small></p>
{''.join(cards) if cards else '<p>No violations were reported by the selected automated checks.</p>'}
<p><strong>Note:</strong> Automated checks do not prove full WCAG conformance. Manual testing is also required.</p>
</body></html>"""
    output.write_text(content, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Run an automated WCAG-focused accessibility scan.")
    parser.add_argument("url", help="Website URL, for example https://example.com")
    parser.add_argument("--output", default="reports", help="Output directory")
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        parser.error("URL must start with http:// or https://")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = scan_website(args.url)
    json_path = output_dir / "accessibility-report.json"
    html_path = output_dir / "accessibility-report.html"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_html_report(report, html_path)

    print(f"Scan completed. Violations found: {report['violations_count']}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")

if __name__ == "__main__":
    main()
