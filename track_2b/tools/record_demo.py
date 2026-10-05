"""Record a captioned demo of the web UI: python tools/record_demo.py (app must be running on :8080)."""

from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8080/"
OUT = Path(__file__).resolve().parent.parent / "demo"
SAMPLE = (
    "Fallnotiz Sozialdienst\n\nKlient: Luca Bernasconi, AHV 756.1234.5678.97, Bärenmatte 4, 3011 Bern.\n"
    "Der Klient bezieht seit März wirtschaftliche Sozialhilfe. Er leidet an Epilepsie und ist Zeuge Jehovas. "
    "Kontakt: 079 555 12 34."
)
BEFORE = [
    ("A Swiss social worker wants an AI assistant to summarise this case note.", 4500),
    ("But Swiss data protection law (nDSG Art. 5) treats health, religion and welfare data as particularly sensitive.", 5500),
    ("Schild runs inside the office. Checksum rules catch AHV numbers, IBANs and phone numbers…", 4500),
    ("…and Apertus 1.5 8B, the Swiss open model, catches names, addresses and sensitive facts.", 5000),
    ("In this recording Apertus runs on the Swiss CSCS cloud; 'make local' runs the same model fully offline.", 5000),
]
AFTER = [
    ("Left: what Schild found. Right: the only text an external AI would ever see.", 6000),
    ("Placeholders are stable, and the real values come back into the AI's answer. They never leave the building.", 6000),
    ("Not perfect: here Apertus missed the welfare benefit ('wirtschaftliche Sozialhilfe'). We measure this openly.", 7000),
    ("Benchmark, 20 hard documents written for this test: rules alone protect 27% of personal data, Schild with Apertus 8B 82%.", 7000),
    ("If Apertus is unreachable, Schild refuses to forward anything: privacy fails closed.", 5000),
    ("Air-gapped with one command: make local. Schild, built on Apertus.", 5000),
]


def caption(page, text: str, ms: int) -> None:
    page.evaluate(
        """t => { let c = document.getElementById('cap');
                 if (!c) { c = document.createElement('div'); c.id = 'cap';
                   c.style.cssText = 'position:fixed;left:0;right:0;bottom:0;padding:18px 28px;'
                     + 'background:rgba(20,20,20,.9);color:#fff;font:600 22px/1.35 system-ui;z-index:9';
                   document.body.appendChild(c); }
                 c.textContent = t; }""",
        text,
    )
    page.wait_for_timeout(ms)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUT),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        page.goto(URL)
        page.fill("#input", "")
        caption(page, *BEFORE[0])
        page.type("#input", SAMPLE, delay=6)
        for text, ms in BEFORE[1:]:
            caption(page, text, ms)
        page.click("#go")
        page.wait_for_function("document.getElementById('status').textContent.includes('redacted')", timeout=120000)
        for text, ms in AFTER:
            caption(page, text, ms)
        video = page.video.path()
        context.close()
        browser.close()
    print("raw video:", video)


if __name__ == "__main__":
    main()
