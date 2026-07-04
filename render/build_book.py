#!/usr/bin/env python3
"""Build the online flipbook (output/book.html) from both transcripts.

The printed PDFs remain the job of render/build.py; this script produces the
web edition: a single self-contained HTML file with a real page-curl flip
(StPageFlip, vendored in render/vendor/), an EN/中文 toggle, and a PDF button.

Each spread becomes two facing pages: the prose on the left, the art on the
right, exactly like the printed book. Both languages are baked into the text
pages and toggled with CSS, so switching language never reloads the book.

Page geometry is the print geometry (5.5in x 6.1875in at 96dpi = 528x594 px),
and all type is set in container-query units, so text wraps identically to the
print edition at every zoom level. The fit check in build.py therefore governs
this edition too.

Art is served as resized JPEGs (render/book-assets/, built with macOS sips)
because the print PNGs total tens of megabytes.

Usage:
    python3 render/build_book.py            # build assets + output/book.html
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import EDITIONS, find_image, inline_md, parse_transcript  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RENDER_DIR = ROOT / "render"
ASSETS_DIR = RENDER_DIR / "book-assets"
VENDOR_JS = RENDER_DIR / "vendor" / "page-flip.browser.js"
BOOK_HTML = ROOT / "output" / "book.html"

JPEG_WIDTH = 1100  # px; roughly 2x the on-screen page width, keeps pages crisp

# ---------------------------------------------------------------- page assets
def build_assets(spread_ids: list[str]) -> None:
    """Resize each spread's print PNG into a web JPEG (skip if up to date)."""
    ASSETS_DIR.mkdir(exist_ok=True)
    for sid in spread_ids:
        src = find_image(sid)
        if src is None:
            sys.stderr.write(f"WARN: no art for spread {sid}; page will be blank.\n")
            continue
        dest = ASSETS_DIR / f"spread-{sid}.jpg"
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
             "--resampleWidth", str(JPEG_WIDTH), str(src), "--out", str(dest)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(f"sips failed for spread {sid}: {result.stderr}\n")
            raise SystemExit(1)
        print(f"  asset spread-{sid}.jpg")


# ------------------------------------------------------------------ html body
def prose_div(spread: dict, lang: str) -> str:
    paras = "".join(f"<p>{inline_md(p)}</p>" for p in spread["paras"])
    return f'<div class="prose lang-{lang}">{paras}</div>'


def pages_html(spreads_en: list[dict], spreads_cn: list[dict]) -> str:
    out: list[str] = []
    for en, cn in zip(spreads_en, spreads_cn):
        sid, stype = en["id"], en["type"]
        out.append(
            f'<div class="page {stype}" data-spread="{sid}">'
            f'<div class="pane text">{prose_div(en, "en")}{prose_div(cn, "cn")}</div>'
            "</div>"
        )
        art = ASSETS_DIR / f"spread-{sid}.jpg"
        img = (
            f'<img src="../render/book-assets/{art.name}" alt="" loading="lazy" decoding="async">'
            if art.exists() else ""
        )
        out.append(
            f'<div class="page {stype}" data-spread="{sid}">'
            f'<div class="pane art">{img}</div>'
            "</div>"
        )
    return "\n".join(out)


