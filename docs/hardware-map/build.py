"""Print index.html to Infidex-Hardware-Map.pdf at the repo root.

Needs Python Playwright with Chromium (pip install playwright; playwright install chromium)
and the Inter font, which the page loads from Google Fonts.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "Infidex-Hardware-Map.pdf"

FOOTER = """
<div style="width:100%; text-align:center; font: 6pt Inter, sans-serif; color:#6b6b6b;">
  Infidex 176 V x IDENTIDEM.design Remix · page <span class="pageNumber"></span> of <span class="totalPages"></span>
</div>"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto((HERE / "index.html").as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(OUT), format="A4", print_background=True, prefer_css_page_size=True,
                 display_header_footer=True, header_template="<span></span>", footer_template=FOOTER)
        browser.close()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
