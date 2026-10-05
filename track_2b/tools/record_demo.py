"""Record a captioned, narrated demo of the web UI.

    python tools/record_demo.py                 # captions only
    python tools/record_demo.py --voice VOICE   # captions + Piper TTS narration (e.g. en_US-ljspeech-high.onnx)

The app must be running on :8080. Output: demo/schild-demo.mp4 (ffmpeg on PATH).
"""

import argparse
import subprocess
import time
import wave
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8080/"
OUT = Path(__file__).resolve().parent.parent / "demo"
SAMPLE = (
    "Fallnotiz Sozialdienst\n\nKlient: Luca Bernasconi, AHV 756.1234.5678.97, Bärenmatte 4, 3011 Bern.\n"
    "Der Klient bezieht seit März wirtschaftliche Sozialhilfe. Er leidet an Epilepsie und ist Zeuge Jehovas. "
    "Kontakt: 079 555 12 34."
)
# (caption shown on screen, text read aloud, minimum milliseconds on screen)
BEFORE = [
    ("A Swiss social worker wants an AI assistant to summarise this case note.",
     "A Swiss social worker wants an AI assistant to summarise this case note.", 4500),
    ("But Swiss data protection law (nDSG Art. 5) treats health, religion and welfare data as particularly sensitive.",
     "But Swiss data protection law treats health, religion and welfare data as particularly sensitive.", 5500),
    ("Schild runs inside the office. Checksum rules catch AHV numbers, IBANs and phone numbers…",
     "Schild runs inside the office. Checksum rules catch social security numbers, bank accounts and phone numbers.", 4500),
    ("…and Apertus 1.5 8B, the Swiss open model, catches names, addresses and sensitive facts.",
     "And Apertus, the Swiss open language model, catches names, addresses and sensitive facts.", 5000),
    ("In this recording Apertus runs on the Swiss CSCS cloud; 'make local' runs the same model fully offline.",
     "In this recording, Apertus runs on the Swiss national supercomputing cloud. One command runs the same model fully offline.", 5000),
]
AFTER = [
    ("Left: what Schild found. Right: the only text an external AI would ever see.",
     "On the left, what Schild found. On the right, the only text an external AI would ever see.", 6000),
    ("Placeholders are stable, and the real values come back into the AI's answer. They never leave the building.",
     "Placeholders are stable, and the real values come back into the answer. They never leave the building.", 6000),
    ("Not perfect: here Apertus missed the welfare benefit ('wirtschaftliche Sozialhilfe'). We measure this openly.",
     "It is not perfect. Here, Apertus missed the welfare benefit. We measure this openly.", 7000),
    ("Benchmark, 20 hard documents written for this test: rules alone protect 27% of personal data, Schild with Apertus 8B 82%.",
     "On twenty hard test documents, rules alone protect twenty seven percent of personal data. Schild with Apertus protects eighty two percent.", 7000),
    ("If Apertus is unreachable, Schild refuses to forward anything: privacy fails closed.",
     "If Apertus is unreachable, Schild refuses to forward anything. Privacy fails closed.", 5000),
    ("Air-gapped with one command: make local. Schild, built on Apertus.",
     "Air gapped with one command. Schild, built on Apertus.", 5000),
]
PAD_MS = 700


def synthesize(voice_path: Path, lines: list[tuple[str, str, int]], tag: str) -> list[tuple[str, Path, int]]:
    """Return (caption, wav, ms on screen) with the screen time stretched to fit the narration."""
    from piper import PiperVoice

    voice = PiperVoice.load(str(voice_path))
    out = []
    for i, (caption, spoken, min_ms) in enumerate(lines):
        wav = OUT / f"narration-{tag}-{i}.wav"
        with wave.open(str(wav), "wb") as w:
            voice.synthesize_wav(spoken, w)
        with wave.open(str(wav)) as w:
            audio_ms = int(1000 * w.getnframes() / w.getframerate())
        out.append((caption, wav, max(min_ms, audio_ms + PAD_MS)))
    return out


def caption(page, text: str) -> None:
    page.evaluate(
        """t => { let c = document.getElementById('cap');
                 if (!c) { c = document.createElement('div'); c.id = 'cap';
                   c.style.cssText = 'position:fixed;left:0;right:0;bottom:0;padding:18px 28px;'
                     + 'background:rgba(20,20,20,.9);color:#fff;font:600 22px/1.35 system-ui;z-index:9';
                   document.body.appendChild(c); }
                 c.textContent = t; }""",
        text,
    )


def record(before, after) -> tuple[Path, list[tuple[Path, float]]]:
    """Record the UI; return the raw video and (wav, start second) for each narrated caption."""
    cues: list[tuple[Path, float]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(OUT),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        t0 = time.monotonic()  # the recording starts with the page

        def show(text, wav, ms):
            caption(page, text)
            if wav is not None:
                cues.append((wav, time.monotonic() - t0))
            page.wait_for_timeout(ms)

        page.goto(URL)
        page.fill("#input", "")
        first_text, first_wav, first_ms = before[0]
        caption(page, first_text)
        if first_wav is not None:
            cues.append((first_wav, time.monotonic() - t0))
        started = time.monotonic()
        page.type("#input", SAMPLE, delay=6)
        page.wait_for_timeout(max(0, first_ms - int(1000 * (time.monotonic() - started))))
        for text, wav, ms in before[1:]:
            show(text, wav, ms)
        page.click("#go")
        page.wait_for_function("document.getElementById('status').textContent.includes('redacted')", timeout=120000)
        for text, wav, ms in after:
            show(text, wav, ms)
        video = Path(page.video.path())
        context.close()
        browser.close()
    return video, cues


def mux(video: Path, cues: list[tuple[Path, float]], out: Path) -> None:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video)]
    for wav, _ in cues:
        cmd += ["-i", str(wav)]
    if cues:
        delays = "".join(
            f"[{i + 1}:a]adelay={int(start * 1000)}|{int(start * 1000)}[a{i}];" for i, (_, start) in enumerate(cues)
        )
        mix = "".join(f"[a{i}]" for i in range(len(cues))) + f"amix=inputs={len(cues)}:normalize=0[aout]"
        cmd += ["-filter_complex", delays + mix, "-map", "0:v", "-map", "[aout]", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", type=Path, help="Piper .onnx voice for narration")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.voice:
        before = synthesize(args.voice, BEFORE, "before")
        after = synthesize(args.voice, AFTER, "after")
    else:
        before = [(c, None, ms) for c, _, ms in BEFORE]
        after = [(c, None, ms) for c, _, ms in AFTER]
    video, cues = record(before, after)
    out = OUT / ("schild-demo-narrated.mp4" if args.voice else "schild-demo.mp4")
    mux(video, cues, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