# The whole page design lives at 528x594 px (one page = half a print spread).
# Type and spacing use cqw so the page scales as one unit; 1cqw = 5.28px at
# design size, hence the odd-looking constants (18px body -> 3.4091cqw, etc.).
BOOK_CSS = """
:root {
  --paper: #fbf9f3;
  --ink: #3a3733;
  --ink-soft: #6f6a62;
  --accent: #b9542d;
  --stage-1: #2e2a25;
  --stage-2: #201d19;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; }
/* iOS Safari paints the area behind its collapsing URL bar with the ROOT
   background (white by default), and re-composites it mid-animation with the
   page's dark gradient: a white/dark flicker on every flip. A solid dark
   root background keeps that strip one color in every state. */
html { background: #201d19; }
body {
  font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  background: radial-gradient(120% 120% at 50% 20%, var(--stage-1), var(--stage-2));
  display: flex; flex-direction: column; align-items: center;
  overflow: hidden;
  height: 100dvh; /* the height:100% above is the pre-iOS-15.4 fallback */
  overscroll-behavior: none;
}

/* Language toggle: both languages are in the DOM; CSS shows one. */
html[data-lang="en"] .lang-cn { display: none; }
html[data-lang="cn"] .lang-en { display: none; }
html[data-lang="cn"] .prose {
  font-family: "Iowan Old Style", Palatino, "Songti SC", "STSong", Georgia, serif;
}

/* ---- Stage ---- */
.stage {
  flex: 1; width: 100%;
  display: flex; align-items: center; justify-content: center;
  padding: 3vh 3vw 1vh; /* 3vw each side leaves exactly 94vw for the book */
  min-height: 0;
}
/* Pre-JS placeholder only: sizeFrame() in BOOK_JS sets explicit pixel
   width/height before StPageFlip initializes (the library derives all its
   geometry from this box's measured width, so it must never depend on
   layout-time CSS resolution). */
.book-frame {
  width: min(94vw, calc((100dvh - 14vh) * 1.7778));
  aspect-ratio: 1056 / 594;
}
/* The browser must never claim a pan/zoom gesture over the book; the ID
   selector outranks the vendor's injected .stf__parent{touch-action:pan-y}. */
#book {
  touch-action: none;
  -webkit-user-select: none; user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* ---- Pages ---- */
.page {
  background: var(--paper);
  overflow: hidden;
  container-type: size;
}
.pane { width: 100%; height: 100%; }
.pane.text {
  display: flex; flex-direction: column; justify-content: center;
  /* print geometry: 0.35in top/bottom (the guaranteed margin), 0.85in outer,
     0.7in toward the gutter */
  padding: 6.364cqw 12.727cqw 6.364cqw 15.455cqw;
}
/* gutter shading so facing pages read as a bound book */
.pane.text::after, .pane.art::before {
  content: ""; position: absolute; top: 0; bottom: 0; width: 7cqw;
  pointer-events: none;
}
.pane.text::after {
  right: 0;
  background: linear-gradient(to left, rgba(58, 55, 51, 0.14), transparent);
}
.pane.art { position: relative; }
.pane.art::before {
  left: 0; z-index: 1;
  background: linear-gradient(to right, rgba(58, 55, 51, 0.18), transparent);
}
.pane.text { position: relative; }
.pane.art img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  -webkit-touch-callout: none; /* no iOS long-press image sheet mid-drag */
}

.prose { color: var(--ink); font-size: 3.409cqw; line-height: 1.5; }
.prose.lang-cn { font-size: 3.914cqw; }
.prose p { margin: 0 0 0.7em; }
.prose p:last-child { margin-bottom: 0; }
.prose strong { color: var(--accent); font-weight: 700; }
.prose em { font-style: italic; }

/* title spread */
.page.title .prose { font-size: 2.652cqw; }
.page.title .prose p:first-child {
  font-size: 7.576cqw; line-height: 1.1; color: var(--ink); margin-bottom: 0.25em;
}
.page.title .prose.lang-cn p:first-child { font-size: 6.307cqw; }
.page.title .prose p:nth-child(2) {
  font-size: 3.788cqw; color: var(--accent); font-style: italic; margin-bottom: 1.2em;
}
.page.title .prose p { color: var(--ink-soft); font-size: 2.273cqw; }

/* back cover */
.page.backcover .prose em {
  display: block; color: var(--ink-soft); font-style: normal;
  font-size: 2.898cqw; line-height: 1.3;
}

/* ---- Toolbar ---- */
.toolbar {
  display: flex; align-items: center; gap: 0.6rem;
  flex: none;
  padding: 0.55rem 0.9rem; margin: 0 0 2.2vh;
  background: rgba(251, 249, 243, 0.08);
  border: 1px solid rgba(251, 249, 243, 0.14);
  border-radius: 999px;
  backdrop-filter: blur(6px);
}
.toolbar button, .toolbar a {
  font: 600 0.85rem/1 "Helvetica Neue", Arial, sans-serif;
  color: #f4efe4; background: transparent;
  border: 1px solid rgba(251, 249, 243, 0.25); border-radius: 999px;
  height: 1.9rem; padding: 0;
  display: inline-flex; align-items: center; justify-content: center;
  cursor: pointer; text-decoration: none;
  touch-action: manipulation; /* no double-tap zoom on rapid Next taps */
  transition: background 150ms ease, border-color 150ms ease, transform 80ms ease;
}
/* Fixed widths, sized to the widest (Chinese) labels, so toggling the
   language never moves the buttons. All four arrows are inline SVGs (same
   stroke, flex-centered) because text glyphs come from different fonts and
   sit on the text baseline; the nav arrows are pinned to the button edges
   and only the label swaps with the language. */
.toolbar .icon { display: block; flex: none; }
.toolbar .nav { width: 6.2rem; justify-content: space-between; padding: 0 0.7rem; }
.toolbar .nav .lbl { flex: 1; text-align: center; }
.toolbar .jump { width: 2.9rem; }
.toolbar #btn-lang { width: 3.6rem; }
.toolbar a.pdf { width: 2.9rem; }
/* The PDF glyph's ink is measured dead-center, but its faint outlined top vs
   dense filled curl at the bottom makes it read low; lift it a hair. */
.toolbar a.pdf .icon { transform: translateY(-0.5px); }
/* Optical centering: Helvetica Neue's line box carries more descent than the
   glyphs use, so flex-centered TEXT sits a hair high next to the geometrically
   centered SVG icons. Padding-top shifts the text down by half its value;
   the icons are left untouched. */
.toolbar .nav .lbl, .toolbar #btn-lang, .toolbar .counter {
  padding-top: 0.15em;
}
/* hover-capable devices only, so tapped buttons don't stick orange on iOS */
@media (hover: hover) {
  .toolbar button:hover, .toolbar a:hover {
    background: rgba(185, 84, 45, 0.35); border-color: rgba(185, 84, 45, 0.7);
  }
}
.toolbar button:active, .toolbar a:active {
  transform: scale(0.92);
  background: rgba(185, 84, 45, 0.5); border-color: rgba(185, 84, 45, 0.9);
}
.toolbar button:disabled { opacity: 0.35; cursor: default; background: none; }
.toolbar .counter {
  font: 500 0.85rem/1 "Helvetica Neue", Arial, sans-serif;
  color: rgba(244, 239, 228, 0.75); min-width: 4.5rem; text-align: center;
}
/* Below this the full labeled bar (~560px) can't fit: drop the nav labels,
   tighten everything, fatten the tap targets; every control survives. */
@media (max-width: 620px) {
  .toolbar { gap: 0.25rem; padding: 0.45rem 0.5rem; }
  .toolbar .nav .lbl { display: none; }
  .toolbar .nav { width: 2.1rem; padding: 0; justify-content: center; }
  .toolbar .jump, .toolbar a.pdf { width: 2.1rem; }
  .toolbar #btn-lang { width: 2.5rem; font-size: 0.78rem; }
  .toolbar .counter { min-width: 2.75rem; font-size: 0.78rem; }
  .toolbar button, .toolbar a { height: 2.2rem; }
}
noscript { color: #f4efe4; font-size: 1rem; padding: 2rem; text-align: center; }
"""

