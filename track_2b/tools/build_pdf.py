"""Render technical_report.md to PDF: python tools/build_pdf.py <TeamName>"""

import base64
import re
import sys
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

CSS = """
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.38; margin: 0; color: #1d1d1b; }
h1 { font-size: 17pt; margin: 0 0 6pt; } h2 { font-size: 12.5pt; margin: 13pt 0 4pt; } h3 { font-size: 10.5pt; margin: 10pt 0 3pt; }
p, ul, ol { margin: 4pt 0; } li { margin: 1pt 0; }
table { border-collapse: collapse; margin: 6pt 0; font-size: 9pt; }
td, th { border: 1px solid #bbb; padding: 2pt 5pt; vertical-align: top; } th { background: #f0f0ea; }
code { font-size: 8.5pt; background: #f4f4f0; padding: 0 2pt; }
img { max-width: 92%; display: block; margin: 6pt auto; }
"""


def report_html(root: Path) -> str:
    source = (root / "technical_report.md").read_text(encoding="utf-8")
    # Python-Markdown needs 4-space indents for nested lists; the report uses GitHub's 2 spaces.
    source = re.sub(r"(?m)^(  +)(?=[-*] |\d+\. )", lambda m: m.group(1) * 2, source)
    # Inline images: a page loaded with set_content cannot read local files.
    source = re.sub(
        r"!\[([^\]]*)\]\(([^)]+\.svg)\)",
        lambda m: f"![{m.group(1)}](data:image/svg+xml;base64,"
        + base64.b64encode((root / m.group(2)).read_bytes()).decode() + ")",
        source,
    )
    body = markdown.markdown(source, extensions=["tables", "fenced_code"])
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


def main() -> None:
    team = sys.argv[1]
    root = Path(__file__).resolve().parent.parent
    html = report_html(root)
    out = root / f"{team}_Report.pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.pdf(path=str(out), format="A4", margin={"top": "15mm", "bottom": "15mm", "left": "16mm", "right": "16mm"})
        browser.close()
    pages = len(PdfReader(str(out)).pages)
    print(f"{out.name}: {pages} pages")
    if pages > 6:
        sys.exit("Report is longer than 6 pages; shorten it.")


if __name__ == "__main__":
    main()
