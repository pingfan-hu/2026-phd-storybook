#!/usr/bin/env python3
"""Composite cartoon versions of the real charts onto base scenes.

The base scenes (from generate_scenes.py) are generated with a clear, front-facing
surface left for a chart: a framed print on a wall, a monitor/tablet screen, or a
whiteboard. This pastes the matching cartoon chart asset (charts/cartoon/*.png, made
by charts/make_cartoon.py) onto that surface so the book shows the ACTUAL study
findings.

Surfaces are addressed in fractional coordinates (0..1 of the base canvas) so the code
is resolution independent. Three render styles:
  - frame:  wall print, white mat + thin dark frame + soft drop shadow
  - screen: monitor/tablet, dark bezel, chart nearly fills it
  - board:  whiteboard, chart pasted softly as if drawn, no frame

Run from the storybook root, after base scenes and cartoon charts exist:
    python3 images/integrate_charts.py            # all placements
    python3 images/integrate_charts.py 11 13 14   # only these spreads
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images"
BASE = OUT / "base"          # base scenes (chart surface left blank)
CARTOON = ROOT / "charts" / "cartoon"

FRAME_COLOR = (78, 66, 52)    # warm dark wood
MAT_COLOR = (250, 248, 242)   # cream mat
BEZEL_COLOR = (44, 44, 50)    # dark screen bezel
SHADOW = (40, 34, 28)


def _rounded(size: tuple[int, int], radius: int, fill) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill)
    return img


def _contain(chart: Image.Image, box: tuple[int, int]) -> Image.Image:
    cw, ch = chart.size
    bw, bh = box
    scale = min(bw / cw, bh / ch)
    return chart.resize((max(1, int(cw * scale)), max(1, int(ch * scale))))


def _place_rect(canvas: tuple[int, int], frac: tuple[float, float, float, float]):
    W, H = canvas
    fx, fy, fw, fh = frac
    return int(fx * W), int(fy * H), int(fw * W), int(fh * H)


def paste_frame(base: Image.Image, chart: Image.Image, frac) -> None:
    x, y, w, h = _place_rect(base.size, frac)
    # soft drop shadow
    shadow = _rounded((w, h), radius=int(0.03 * w), fill=SHADOW + (120,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(0.018 * w)))
    base.paste(shadow, (x + int(0.012 * w), y + int(0.018 * h)), shadow)
    # frame + mat
    frame = _rounded((w, h), radius=int(0.02 * w), fill=FRAME_COLOR)
    fb = int(0.045 * w)                      # frame border thickness
    mat = _rounded((w - 2 * fb, h - 2 * fb), radius=int(0.012 * w), fill=MAT_COLOR)
    frame.paste(mat, (fb, fb), mat)
    # chart inside the mat
    mb = int(0.05 * w)                       # mat border thickness
    inner = (w - 2 * fb - 2 * mb, h - 2 * fb - 2 * mb)
    c = _contain(chart.convert("RGBA"), inner)
    cx = fb + mb + (inner[0] - c.size[0]) // 2
    cy = fb + mb + (inner[1] - c.size[1]) // 2
    frame.paste(c, (cx, cy), c)
    base.paste(frame, (x, y), frame)


def paste_screen(base: Image.Image, chart: Image.Image, frac) -> None:
    x, y, w, h = _place_rect(base.size, frac)
    shadow = _rounded((w, h), radius=int(0.04 * w), fill=SHADOW + (110,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(int(0.02 * w)))
    base.paste(shadow, (x + int(0.01 * w), y + int(0.02 * h)), shadow)
    bezel = _rounded((w, h), radius=int(0.035 * w), fill=BEZEL_COLOR)
    bb = int(0.03 * w)
    screen_box = (w - 2 * bb, h - 2 * bb)
    panel = _rounded(screen_box, radius=int(0.02 * w), fill=MAT_COLOR)
    c = _contain(chart.convert("RGBA"), screen_box)
    panel.paste(c, ((screen_box[0] - c.size[0]) // 2, (screen_box[1] - c.size[1]) // 2), c)
    bezel.paste(panel, (bb, bb), panel)
    base.paste(bezel, (x, y), bezel)


def paste_board(base: Image.Image, chart: Image.Image, frac) -> None:
    x, y, w, h = _place_rect(base.size, frac)
    c = _contain(chart.convert("RGBA"), (w, h))
    # soften: drop pure-white so it reads as drawn on the board
    c = c.copy()
    if c.mode == "RGBA":
        alpha = c.split()[3].point(lambda a: int(a * 0.95))
        c.putalpha(alpha)
    cx = x + (w - c.size[0]) // 2
    cy = y + (h - c.size[1]) // 2
    base.paste(c, (cx, cy), c)


CARD_BG = (252, 251, 248)     # near-white print stock
CARD_EDGE = (120, 110, 96)    # faint warm border


def paste_card(base: Image.Image, chart: Image.Image, frac) -> None:
    """Drop a chart as a clean white-backed print into an EXISTING blank surface.

    The base scene already drew the wood frame / screen bezel / whiteboard, so this
    adds no frame of its own: it backs the chart on a small white card (so axis
    labels read against any mat color), adds a faint border and soft shadow, and
    sits it inside the given inner rectangle.
    """
    x, y, w, h = _place_rect(base.size, frac)
    pad = max(2, int(0.04 * min(w, h)))
    inner = (w - 2 * pad, h - 2 * pad)
    c = _contain(chart.convert("RGBA"), inner)
    cw, ch = c.size
    card_w, card_h = cw + 2 * pad, ch + 2 * pad
    card = Image.new("RGBA", (card_w, card_h), CARD_BG + (255,))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, card_w - 1, card_h - 1], outline=CARD_EDGE + (160,), width=1)
    card.paste(c, (pad, pad), c)
    cx = x + (w - card_w) // 2
    cy = y + (h - card_h) // 2
    # faint contact shadow so the print sits on the surface
    shadow = Image.new("RGBA", (card_w, card_h), SHADOW + (90,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, int(0.02 * card_w))))
    base.paste(shadow, (cx + int(0.01 * card_w), cy + int(0.015 * card_h)), shadow)
    base.paste(card, (cx, cy), card)


STYLES = {"frame": paste_frame, "screen": paste_screen, "board": paste_board, "card": paste_card}

# spread id -> list of (chart-key, style, (x, y, w, h) fractional)
# NOTE: rects are first-pass guesses; tuned after inspecting base scenes.
PLACEMENTS: dict[str, list[tuple[str, str, tuple[float, float, float, float]]]] = {
    "07": [("choice", "card", (0.10, 0.48, 0.29, 0.28))],
    "08": [("caiso", "card", (0.79, 0.14, 0.13, 0.15))],
    "11": [("caiso", "card", (0.21, 0.13, 0.23, 0.22)),
           ("cost", "card", (0.51, 0.13, 0.26, 0.22))],
    "12": [("enroll", "card", (0.42, 0.55, 0.31, 0.18))],
    "13": [("caiso", "card", (0.53, 0.17, 0.32, 0.19))],
    "14": [("cost", "board", (0.12, 0.21, 0.33, 0.30))],
    "18": [("survey", "card", (0.37, 0.11, 0.23, 0.22))],
    "19": [("howitworks", "card", (0.33, 0.31, 0.50, 0.29))],
    "21": [("owners", "card", (0.23, 0.25, 0.19, 0.20)),
           ("caiso", "card", (0.47, 0.25, 0.19, 0.20)),
           ("survey", "card", (0.71, 0.25, 0.19, 0.20))],
}


def run(ids: list[str]) -> int:
    failures = []
    for sid in ids:
        if sid not in PLACEMENTS:
            print(f"  SKIP {sid}: no placement")
            continue
        base_path = BASE / f"spread-{sid}.png"
        if not base_path.exists():
            print(f"  FAIL {sid}: missing base {base_path}")
            failures.append(sid)
            continue
        base = Image.open(base_path).convert("RGBA")
        ok = True
        for key, style, frac in PLACEMENTS[sid]:
            chart_path = CARTOON / f"{key}.png"
            if not chart_path.exists():
                print(f"  FAIL {sid}: missing chart cartoon/{key}.png")
                ok = False
                break
            chart = Image.open(chart_path)
            STYLES[style](base, chart, frac)
        if not ok:
            failures.append(sid)
            continue
        out = OUT / f"spread-{sid}.png"
        base.convert("RGB").save(out)
        print(f"  OK   spread-{sid}.png  ({len(PLACEMENTS[sid])} chart(s))")
    print(f"\nDone. {len(ids) - len(failures)}/{len(ids)} succeeded.")
    if failures:
        print("Failed:", ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    requested = sys.argv[1:] or list(PLACEMENTS.keys())
    raise SystemExit(run(requested))
