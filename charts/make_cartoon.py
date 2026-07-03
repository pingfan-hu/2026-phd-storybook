#!/usr/bin/env python3
"""Produce cartoon versions of the real study figures (charts/original/).

Each output keeps the REAL chart's exact shape, structure, and a few key labels,
but is recolored into the storybook's warm Ghibli palette (cream, sage green, soft
terracotta, sky blue), with dense tick text and busy gridlines stripped away so it
blends with the painterly art. These cartoon assets (charts/cartoon/) are then
composited onto real surfaces (framed prints, monitors, a tablet, a whiteboard)
inside the scenes by images/integrate_charts.py, so the book shows the ACTUAL
findings, not invented charts.

Run from the storybook root:
    python3 charts/make_cartoon.py            # all
    python3 charts/make_cartoon.py caiso cost # only these keys
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL = Path.home() / ".claude/skills/ph-image"
sys.path.insert(0, str(SKILL))
from image_gemini import generate  # noqa: E402

CHARTS = Path(__file__).resolve().parent
ORIGINAL = CHARTS / "original"
CARTOON = CHARTS / "cartoon"

PALETTE = (
    "Recolor everything into a warm, soft Studio Ghibli storybook palette: a plain "
    "cream off-white background (no grey, no pure white panel), gentle hand-painted "
    "watercolor and gouache textures, soft clean linework. Use deep slate blue, sage "
    "green, soft terracotta, and muted sky blue for the data lines and shapes. Thin, "
    "calm axis lines only. Remove the chart title, remove busy gridlines, remove dense "
    "numeric tick labels and remove any source caption. Keep ONLY a few essential, "
    "tidy labels as specified. Keep the shapes, curves, proportions and positions "
    "EXACTLY as in the reference so the data still reads true. Cohesive, uncluttered, "
    "friendly. No drop shadow, no outer frame, fill the canvas edge to edge."
)

# key -> (source filename in charts/original/, aspect, what-to-keep prompt)
CARTOONS: dict[str, tuple[str, str, str]] = {
    "caiso": (
        "study2-caiso-peak-shaving.png", "16:9",
        "A daily electricity load curve over 24 hours shaped like a mountain. Keep the "
        "two lines exactly: a darker slate-blue line for the original load with a tall "
        "evening peak, and a sage-green line that sits below it at the evening peak "
        "(shaving it) and rises a little above it overnight after midnight (the small "
        "new overnight bump). Keep the softly shaded net-load area beneath in a pale "
        "tone. Keep a small two-row legend swatch (dark = before, green = with smart "
        "charging) with very short text, and a simple horizontal time axis feel. "
        "Nothing else.",
    ),
    "cost": (
        "study2-cost-efficiency.png", "1:1",
        "Three upward-curving cost curves rising from a flat bottom-left then climbing "
        "steeply, showing sharply rising cost as participation grows. Recolor the three "
        "curves to soft terracotta, sage green, and sky blue. Keep the small rounded "
        "marker labels reading 30%, 50%, and 100% along the curves, but drop all other "
        "numbers and axis text. Plain vertical and horizontal axis lines only.",
    ),
    "enroll": (
        "study2-enrollment-vs-incentive.png", "16:9",
        "A single concave enrollment curve that rises steeply from about a third at the "
        "left, bends over, and levels off near the top right approaching full "
        "participation, with a faint soft confidence band around it. Recolor the line "
        "to deep slate blue and the band to a pale tone. Keep just four short axis "
        "ticks suggesting 0%, 50%, 100% on the upright axis and a dollar sign feel on "
        "the bottom axis. Nothing else.",
    ),
    "choice": (
        "study1-choice-question.png", "16:9",
        "A clean survey choice-question card with three columns labeled Option 1, "
        "Option 2, and Not Interested. Keep the short attribute rows (Enrollment Cash, "
        "Monthly Cash, Override Allowance) with their small dollar values, and keep the "
        "two horizontal Battery Threshold bars made of grey, terracotta, and green "
        "segments with small Min and Guaranteed markers. This is a readable survey "
        "screen, so keep these labels legible but tidy; just soften the colors and "
        "remove the top question text and the Access button.",
    ),
    "survey": (
        "study3-survey-example.png", "4:5",
        "A clean, friendly rendered web-survey page: a short welcome heading line, one "
        "multiple-choice question with three or four radio-button options, and a single "
        "rounded Next button at the bottom. Keep it readable as a real survey UI, just "
        "recolor to the warm palette and simplify. Minimal placeholder text.",
    ),
    "howitworks": (
        "study3-how-it-works.png", "4:3",
        "A simple left-to-right logic-flow diagram with three or four rounded nodes "
        "joined by arrows: a plain-text document node, then a render/build step, then a "
        "live web-survey screen node, then a database-cylinder node for stored "
        "responses. Keep tiny tidy icon-like labels only. Clean and uncluttered.",
    ),
}


def run(keys: list[str]) -> int:
    CARTOON.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for key in keys:
        if key not in CARTOONS:
            print(f"  SKIP {key}: unknown")
            continue
        src, aspect, keep = CARTOONS[key]
        ref = ORIGINAL / src
        if not ref.exists():
            print(f"  FAIL {key}: missing {src}")
            failures.append(key)
            continue
        out = CARTOON / f"{key}.png"
        prompt = keep + " " + PALETTE
        print(f"  cartooning {key} <- {src} ...", flush=True)
        try:
            generate(prompt, out, ref_image=ref, aspect=aspect)
            print(f"  OK   cartoon/{key}.png")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {key}: {exc}")
            failures.append(key)
    print(f"\nDone. {len(keys) - len(failures)}/{len(keys)} succeeded.")
    if failures:
        print("Failed:", ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    requested = sys.argv[1:] or list(CARTOONS.keys())
    raise SystemExit(run(requested))