BOOK_JS = """
const LABELS = {
  en: { prev: 'Prev', next: 'Next', lang: '\\u4e2d\\u6587',
        title: 'A Million Cars Come Home',
        counter: (n, total) => `${n} / ${total}` },
  cn: { prev: '\\u4e0a\\u4e00\\u9875', next: '\\u4e0b\\u4e00\\u9875',
        lang: 'EN',
        title: '\\u5f53\\u4e00\\u767e\\u4e07\\u8f86\\u8f66\\u540c\\u65f6\\u56de\\u5bb6',
        counter: (n, total) => `${n} / ${total}` },
};
const PDFS = { en: 'storybook.pdf', cn: 'storybook-cn.pdf' };

const params = new URLSearchParams(location.search);
let lang = params.get('lang') || localStorage.getItem('storybook-lang') || 'en';
if (!(lang in LABELS)) lang = 'en';

const el = (id) => document.getElementById(id);

function applyLang() {
  document.documentElement.dataset.lang = lang;
  document.title = LABELS[lang].title;
  el('prev-lbl').textContent = LABELS[lang].prev;
  el('next-lbl').textContent = LABELS[lang].next;
  el('btn-lang').textContent = LABELS[lang].lang;
  el('pdf-link').href = PDFS[lang];
  localStorage.setItem('storybook-lang', lang);
}
applyLang();

// Deep link: ?page=N opens the book at spread N.
const pageEls = document.querySelectorAll('.page');
const totalSpreads = pageEls.length / 2;
const startSpread = Math.min(
  Math.max(parseInt(params.get('page'), 10) || 1, 1), totalSpreads);

// Deterministic frame sizing. StPageFlip measures its container's width at
// init and derives everything (page size, height, hit areas) from it, so the
// container gets an explicit pixel size before init and on every viewport
// change; CSS-time formulas proved unreliable on phones. Portrait iff width
// < 480 mirrors the library's own rule (blockWidth < 2*minWidth); capping
// portrait width at 478 keeps the two decisions from ever disagreeing.
const stage = document.querySelector('.stage');
const frame = document.querySelector('.book-frame');

function sizeFrame() {
  const cs = getComputedStyle(stage);
  const availW = stage.clientWidth
    - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
  const availH = stage.clientHeight
    - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  // Same viewport caps as the old pure-CSS sizing (94vw wide, 86dvh/84dvh
  // tall), so the desktop book keeps its exact size; the stage clamp is the
  // safety net that keeps the toolbar visible on small screens.
  let w = Math.min(availW, Math.min(availH, window.innerHeight * 0.86) * (1056 / 594));
  const portrait = w < 480;
  if (portrait) {
    w = Math.min(availW, Math.min(availH, window.innerHeight * 0.84) * (528 / 594), 478);
  }
  w = Math.max(Math.floor(w), 240);
  frame.style.width = w + 'px';
  frame.style.height = Math.floor(portrait ? w * 594 / 528 : w * 594 / 1056) + 'px';
}
sizeFrame();

const pageFlip = new St.PageFlip(el('book'), {
  width: 528,
  height: 594,
  size: 'stretch',
  minWidth: 240,
  maxWidth: 1000,
  minHeight: 270,
  maxHeight: 1125,
  showCover: false,
  usePortrait: true,
  startPage: (startSpread - 1) * 2,
  maxShadowOpacity: 0.35,
  flippingTime: 500,
  mobileScrollSupport: false,
  // No corner fold-out preview when the cursor nears an edge, and the
  // library's own click-to-flip stays off (it maps clicks to the wrong book
  // region in portrait). Click navigation is reimplemented below on the frame:
  // left half = previous, right half = next.
  showPageCorners: false,
  disableFlipByClick: true,
});
pageFlip.loadFromHTML(pageEls);
window.book = pageFlip; // console/debug handle

function setCounter(pageIndex) {
  const spread = Math.floor(pageIndex / 2) + 1;
  el('counter').textContent = LABELS[lang].counter(spread, totalSpreads);
}
setCounter(pageFlip.getCurrentPageIndex());

// disableFlipByClick also gates the library's OWN synthetic flip points, and
// in portrait mode flipPrev()'s point {x:10} converts to mid-book coordinates
// and gets silently rejected (backward navigation dead on phones). Toolbar
// and keyboard navigation is deliberate, not a bare click, so lift the gate
// just for the duration of the call.
function nav(fn) {
  const s = pageFlip.getSettings();
  const saved = s.disableFlipByClick;
  s.disableFlipByClick = false;
  try { fn(); } finally { s.disableFlipByClick = saved; }
}
const goPrev = () => nav(() => pageFlip.flipPrev());
const goNext = () => nav(() => pageFlip.flipNext());
const goHome = () => nav(() => pageFlip.flip(0));
const goEnd = () => nav(() => pageFlip.flip((totalSpreads - 1) * 2));

pageFlip.on('flip', (e) => setCounter(e.data));
el('btn-home').addEventListener('click', goHome);
el('btn-prev').addEventListener('click', goPrev);
el('btn-next').addEventListener('click', goNext);
el('btn-end').addEventListener('click', goEnd);
el('btn-lang').addEventListener('click', () => {
  lang = lang === 'en' ? 'cn' : 'en';
  applyLang();
  setCounter(pageFlip.getCurrentPageIndex());
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') goPrev();
  if (e.key === 'ArrowRight') goNext();
  if (e.key === 'Home') goHome();
  if (e.key === 'End') goEnd();
});

// Click-to-flip, done by hand instead of the library's disableFlipByClick
// path (broken in portrait): click on the left half of the book goes back,
// right half goes forward. A press that turns into a drag-to-fold must not
// also flip on release, so track pointer travel and ignore anything that
// moved more than a click's worth.
let mouseDownX = null, mouseDownY = null;
frame.addEventListener('mousedown', (e) => {
  mouseDownX = e.clientX;
  mouseDownY = e.clientY;
});
frame.addEventListener('click', (e) => {
  if (mouseDownX === null) return;
  const moved = Math.hypot(e.clientX - mouseDownX, e.clientY - mouseDownY);
  mouseDownX = null;
  if (moved > 8) return; // was a drag, the library already handled it
  const rect = frame.getBoundingClientRect();
  if (e.clientX < rect.left + rect.width / 2) goPrev(); else goNext();
});

// In portrait mode the library's touch handling is broken the same way its
// flipPrev is: the single-page bounds rect is offset by a full page width, so
// touches map to the wrong book region (swipe-forward flips backward and
// swipe-back does nothing). Intercept touches before they reach the library
// (capture phase on the frame, its listener sits on a descendant) and run our
// own swipe detection. Landscape keeps the library's native drag-to-fold.
let touchStartX = null, touchStartY = null;
frame.addEventListener('touchstart', (e) => {
  if (pageFlip.getOrientation() !== 'portrait') return;
  e.stopPropagation();
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
}, { capture: true, passive: true });
frame.addEventListener('touchend', (e) => {
  if (pageFlip.getOrientation() !== 'portrait' || touchStartX === null) return;
  e.stopPropagation();
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  touchStartX = null;
  if (Math.abs(dx) < 50 || Math.abs(dx) < Math.abs(dy) * 1.5) return;
  if (dx < 0) goNext(); else goPrev();
}, { capture: true, passive: true });

// Phones never fire resize after load unless the frame follows the viewport:
// URL-bar collapse, rotation, and split-screen all land here. update()
// re-measures, switches portrait/landscape when needed, and re-shows the
// current page.
let resizeTimer = null;
function onViewportChange() {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { sizeFrame(); pageFlip.update(); }, 150);
}
window.addEventListener('resize', onViewportChange);
window.addEventListener('orientationchange', onViewportChange);
"""


