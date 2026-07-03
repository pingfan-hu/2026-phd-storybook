#!/usr/bin/env python3
"""Build the storybook PDF from the plain-text transcript.

Pipeline:  content/02-transcript.md  ->  render/storybook.html  ->  output/storybook.pdf

The transcript is the single source of truth. Each spread is parsed, rendered into a
self-contained HTML page (left prose pane + right illustration pane), and the whole thing
is printed to a landscape PDF with Chrome headless. No third-party Python packages needed.

Images are on hold: every spread shows a dashed placeholder card with its illustration
brief. When real art lands in images/spread-NN.png, it is used automatically.

Usage:
    python3 render/build.py            # build HTML + PDF
    python3 render/build.py --html     # build HTML only (skip PDF)

The online flipbook edition (render/book.html) is built separately by
render/build_book.py, which reuses this module's parser and geometry.

Override the browser with the CHROME env var if auto-detection fails.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"
RENDER_DIR = ROOT / "render"
CSS_FILE = RENDER_DIR / "styles.css"

# Two parallel editions share the same images and spread structure. The English
# transcript is the source of truth; the Chinese file mirrors it spread for spread.
EDITIONS = {
    "en": {
        "transcript": ROOT / "content" / "02-transcript.md",
        "html": RENDER_DIR / "storybook.html",
        "pdf": ROOT / "output" / "storybook.pdf",
        "title": "A Million Cars Come Home",
        "extra_css": "",
    },
    "cn": {
        "transcript": ROOT / "content" / "03-transcript-cn.md",
        "html": RENDER_DIR / "storybook-cn.html",
        "pdf": ROOT / "output" / "storybook-cn.pdf",
        "title": "当一百万辆车同时回家",
        # Latin glyphs keep the English edition's serif stack; CJK glyphs fall
        # back to Songti SC (matching the dissertation's CJK font choice).
        "extra_css": (
            'body, .prose, .prose p {\n'
            '  font-family: "Iowan Old Style", Palatino, "Songti SC", "STSong",\n'
            '    Georgia, serif;\n'
            "}\n"
            "/* Chinese runs shorter than English; larger type rebalances the page.\n"
            "   15.5pt is the largest size at which the densest spreads (05, 03, 07,\n"
            "   19) and the backcover still fit without pushing text out of the pane. */\n"
            ".prose { font-size: 15.5pt; line-height: 1.5; }\n"
            "/* the 10-character Chinese title needs one line at a smaller size */\n"
            ".spread.title .prose p:first-child { font-size: 25pt; }\n"
        ),
    },
}

SPREAD_HEADER = re.compile(r"^##\s+(\d+)\s*\|\s*(\w+)\s*$")


# --------------------------------------------------------------------------- parsing
def parse_transcript(text: str) -> list[dict]:
    """Split the transcript into a list of spread dicts: id, type, paras, brief."""
    lines = text.splitlines()
    spreads: list[dict] = []
    current: dict | None = None
    in_image = False
    image_lines: list[str] = []
    body_lines: list[str] = []

    def flush() -> None:
        if current is None:
            return
        current["paras"] = paragraphs(body_lines)
        current["brief"] = " ".join(l.strip() for l in image_lines if l.strip()).strip()
        spreads.append(current)

    for raw in lines:
        header = SPREAD_HEADER.match(raw.strip())
        if header:
            flush()
            current = {"id": header.group(1), "type": header.group(2).lower()}
            in_image = False
            image_lines = []
            body_lines = []
            continue
        if current is None:
            continue  # skip the book title and leading comments
        if raw.strip() == "::: image":
            in_image = True
            continue
        if raw.strip() == ":::":
            in_image = False
            continue
        if in_image:
            image_lines.append(raw)
        else:
            body_lines.append(raw)

    flush()
    return spreads


def paragraphs(lines: list[str]) -> list[str]:
    """Group non-blank lines into paragraphs, dropping HTML comments."""
    out: list[str] = []
    buf: list[str] = []
    for line in lines:
        if line.strip().startswith("<!--") or line.strip().startswith("-->"):
            continue
        if line.strip() == "":
            if buf:
                out.append(" ".join(buf).strip())
                buf = []
        else:
            buf.append(line.strip())
    if buf:
        out.append(" ".join(buf).strip())
    return [p for p in out if p]


def inline_md(text: str) -> str:
    """Escape HTML, then convert **bold** and *italic* to tags."""
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


# --------------------------------------------------------------------------- html
def find_image(spread_id: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = IMAGES_DIR / f"spread-{spread_id}{ext}"
        if candidate.exists():
            return candidate
    return None


def image_pane(spread: dict) -> str:
    art = find_image(spread["id"])
    if art is not None:
        rel = os.path.relpath(art, RENDER_DIR)
        return f'<div class="image-pane"><img class="art" src="{html.escape(rel)}" alt=""></div>'
    brief = inline_md(spread["brief"]) if spread["brief"] else "Illustration to come."
    return (
        '<div class="image-pane">'
        '<div class="placeholder">'
        '<div class="tag">Illustration</div>'
        f'<div class="brief">{brief}</div>'
        f'<div class="num">Spread {spread["id"]}</div>'
        "</div></div>"
    )


def render_spread(spread: dict) -> str:
    paras = "\n      ".join(f"<p>{inline_md(p)}</p>" for p in spread["paras"])
    return (
        f'  <section class="spread {spread["type"]}" data-id="{spread["id"]}">\n'
        f'    <div class="text-pane"><div class="prose">\n      {paras}\n    </div></div>\n'
        f"    {image_pane(spread)}\n"
        f"  </section>"
    )


def build_html(spreads: list[dict], lang: str) -> str:
    edition = EDITIONS[lang]
    css = CSS_FILE.read_text(encoding="utf-8") + "\n" + edition["extra_css"]
    body = "\n".join(render_spread(s) for s in spreads)
    html_lang = "zh-CN" if lang == "cn" else "en"
    return (
        f'<!doctype html>\n<html lang="{html_lang}">\n<head>\n'
        '<meta charset="utf-8">\n'
        f"<title>{edition['title']}</title>\n"
        f"<style>\n{css}\n</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


# --------------------------------------------------------------------------- fit check
# The prose pane centers its text vertically, so prose taller than the pane's
# content box silently eats the page margin (nothing clips it before the page
# edge). This probe renders the built HTML headless and reports any spread whose
# prose exceeds the content box, i.e. would shrink the guaranteed margin set by
# .text-pane's vertical padding in styles.css.
FIT_PROBE_JS = """
<script>
window.addEventListener('load', () => {
  const bad = [];
  document.querySelectorAll('.spread').forEach((s) => {
    const pane = s.querySelector('.text-pane');
    const prose = s.querySelector('.prose');
    const cs = getComputedStyle(pane);
    const avail = pane.clientHeight
      - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    if (prose.scrollHeight > avail) {
      bad.push(`spread ${s.dataset.id}: prose ${prose.scrollHeight}px > ` +
               `${Math.round(avail)}px available ` +
               `(over by ${Math.round(prose.scrollHeight - avail)}px)`);
    }
  });
  const pre = document.createElement('pre');
  pre.id = 'fit-report';
  pre.textContent = bad.join('\\n');
  document.body.appendChild(pre);
});
</script>
"""


def check_fit(chrome: str, html_out: Path) -> list[str] | None:
    """Return overflow warnings ([] = all spreads fit, None = probe failed)."""
    probe = html_out.with_name(html_out.stem + ".fitprobe.html")
    probe.write_text(
        html_out.read_text(encoding="utf-8").replace("</body>", FIT_PROBE_JS + "</body>"),
        encoding="utf-8",
    )
    try:
        result = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--virtual-time-budget=3000",
             "--dump-dom", probe.as_uri()],
            capture_output=True, text=True,
        )
    finally:
        probe.unlink()
    match = re.search(r'<pre id="fit-report">(.*?)</pre>', result.stdout, re.DOTALL)
    if result.returncode != 0 or match is None:
        return None
    report = html.unescape(match.group(1)).strip()
    return report.splitlines() if report else []


# --------------------------------------------------------------------------- pdf
def find_chrome() -> str | None:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            candidates.insert(0, found)
    for c in candidates:
        if c and Path(c).exists():
            return c
    return None


def render_pdf(chrome: str, html_out: Path, pdf_out: Path) -> bool:
    pdf_out.parent.mkdir(exist_ok=True)
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-margins",
        f"--print-to-pdf={pdf_out}",
        html_out.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not pdf_out.exists():
        sys.stderr.write(result.stdout + "\n" + result.stderr + "\n")
        return False
    return True


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Build the storybook from the transcript.")
    ap.add_argument("--html", action="store_true", help="build HTML only, skip the PDF")
    ap.add_argument("--lang", choices=sorted(EDITIONS), default="en",
                    help="edition to build: en (default) or cn")
    args = ap.parse_args()

    edition = EDITIONS[args.lang]
    transcript, html_out, pdf_out = edition["transcript"], edition["html"], edition["pdf"]

    if not transcript.exists():
        sys.stderr.write(f"Transcript not found: {transcript}\n")
        return 1

    spreads = parse_transcript(transcript.read_text(encoding="utf-8"))
    if not spreads:
        sys.stderr.write("No spreads parsed. Check the transcript format.\n")
        return 1

    html_out.write_text(build_html(spreads, args.lang), encoding="utf-8")
    with_art = sum(1 for s in spreads if find_image(s["id"]))
    print(f"Parsed {len(spreads)} spreads ({with_art} with art, "
          f"{len(spreads) - with_art} placeholders).")
    print(f"HTML -> {html_out.relative_to(ROOT)}")

    chrome = find_chrome()
    if chrome:
        warnings = check_fit(chrome, html_out)
        if warnings is None:
            sys.stderr.write("WARN: fit check failed to run; skipping it.\n")
        elif warnings:
            sys.stderr.write(
                "Text overflow: these spreads would eat into the page margin.\n"
                "Trim their prose (or adjust styles.css) and rebuild:\n"
            )
            for line in warnings:
                sys.stderr.write(f"  {line}\n")
            return 3
        else:
            print("Fit check: all spreads fit their text pane.")

    if args.html:
        return 0

    if not chrome:
        sys.stderr.write(
            "Chrome/Chromium not found. Open the HTML in a browser and Print to PDF, "
            "or set the CHROME env var to a browser binary.\n"
        )
        return 2
    if render_pdf(chrome, html_out, pdf_out):
        print(f"PDF  -> {pdf_out.relative_to(ROOT)}")
        return 0
    sys.stderr.write("PDF render failed.\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
