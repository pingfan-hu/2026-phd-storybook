#!/usr/bin/env python3
"""Build composite 'cast sheet' reference images for multi-person scenes.

image_gemini.generate() accepts a single reference image, but group scenes (the team
meeting, the cafe chat, the gratitude scene) need several real faces matched at once.
This tiles the relevant portraits into one labeled sheet, left to right, which is then
passed as the single ref_image. The scene prompt names who is who and forbids inventing
strangers, so only people from characters/cartoon/ appear.

The sheets are derived artifacts and are NOT tracked in the repo: run this script
first whenever images/generate_scenes.py needs to regenerate a group scene (it
recreates characters/sheets/).

Run from the storybook root:
    python3 characters/build_sheets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHARS = ROOT / "characters"
CARTOON = CHARS / "cartoon"
SHEETS = CHARS / "sheets"

# sheet name -> ordered list of portrait slugs (left to right).
# Pingfan uses pingfan-ref.png (the cropped, approved likeness from spread-11) so every
# group shot carries the same face the user signed off on, not the older scarf portrait.
SHEETS_DEF: dict[str, list[str]] = {
    "pair-pf-john": ["pingfan-ref", "john-helveston"],
    "pair-pf-bogdan": ["pingfan-ref", "bogdan-bunea"],
    "team08": [
        "pingfan-ref", "john-helveston", "alan-jenn",
        "brian-tarroja", "eric-hittinger", "kate-forrest", "matthew-dean",
    ],
    "group23": [
        "pingfan-ref", "john-helveston", "eric-hittinger",
        "kate-forrest", "bogdan-bunea",
    ],
}

TILE = 384       # each face thumbnail is TILE x TILE
PAD = 16         # white gutter between tiles
BG = (255, 255, 255)


def build(name: str, slugs: list[str]) -> Path:
    tiles = []
    for slug in slugs:
        p = CARTOON / f"{slug}.png"
        if not p.exists():
            raise FileNotFoundError(p)
        img = Image.open(p).convert("RGB")
        # center-crop to square, then resize to TILE
        w, h = img.size
        side = min(w, h)
        left, top = (w - side) // 2, (h - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((TILE, TILE))
        tiles.append(img)

    n = len(tiles)
    sheet_w = n * TILE + (n + 1) * PAD
    sheet_h = TILE + 2 * PAD
    sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
    x = PAD
    for t in tiles:
        sheet.paste(t, (x, PAD))
        x += TILE + PAD
    SHEETS.mkdir(parents=True, exist_ok=True)
    out = SHEETS / f"{name}.png"
    sheet.save(out)
    return out


def main() -> None:
    for name, slugs in SHEETS_DEF.items():
        out = build(name, slugs)
        print(f"  OK   {out.relative_to(ROOT)}  ({len(slugs)} faces)")


if __name__ == "__main__":
    main()