# One arrow family for the whole toolbar: 16x16 viewBox, shared stroke.
def _icon(path: str) -> str:
    return (
        '<svg class="icon" viewBox="0 0 16 16" width="15" height="15" aria-hidden="true">'
        f'<path d="{path}" fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


ICON_LEFT = _icon("M14 8H3.5 M7.5 4 3.5 8l4 4")
ICON_RIGHT = _icon("M2 8h10.5 M8.5 4l4 4-4 4")
ICON_HOME = _icon("M2.5 3.5v9 M14 8H5 M8.5 4.5 5 8l3.5 3.5")
ICON_END = _icon("M13.5 3.5v9 M2 8h9 M7.5 4.5 11 8l-3.5 3.5")
# Bootstrap Icons "file-earmark-pdf" (MIT), filled: the recognizable Acrobat
# curl is a filled shape and cannot be drawn convincingly in the stroke style.
# Rendered at 13px: this glyph fills its viewBox edge to edge (the stroke
# icons keep inner padding), so at 15px it reads oversized and off-center.
ICON_PDF = (
    '<svg class="icon" viewBox="0 0 16 16" width="13" height="13" '
    'fill="currentColor" aria-hidden="true">'
    '<path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 '
    "2-2M9.5 3A1.5 1.5 0 0 0 11 4.5h2V14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 "
    '0 0 1 1-1h5.5z"/>'
    '<path d="M4.603 14.087a.8.8 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.'
    "198-.307.526-.568.897-.787a7.7 7.7 0 0 1 1.482-.645 20 20 0 0 0 "
    "1.062-2.227 7.3 7.3 0 0 1-.43-1.295c-.086-.4-.119-.796-.046-1.136.075-.354"
    ".274-.672.65-.823.192-.077.4-.12.602-.077a.7.7 0 0 1 .477.365c.088.164.12"
    ".356.127.538.007.188-.012.396-.047.614-.084.51-.27 1.134-.52 1.794a11 11 "
    "0 0 0 .98 1.686 5.8 5.8 0 0 1 1.334.05c.364.066.734.195.96.465.12.144.193"
    ".32.2.518.007.192-.047.382-.138.563a1.04 1.04 0 0 1-.354.416.86.86 0 0 1-"
    ".51.138c-.331-.014-.654-.196-.933-.417a5.7 5.7 0 0 1-.911-.95 11.7 11.7 0 "
    "0 0-1.997.406 11.3 11.3 0 0 1-1.02 1.51c-.292.35-.609.656-.927.787a.8.8 0 "
    "0 1-.58.029m1.379-1.901q-.25.115-.459.238c-.328.194-.541.383-.647.547-.094"
    ".145-.096.25-.04.361q.016.032.026.044l.035-.012c.137-.056.355-.235.635-"
    ".572a8 8 0 0 0 .45-.606m1.64-1.33a13 13 0 0 1 1.01-.193 12 12 0 0 1-.51-"
    ".858 21 21 0 0 1-.5 1.05zm2.446.45q.226.245.435.41c.24.19.407.253.498."
    "256a.1.1 0 0 0 .07-.015.3.3 0 0 0 .094-.125.44.44 0 0 0 .059-.2.1.1 0 0 "
    "0-.026-.063c-.052-.062-.2-.152-.518-.209a4 4 0 0 0-.612-.053zM8.078 7.8a7 "
    "7 0 0 0 .2-.828q.046-.282.038-.465a.6.6 0 0 0-.032-.198.5.5 0 0 0-.145.04c"
    '-.087.035-.158.106-.196.283-.04.192-.03.469.046.822q.036.167.09.346z"/>'
    "</svg>"
)


def build_book() -> str:
    editions = {}
    for lang in ("en", "cn"):
        text = EDITIONS[lang]["transcript"].read_text(encoding="utf-8")
        editions[lang] = parse_transcript(text)
    en, cn = editions["en"], editions["cn"]
    if [(s["id"], s["type"]) for s in en] != [(s["id"], s["type"]) for s in cn]:
        sys.stderr.write("Transcripts out of sync: spread ids/types differ.\n")
        raise SystemExit(1)

    build_assets([s["id"] for s in en])

    if not VENDOR_JS.exists():
        sys.stderr.write(
            f"Missing {VENDOR_JS}.\nDownload it once with:\n"
            "  curl -sL -o render/vendor/page-flip.browser.js "
            "https://unpkg.com/page-flip@2.0.7/dist/js/page-flip.browser.js\n"
        )
        raise SystemExit(1)
    vendor = VENDOR_JS.read_text(encoding="utf-8")

    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#201d19">
<title>A Million Cars Come Home</title>
<style>{BOOK_CSS}</style>
</head>
<body>
<div class="stage"><div class="book-frame"><div id="book">
{pages_html(en, cn)}
</div></div></div>
<div class="toolbar">
  <button id="btn-home" class="jump" type="button" aria-label="First spread">{ICON_HOME}</button>
  <button id="btn-prev" class="nav" type="button">{ICON_LEFT}<span class="lbl" id="prev-lbl"></span></button>
  <span class="counter" id="counter"></span>
  <button id="btn-next" class="nav" type="button"><span class="lbl" id="next-lbl"></span>{ICON_RIGHT}</button>
  <button id="btn-end" class="jump" type="button" aria-label="Last spread">{ICON_END}</button>
  <button id="btn-lang" type="button"></button>
  <a id="pdf-link" class="pdf" target="_blank" rel="noopener" aria-label="Download PDF" title="PDF">{ICON_PDF}</a>
</div>
<noscript>This book needs JavaScript. The PDF editions:
  <a href="storybook.pdf">English</a> / <a href="storybook-cn.pdf">中文</a>.
</noscript>
<script>{vendor}</script>
<script>{BOOK_JS}</script>
</body>
</html>
"""


def main() -> int:
    html = build_book()
    BOOK_HTML.parent.mkdir(exist_ok=True)
    BOOK_HTML.write_text(html, encoding="utf-8")
    print(f"Book -> {BOOK_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
